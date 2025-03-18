from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import time
import json
import re
import datetime
import zoneinfo
import html
from bs4 import BeautifulSoup
import tabulate

from plugins.base.common.base import get_hero_id
import plugins.base.common.sqlstatement as sql
import plugins.base.base.driver as driver
import plugins.base.base.pqsldb as db

layer_reports = {}

def get_list(group, count):
    hero_id = get_hero_id(str(group))
    url = f'http://delta.world-of-dungeons.org/wod/spiel/dungeon/report.php?session_hero_id={hero_id}'
    d = driver.WodDriver.get_instance()
    resp = d.open_get_page(url)
    if resp:
    # 加载5个战报, tr[1] 是头
        soup = BeautifulSoup(resp, 'html.parser')
        table = soup.find('table', class_='content_table')
        if not table:
            return False, f'没有战报啊, 超时? '

        report_entries = []
        num = 0 # 输出每个地城及其对应的 value
        for row in table.find_all('tr')[1:]:  # Skip the header row
            if num >= count:
                break
            num+=1
            cols = row.find_all('td')
            date = cols[0].get_text(strip=True)
            dungeon = cols[1].get_text(strip=True)
            # Find the hidden input to get the value
            hidden_input = cols[2].find('input', type='hidden')
            value = hidden_input['value'] if hidden_input else None
            report_entries.append({'ID': value, 'date': date, 'dungeon': dungeon})
        ret_str = tabulate.tabulate(report_entries, tablefmt="github", showindex="always")
        return True, f'{"上个地城" if count == 1 else f"前{count}战报"}\n{ret_str}\n'
    else:
        return False, f'打开战报界面失败'

def __find_report(group, report_id):
    print(f'find 战报 {group}, {report_id} 1')
    hero_id = get_hero_id(str(group))
    url = f'http://delta.world-of-dungeons.org/wod/spiel/dungeon/report.php?session_hero_id={hero_id}'
    d = driver.WodDriver.get_instance()
    resp = d.open_get_page(url)
    if resp:        # 加载战报, tr[1] 是头 d.wait('//*[@id="main_content"]/div/form/table/tbody/tr[1]/td[1]/span'):
        print(f'find 战报 {group}, {report_id} 2')
        soup = BeautifulSoup(resp, 'html.parser')
        table = soup.find('table', class_='content_table')
        if not table:
            return False, f'没有战报列表啊, 超时? '

        print(f'find 战报 {group}, {report_id} 3')
        value = date = dungeon = None
        # 输出每个地城及其对应的 value
        for num, row in enumerate(table.find_all('tr')[1:], start=1):  # Skip the header row
            cols = row.find_all('td')
            # Find the hidden input to get the value
            hidden_input = cols[2].find('input', type='hidden')
            value = hidden_input['value'] if hidden_input else None #id
            date = cols[0].get_text(strip=True)
            dungeon = cols[1].get_text(strip=True)
            if report_id is None or (value and value == report_id):
                break
        else:
            return False, f'没有找到{report_id}, 查询了 {num} 个战报'
        print(f'find report {report_id}, num is {num}, name {dungeon}, time {date}')
        return True, f'找到{report_id}, 查询了 {num} 个战报', num, value, dungeon, date
    else:
        return False, f'打开战报界面失败'

def __pares_db_pass(report_id):
    records = db.Pdb.get_instance().exec_all(sql.select_battle_report, (report_id,)) # execute 就会开启事务, 要不用with 之类自动提交, 要不手动提交
    db.Pdb.get_instance().commit()
    if records:
        print(f"记录存在，report_id = {report_id}")
        for record in records:
            print(record)  # 打印出记录内容
            # 处理数据
            dungeon = record[1]
            id = record[0]
            dungeon_time = record[2]
            max_layer = int(record[3])
            players = re.findall(r'\((.*?)\)', record[4])
            fight_count = total_fight_count = 0
            die_players = {}
            for player in players:
                player = player.split(',')
                name = player[1]
                layer = int(player[2])
                fight_count += layer
                total_fight_count += max_layer
                if layer != max_layer:
                    die_players[name] = layer + 1
                print(f'{name}, {layer} / {max_layer}, this {fight_count}, totoal {total_fight_count}, len {len(die_players)}')

            # 计算完成率
            completion_rate = fight_count / total_fight_count if total_fight_count != 0 else 0
            # # 使用格式化字符串输出基本信息
            output = f'{id} {dungeon} {dungeon_time} 完城率 {completion_rate:.2%}'  # 保留两位小数并格式化为百分比
            # 添加死于敌人的信息
            if die_players:
                output += "\n" + "\n".join([f"{key}: 止步 {value}f / {max_layer}f" for key, value in die_players.items()]) + "\n"
        return True, output
    return False, ""

# 换为psql tz时间戳
def __wod_time_to_tstz(wod_time : str):
    times = wod_time.split()
    if len(times) != 2:
        return None, f'无法解析时间{wod_time}'
    time_base = None
    tz = zoneinfo.ZoneInfo('Asia/Shanghai')
    if times[0] == '今天':
        time_base = datetime.date.today()
    elif times[0] == '昨天':
        time_base = datetime.date.today() - datetime.timedelta(days=1)
    else:
        return datetime.datetime.strptime(wod_time, "%Y年%m月%d日 %H:%M").replace(tzinfo=tz).isoformat(), ""
    
    hhmm = times[1].split(':')
    return datetime.datetime(time_base.year, time_base.month, time_base.day, int(hhmm[0]), int(hhmm[1]), 0).replace(tzinfo=tz).isoformat(), ""

def _parse_pass(group, report_id):
    print(f'解析战报 {group}, {report_id}')
    #  先去找id, 再去db找, db 没有就读
    if report_id is not None:
        ret, ret_str = __pares_db_pass(report_id)
        if ret:
            return True, ret_str

    ret = None
    ret_str = ""
    have_report, have_report_str, num, id, dungeon, dungeon_time = __find_report(group, report_id)
    if id is not None: # 赋值是因为支持了report_id 为空
        ret, ret_str = __pares_db_pass(id)
    elif report_id is not None:
        ret, ret_str = __pares_db_pass(report_id)
    else:
        return False, f'找不到最近战报, 也没传入战报id'
    if ret:
        return True, ret_str

    if not have_report:
        print(have_report_str)
        return False, have_report_str

    print(f'解析战报 {group}, {report_id} 1')
    d = driver.WodDriver.get_instance()
    #//*[@id="main_content"]/div/form/table/tbody/tr[2]/td[3]/input[2]              tr[x+1] 是第x个战报 td[3] 统计表的外框  input1,2,3,4: 隐藏的id, 统计表, 物品, 资料
    #<input type="submit" name="stats[0]" value="统计表" class="button clickable">
    submit_button = d.find_xpath(f'//*[@id="main_content"]/div/form/table/tbody/tr[{num+1}]/td[3]/input[2]') # 加1因为1是表头, 战报从2开始的
    if submit_button is None:
        return False, f'找到战报{report_id}, 缺找不到他的统计表?'
    
    submit_button.click()

    print(f'解析战报 {group}, {report_id} 2')
    #统计表的 
    # 名字
    # //*[@id="main_content"]/div/form/table/tbody/tr/td/table/tbody/tr[1]/th[2]/a  tr[x+1] 是数列的第x个元素, th[x+1]是第x个玩家
    # <a href="../hero/profile.php?id=0" onclick="return wo('../hero/profile.php?id=0);"></a>
    # //*[@id="main_content"]/div/form/table/tbody/tr/td/table/tbody/tr[1]/th[3]/a
    # 战斗层数
    # //*[@id="main_content"]/div/form/table/tbody/tr/td/table/tbody/tr[6]/td[2]/span  tr[6]是战斗  td[x+1] 是第x个玩家
    # //*[@id="main_content"]/div/form/table/tbody/tr/td/table/tbody/tr[6]/td[3]/span
    # <span class="rep_emphasized">7/7</span>
    d.wait(f'//*[@id="main_content"]/div/form/table/tbody/tr/td/table/tbody/tr[6]/td[11]/span') # 读第10个元素作为加载成功
    
    fight_count = 0
    total_fight_count = 0
    max_layer = 0
    die_players = {}
    players = []
    timestamp = datetime.datetime.now(zoneinfo.ZoneInfo(key='Asia/Shanghai'))
    dbi = db.Pdb.get_instance()
    dbi.exec_no_fetch('begin')
    for player in range(1,13):
        name = d.find_xpath(f'//*[@id="main_content"]/div/form/table/tbody/tr/td/table/tbody/tr[1]/th[{player+1}]/a')
        fight_info = d.find_xpath(f'//*[@id="main_content"]/div/form/table/tbody/tr/td/table/tbody/tr[5]/td[{player+1}]/span')
        if name is None:
            break
        if fight_info is None:
            fight_info = d.find_xpath(f'//*[@id="main_content"]/div/form/table/tbody/tr/td/table/tbody/tr[5]/td[{player+1}]')
        href = name.get_attribute('href')
        name = name.text
        fight_info = fight_info.text.split('/')
        fight_count += int(fight_info[0])
        total_fight_count += int(fight_info[1])
        max_layer = int(fight_info[1])
        if fight_info[0] != fight_info[1]:
            die_players[name] = int(fight_info[0]) + 1
        print(f'{name}, {fight_info[0]} / {fight_info[1]}, this {fight_count}, totoal {total_fight_count}, len {len(die_players)}')
        players.append( (href.split('=')[-1], name, int(fight_info[0])) )

    print(f'解析战报 {group}, {report_id} 3')
    # 计算完成率
    completion_rate = fight_count / total_fight_count if total_fight_count != 0 else 0
    # # 使用格式化字符串输出基本信息
    output = f'{id} {dungeon} {dungeon_time} 完城率 {completion_rate:.2%}'  # 保留两位小数并格式化为百分比
    # 添加死于敌人的信息
    if die_players:
        output += "\n" + "\n".join([f"{key}: 止步 {value}f / {max_layer}f" for key, value in die_players.items()]) + "\n"

    dungeon_time_tz, time_str = __wod_time_to_tstz(dungeon_time)
    if dungeon_time_tz is None:
        return False, time_str 
    dbi.exec_no_fetch(sql.insert_battle_report, (id, timestamp, dungeon, dungeon_time_tz, max_layer, players,))
    dbi.exec_no_fetch('commit')
    return True, output
    # return True, f'{id} {dungeon} {dungeon_time} 完城率 {completion_rate:.2%}\n{"{}".format("\n".join([f"{key}:死于 {value}" for key, value in die_players.items()])) if die_players else f""}'

def __parse_buff(group, report_id):
    print(f'解析buff {group}, {report_id}')
    have_report, have_report_str, num, id, dungeon, dungeon_time = __find_report(group, report_id)
    if id is None:
        print(have_report_str)
        return False, have_report_str

    dbi = db.Pdb.get_instance()
    records = dbi.exec_all(sql.select_battle_report, (id,)) # execute 就会开启事务, 要不用with 之类自动提交, 要不手动提交
    dbi.commit()
    d = driver.WodDriver.get_instance()
    if not records:
        _parse_pass(group, id)
        hero_id = get_hero_id(str(group))
        url = f'http://delta.world-of-dungeons.org/wod/spiel/dungeon/report.php?session_hero_id={hero_id}'
        d.open(url)

    print(f'解析buff {group}, {report_id} 1')
    #//*[@id="main_content"]/div/form/table/tbody/tr[2]/td[3]/input[2]              tr[x+1] 是第x个战报 td[3] 统计表的外框  input1,2,3,4: 隐藏的id, 统计表, 物品, 资料
    detail_button = d.find_xpath(f'//*[@id="main_content"]/div/form/table/tbody/tr[{num+1}]/td[3]/input[4]') # 加1因为1是表头, 战报从2开始的
    if detail_button is None:
        return False, f'找到战报{report_id}, 缺找不到{num}的详细信息?'
    
    detail_button.click()

    # 一层的按钮 //*[@id="main_content"]/div/form/div/table[2]/tbody/tr/td/p[1]/input[1]
    # 二层的按钮 //*[@id="main_content"]/div/form/div/table[2]/tbody/tr/td/p[1]/input[2]
    # 将收集到的内容写入文件
    regt = r'([^\d\
]+) ([+-]\d*[.%]?\d*%?)? ?([+-]\d*.?\d*%+)?/?([+-]\d*[.%]?\d*%?)? ?([+-]\d*.?\d*%+)?/?([+-]\d*[.%]?\d*%?)? ?([+-]\d*.?\d*%+)? ?(\(.*\))? ?(.回合.*)?'
    create_at = datetime.datetime.now(zoneinfo.ZoneInfo(key='Asia/Shanghai'))
    inputs = d.finds_xpath('//*[@id="main_content"]/div/form/div/table[2]/tbody/tr/td/p[1]/input')
    print(f'{report_id} input {len(inputs)}')
    layer = 0
    is_db_tran = False
    # buttons = d.finds_xpath('//*[@id="main_content"]/div/form/div/table[2]/tbody/tr/td/p[1]//input[contains(@value, "层")]')
    for input in inputs:
        if layer > 1:
            print(f'click {layer} b')
            # input.click()
            xpath = f'//*[@id="main_content"]/div/form/div/table/tbody/tr[1]/td/p[1]/input[{layer+1}]'
            if layer == 1:
                xpath = f'//*[@id="main_content"]/div/form/div/table[2]/tbody/tr[1]/td/p[1]/input[{layer+1}]'
            d.wait(xpath)
            next_layer = d.find_xpath(xpath)
            if next_layer is None:
                print(f'buff 找下一层的按钮失败了, 当前{layer}. {id}')
                continue
            next_layer.click()
            print(f'click {layer} e')
        time.sleep(3)
        layer += 1
        print(f'当前层: {layer}')
        # # 等待最后回合加载出来
        # if layer == 1 and d.find_xpath('//*[@id="main_content"]/div/form/div/table[2]/tbody/tr[1]/td/p[2]/a[2]') is None:
        #     print(f'wait  {layer}  .... ')
        #     d.wait('//*[@id="main_content"]/div/form/div/table[2]/tbody/tr[1]/td/p[2]/a[2]')
        #     print(f'wait  {layer}  end ')
        # if layer > 1 and d.find_xpath('//*[@id="main_content"]/div/form/div/table/tbody/tr/td/p[5]') is None:
        #     print(f'wait  {layer}  .... ')
        #     d.wait('//*[@id="main_content"]/div/form/div/table/tbody/tr[1]/td/p[2]/a[2]')
        #     print(f'wait  {layer}  end ')
        print(f'parse {id} {layer} ')
        html_content = d.get_page()
        soup = BeautifulSoup(html_content, 'html.parser')

        print(f'soupp {layer} b')
        # 找到所有相关的回合并提取 onmouseover 内容
        round_headlines = soup.find_all(class_='rep_round_headline')
        round_count = 0
        grouped_data = {}
        round_num = 0

        for round_headline in round_headlines:
            next_element = round_headline.find_next_sibling()
            while next_element:
                if next_element.name == 'p' and 'rep_status_headline' in next_element['class']:
                    who = next_element.get_text(strip=True)
                    if who != '进攻者:':
                        next_element = next_element.find_next_sibling('p')
                        continue
                    print(who)
                    table = next_element.find_next_sibling('table')
                    if table:
                        round_num = 0
                        for row in table.find_all('tr')[1:]:  # 忽略表头
                            number_td = row.find('td', class_='number')
                            hero_td = row.find('td', class_='hero')
                            if number_td and hero_td:
                                number = number_td.text.strip()  # 获取角色的编号
                                hero_link = hero_td.find('a')
                                
                                if ( hero_link and hero_link.has_attr('href') ):
                                    # 获取数字 ID
                                    #hero_id = re.search(r'id=(\d+)', hero_link['href']).group(1)  # 提取ID数字 召唤物没有id
                                    #hero_id = hero_link['x'] if 'x' in hero_link.attrs else 0 自己没有x
                                    hero_id = re.search(r'id=(\d+)', hero_link['href'])
                                    hero_id = int(hero_id.group(1)) if hero_id else 0

                                    hero_name = hero_link.text.strip()  # 获取英雄的名字
                                    # 修改为新的链接格式，使用对应的数字
                                    # hero_link_new = f"{hero_name}-{hero_id}"
                                
                                    span = row.find('span', onmouseover=True)  # 寻找 onmouseover
                                    if span:
                                        mouse_over_content = span['onmouseover']
                                        match = re.search(r"wodToolTip\(this,'(.*?)'\)", mouse_over_content)
                                        if match:
                                            actual_content = match.group(1)
                                            # 转换 HTML 实体为普通文本
                                            actual_content = html.unescape(actual_content)  # 将HTML实体转换为普通文本
                                            if '属于' in actual_content:
                                                continue
                                            print(hero_id)
                                            # 替换 <br /> 为换行符 '\n'
                                            actual_content = actual_content.replace('<br />', '\n')
                                            # 准备换行符的变量
                                            new_content = ""
                                            # 分割不同的部分
                                            sections = re.split(r'&lt;b&gt;|&lt;/b&gt;', actual_content)
                                            for section in sections:
                                                new_content += '\n' + section.strip() + '\n'
                                            # 清理多余空格
                                            new_content = re.sub(r'\s+', ' ', new_content).strip()
                                            round_num = int(round_headline.text.strip().split()[1])
                                            actual_content = re.sub(r'<.*?>', '', actual_content)  # 移除所有HTML标签
                                            # print(actual_content)
                                            # actual_content = re.sub(r'\s+', ' ', actual_content).strip()  # 删除多余空格
                                            if round_num not in grouped_data:
                                                grouped_data[round_num] = {}
                                            if hero_name not in grouped_data[round_num]:
                                                grouped_data[round_num][hero_name] = {
                                                'number': number,
                                                # 'hero_name': hero_name,
                                                'hero_id': hero_id,
                                                'content': {}
                                                }
                                                lines = actual_content.splitlines()
                                                key = None
                                                for line in lines:
                                                    # print(line)
                                                    ret = re.match(regt, line)
                                                    if ret:
                                                        sub_key = ret.group(1)
                                                        if ret.group(8) and ret.group(8) != 0:
                                                            sub_key+=f' {ret.group(8)}'
                                                        if ret.group(9) and ret.group(9) != 0:
                                                            sub_key+=f' {ret.group(9)}'
                                                            
                                                        grouped_data[round_num][hero_id]['content'][key][sub_key] = {}
                                                        if ret.group(2) and ret.group(2) != 0:
                                                            grouped_data[round_num][hero_id]['content'][key][sub_key]['b1'] = ret.group(2) 
                                                        if ret.group(3) and ret.group(3) != 0:
                                                            grouped_data[round_num][hero_id]['content'][key][sub_key]['p1'] = ret.group(3) 
                                                        if ret.group(4) and ret.group(4) != 0:
                                                            grouped_data[round_num][hero_id]['content'][key][sub_key]['b2'] = ret.group(4) 
                                                        if ret.group(5) and ret.group(5) != 0:
                                                            grouped_data[round_num][hero_id]['content'][key][sub_key]['p2'] = ret.group(5) 
                                                        if ret.group(6) and ret.group(6) != 0:
                                                            grouped_data[round_num][hero_id]['content'][key][sub_key]['b3'] = ret.group(6) 
                                                        if ret.group(7) and ret.group(7) != 0:
                                                            grouped_data[round_num][hero_id]['content'][key][sub_key]['p3'] = ret.group(7) 
                                                        # print(f'g1:对象 {ret.group(1)}, g2:值1 {ret.group(2)}, g3:值1的百分比 {ret.group(3)}, g4:值2 {ret.group(4)},g5:值2的百分比 {ret.group(5)}, g6:值3 {ret.group(6)}, g7:值3的百分比 {ret.group(7)}, g8:xx {ret.group(8)}, g9:x回合后 {ret.group(9)}')
                                                    else:
                                                        ret = re.match("(.*):", line)
                                                        if ret:
                                                            key= ret.group(1)
                                                            print(key)
                                                            grouped_data[round_num][hero_id]['content'][key] = {}
                                            round_count = max(round_count, round_num)
                    # break  # 跳出循环，因为已经找到要处理的部分
                next_element = next_element.find_next_sibling()
        if round_num > 0:
            print(f'insert report_layer, this layer {layer}, {round_num}')
            if dbi.exec_no_fetch(sql.insert_report_layer, (create_at, id, layer, round_count, json.dumps(grouped_data))) is None:
                return False, f'插入{id}的{layer}层战报数据 时失败'
            is_db_tran = True

    if is_db_tran:
        print(f'db commit ')
        dbi.commit()
        return True, f'解析成功, 插入{id}的{layer}层战报数据'

    print(f'parse is quit')
    return False, f''

# 外部输入: 战报id, 层, 回合, 名字
def __get_buff(group, report_id, layer, turn, name, skill, prop):
    global layer_reports
    if report_id not in layer_reports:
        dbi = db.Pdb.get_instance()
        records = dbi.exec_one(sql.select_report_layer, (report_id, layer,))
        dbi.commit()
        if records is None:
            return False, f'战报 {report_id} 还未执行过 解析buff'
    else:
        records = layer_reports[report_id]
    #print(f'get buff db return : {records}')
    if records is None:
        return False, f'战报 {report_id} 还未执行过 解析buff'
    print(f'get buff, db_id {records[0]}, layer {records[1]}, round_count {records[2]}')
    detail = records[3]
    if turn not in detail:
        return False, f'战报 {report_id} 层 {layer} 回合 {turn} 不存在, db最大回合 {records[2]}'
    
    for round_num, heroes in detail.items():
        print(f'get buff for round_num : {round_num}')
        if round_num != turn:
            continue
        if name not in heroes:
            return False, f'{report_id} 中找不到{name}'
        heroes = heroes[name]
        
        print(f'get buff for round_num : {heroes}')
        print(f"  英雄 ID: {heroes['hero_id']}")
        print(f"  英雄名称: {heroes['hero_name']}")
        print(f"  位置: {heroes['number']}")
        # 遍历技能内容
        content = heroes.get('content', {})
        if skill in content:
            ret_str = ''
            for effect, values in content[skill].items():
                ret_str+= f'\n{effect} '
                for prop, value in values.items():
                    if prop == 'b2' or prop == 'b2':
                        ret_str+='/'
                    ret_str+=value
                # 打印效果
                print(f"    效果: {skill} -> {ret_str}")
            return True, f'战报 {report_id} 层 {layer} 回合 {turn} 玩家 {name} [{skill}] 的buff:{ret_str}\n'
        else:
            return False, f'战报 {report_id} 层 {layer} 回合 {turn} 玩家 {name} 找不到 {skill} 的buff'
        for item_name, attributes in content.items():
            if item_name != skill:
                continue
            print(f"    技能: {item_name}")
            total = {}
            for attr_name, attr_value in attributes.items():
                #print(f"      {attr_name}: {attr_value}")
                #detail =
                if attr_name not in total:
                    total[attr_name] = {}
                for i, v in attr_value.items():
                    print(f"      i:{i}: v:{v}")
                    #print(f"      total[attr_name][i]:{total[attr_name][i]}")
                    if v.endswith('%'):
                        i = i.replace('b', 'p')
                        v = v[:-1]
                    if i in total[attr_name]:
                        total[attr_name][i] += float(v)
                    else:
                        total[attr_name][i] = float(v)
            print(f'     total: {total}')
