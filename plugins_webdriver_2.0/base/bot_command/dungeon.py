import re
import requests
import time
import json
import shelve
from datetime import datetime, timedelta
import os
from bs4 import BeautifulSoup

import plugins.base.common.jscode as base
import plugins.base.base.driver as driver
from plugins.base.common.base import get_hero_id, GroupIDMaps

hero_ids = (0, 0)

d_today = {}
d_common = {}
d_tomorrow = {}
d_self = {}
hero_lv = {}
min_lv = {}

def checkInit(func):
    def wapper(*args, **kwargs):
        if args[0] not in hero_lv:
            __init_lv(args[0])
            calc_lv(args[0], False)
        return func(*args, **kwargs)
    return wapper

def checkLv(func):
    def wapper(*args, **kwargs):
        if args[0] not in hero_lv:
            __init_lv(args[0])
        return func(*args, **kwargs)
    return wapper

def __init_lv(group):
        hero_lv[group] = 0
        min_lv[group] = 0
        print(f' *** init lv value')
def __init_dg():
    for group in GroupIDMaps.keys():
        d_today[group] = {}
        d_common[group] = {}
        d_tomorrow[group] = {}
    print(f' *** init dungeon value')

def __init_self_dg():
    d = shelve.open('self_dungeon.txt')
    global d_self
    if 'd_self' in d:
        d_self = d['d_self']
    d.close()
    print(f' *** init self dungeon value')

def __check_timestamp(timestamp):
    six_am_today_ts = datetime.timestamp(datetime.now().replace(hour=6,minute=0,second=0,microsecond=0))
    print("check time stamp input {}, six {}, not bigger six {}, diff {} ".format(int(timestamp), int(six_am_today_ts),
    int(timestamp)<= int(six_am_today_ts), int(timestamp)- int(six_am_today_ts) ))
    return int(timestamp) <= int(six_am_today_ts)

def __init_dungeon(json_d, group, hero_lv):
    d_common[group] = {}
    d_today[group] = {}
    d_tomorrow[group] = {}
    m_lv = min_lv[group]
    now = datetime.now()
    print(f'init dungeon, now{now}')
    for d in json_d['data']:
        if d['type']=='P' and d['minLevel'] <= m_lv and d['maxLevel'] >= hero_lv:
            d_common[group][d['name']] = d['sysId']
        elif d['type']=='L' and d['minLevel'] <= m_lv and d['maxLevel'] >= hero_lv:
            start_time = datetime.fromisoformat(d['startTime'])
            if start_time < now < datetime.fromisoformat(d['endTime']):
                d_today[group][d['name']] = d['sysId']
            elif now < start_time < now+timedelta(hours=24):
                d_tomorrow[group][d['name']] = d['sysId']

def update_dungeon(group, foucs_update = False):
    today_str = datetime.now().strftime("%Y%m%d")
    tick_name = f'test_{group}'
    is_first = False
    if os.path.exists('dungeons.json') and os.path.getsize('dungeons.json'):
        with open('dungeons.json', 'r+') as json_file:
            d_j = json.load(json_file)
            if d_j['time'] == today_str:
                if not d_j.get(tick_name):
                    d_j[tick_name] = time.time()
                    print("dont have tick, init tick, json name {}, value {}".format(tick_name, d_j[tick_name]))
                    is_first = True
                is_next_day = __check_timestamp((d_j[tick_name]))
                if group not in d_common or is_next_day or foucs_update or is_first:
                    d_j[tick_name] = time.time()
                    __init_dungeon(d_j, group, hero_lv[group])
                    print("update by local file dungeon {}, is next day {}, today size {}".format(today_str, is_next_day, len(d_today[group])))
                    with open('dungeons.json', 'w') as json_file:
                        json.dump(d_j, json_file, ensure_ascii=False, indent=4)  # indent=4 让 JSON 文件更美观
                return True, "本地文件更新"
            json_file.seek(0)
            json_file.truncate()

    headers = {
        "Content-Type": "application/json",
    }
    resp = requests.post('https://www.christophero.xyz/wod/dungeon/listCommon', headers=headers)
    if resp.status_code != 200:
        print("cnat update dungeon {}".format( today_str))
        return False, f"wiki无法链接, 状态码{resp.status_code}"
    resp.encoding = 'utf-8'  # 或者使用 response.apparent_encoding
    dungeons = json.loads(resp.text)
    if dungeons['code'] == 200 and dungeons['msg']=='请求成功':
        dungeons['time'] = today_str
        dungeons[tick_name] = time.time()
        print("update by wiki web dungeon {}".format( today_str))
        with open('dungeons.json', 'w') as json_file:
            json.dump(dungeons, json_file, ensure_ascii=False, indent=4)  # indent=4 让 JSON 文件更美观
    __init_dungeon(dungeons, group, hero_lv[group])
    print("update by wiki web dungeon today size {}".format(len(d_today)))
    return True, "wiki更新成功"

@checkInit
def reply_common(group):
    update_dungeon(group)
    return True, "常规地城列表\n{}".format('\n'.join(e for e in d_common[group].keys()))

@checkInit
def reply_today(group):
    update_dungeon(group)
    return True, "今日地城列表\n{}".format('\n'.join(e for e in d_today[group].keys()))

@checkInit
def reply_tomorrow(group):
    update_dungeon(group)
    return True, "明日地城列表\n{}".format('\n'.join(e for e in d_tomorrow[group].keys()))

@checkInit
def reply_time(group):
    update_dungeon(group)
    return True, "今日地城列表\n{}\n\n明日地城列表\n{}".format('\n'.join(e for e in d_today[group].keys()), '\n'.join(e for e in d_tomorrow[group].keys()))

def reply_self(group):
    return True, "自定义地城列表\n{}".format('\n'.join(e for e in d_self[group].keys()))

@checkLv
def get_lv(group):
    cacha_lv = hero_lv[group]
    return (True, f'缓存等级{cacha_lv}, 最小等级 {min_lv[group]}') if cacha_lv != 0 else calc_lv(group, False)

@checkLv
def calc_lv(group, is_init):
    hero_id = get_hero_id(group)
    url = f'http://delta.world-of-dungeons.org/wod/spiel/dungeon/group.php?session_hero_id={hero_id}'
    d = driver.WodDriver.get_instance()
    resp = d.open_get_page(url)
    # resp.encoding = 'utf-8'  # 或者使用 response.apparent_encoding
    if resp:
        with open('get_lv.html', 'w', encoding='utf-8') as file:
            file.write(resp)  # 如果是二进制内容，可以使用 response.content
        cacha_lv = hero_lv[group]
        soup = BeautifulSoup(resp, 'html.parser')
        subline_spans = soup.find_all('span', class_ = 'content_table_subline')
        total_lv = count = 0
        m_lv = 41
        for s in subline_spans:
            ret = re.match(r'.*等级(\d+).*', s.get_text())
            if ret:
                cur_lv = int(ret.group(1))
                total_lv += cur_lv
                count += 1
                if m_lv > cur_lv:
                    m_lv = cur_lv
        if count != 0:
            lv = total_lv//count
            cacha_min_lv = min_lv[group]
            print(f'total {total_lv}, count {count}, lv {total_lv/count}, lvv {lv}, cache_lv {cacha_lv}')
            hero_lv[group] = lv
            min_lv[group] = m_lv
            if m_lv != cacha_min_lv or cacha_lv != lv:
                update_dungeon(group)
            if not is_init:
                return True, f"获取等级 成功, 总等级 {total_lv}, 人数 {count}, 缓存等级 {cacha_lv}, 计算等级{total_lv/count:.2f}, 新等级 {lv}, 最小等级 {m_lv}"
        else:
            print(f'total {total_lv}, count eq 0, cant calc lv')
            if not is_init:
                return False, f"获取等级 失败, 总等级 {total_lv}, 人数 {count}, 缓存等级 {cacha_lv}, 最小等级 {m_lv}"
    else:
        if not is_init:
            return False, "获取等级 失败"
    return False, ""

def cur_dungeon(group):
    hero_id = get_hero_id(group)
    url = f'http://delta.world-of-dungeons.org/wod/spiel/dungeon/group.php?session_hero_id={hero_id}'
    d = driver.WodDriver.get_instance()
    d.open(url)
    # 等团队金库加载出来
    if not d.wait('//*[@id="gadgettable-right-gadgets"]/div[3]/div/div/div/div/div/div[1]/a/span'):
        return False, f"获取当前地城 失败, 超时 或者 没有下个地城"
    end_time = d.find_xpath('//*[@id="gadgetNextdungeonTime"]')
    if end_time:
        end_time = " 结束时间 " + end_time.text
    else:
        return False, f"获取当前地城 失败, 无法解析时间"
    next_name = d.find_xpath('//*[@id="gadgettable-right-gadgets"]/div[2]/div/div/div/div/div/b/a')
    next_name = "当前地城 "+next_name.text

    can_end = d.find_xpath('//*[@id="gadgettable-right-gadgets"]/div[2]/div/div/div/div/div/input')
    if can_end:
        reduce_time = d.find_name("reduce_dungeon_time")
        if reduce_time:
            end_time = " 已点击提前, 结束时间 "+reduce_time.get_attribute("value")
        can_end.click()

    return True, f"{next_name}{end_time}"

def cancle_dungeon(group):
    hero_id = get_hero_id(group)
    url = f'http://delta.world-of-dungeons.org/wod/spiel/dungeon/group.php?session_hero_id={hero_id}'
    d = driver.WodDriver.get_instance()
    if url != d.geturl():
        d.open(url)

    if not d.wait('//*[@id="gadgettable-right-gadgets"]/div[3]/div/div/div/div/div/div[1]/a/span'):
        return False, f"取消地城 失败, 页面超时"
    exec_ret = d.exce_js(base.rep_str['cancle_d'])
    return exec_ret, f"取消地城 {'成功' if exec_ret else '失败'}"

def dungeon_state(group):
    return True, f"常规地城列表 {len(d_common[group])} 个\n今日地城列表 {len(d_today[group])} 个\n明日地城列表 {len(d_tomorrow[group])} 个"

def add_self_dungeon(group, name, d_id):
    self_dungeon = d_self.setdefault(group, {}).setdefault(name, int(d_id))
    d = shelve.open('self_dungeon.txt')
    d['d_self'] = d_self
    d.close()
    return True, f'添加自定义地城 {name} 成功, id {d_id}'

@checkInit
def change_dungeon(group, name):
    d_id = 0
    update_dungeon(group)

    print(f"group {group}, 常规地城列表 {len(d_common[group])} 个\n今日地城列表 {len(d_today[group])} 个\n明日地城列表 {len(d_tomorrow[group])} 个")
    d_id = d_common[group].get(name) or d_today[group].get(name) or d_tomorrow[group].get(name) or d_self[group].get(name)
    if d_id is None:
        return False, "地城 {} 不可达".format(name)

    hero_id = get_hero_id(group)
    url = f'http://delta.world-of-dungeons.org/wod/spiel/dungeon/group.php?session_hero_id={hero_id}'
    d = driver.WodDriver.get_instance()
    if url != d.geturl():
        d.open(url)

    if not d.wait('//*[@id="gadgettable-right-gadgets"]/div[3]/div/div/div/div/div/div[1]/a/span'):
        return False, f"切换 {name} 失败, 页面超时"
    js_code = base.rep_str['d1'] + f"searchParams.set(`visit[{d_id}]`, '探索');" + base.rep_str['d2']
    exec_ret = d.exce_js(js_code)
        
    time.sleep(2)
    end_time = ""
    if exec_ret:
        if d.find_xpath('//*[@id="gadgetNextdungeonTime"]'):
            end_time = " 结束时间:" + d.find_xpath('//*[@id="gadgetNextdungeonTime"]').text
    next_name = d.find_xpath('//*[@id="gadgettable-right-gadgets"]/div[2]/div/div/div/div/div/b/a')
    count = 0
    while not next_name and count < 10:
        time.sleep(1)
        next_name = d.find_xpath('//*[@id="gadgettable-right-gadgets"]/div[2]/div/div/div/div/div/b/a')

    can_end = d.find_xpath('//*[@id="gadgettable-right-gadgets"]/div[2]/div/div/div/div/div/input')
    if can_end:
        reduce_time = d.find_name("reduce_dungeon_time")
        if reduce_time:
            end_time = " 已点击提前, 结束时间 "+reduce_time.get_attribute("value")
        if can_end.is_displayed():
            can_end.click()
        else:
            end_time = " 点击提前结束失败"

    back_next = ""
    if next_name:
        back_next=next_name.text

    return exec_ret, f"切换 {name} {'成功' if exec_ret else '失败'}, 读取地城 {back_next}\n{end_time}"

def __get_time(hour, min):
    min += 50
    if min + 50 >= 60:
        hour += 1
        min  -= 60
    hour += 6
    if hour >= 24:
        return True, hour - 24, min
    return False, hour, min

def __get_time_str(time_str):
    tt = time_str.split(' ')
    prefix = ""
    if len(tt) > 1:
        prefix = tt[0]
        tt=tt[1]
    else:
        tt=tt[0]
    h, m = map(int, tt.split(':'))
    is_new_day, h, m = __get_time(h, m)
    match prefix:
        case "昨天":
            if is_new_day: prefix = "今天 "
        case "今天":
            if is_new_day: prefix = "明天 "
        case "":
            if is_new_day: prefix = "明天 "
        case "明天":
            if is_new_day: prefix = "后天 "
        case _:
            prefix += " "

    print(f"IS NEW DAY {is_new_day}, h {h}, m {m}, time_str {time_str}, prfix {prefix}")

    return f"预估下个地城时间 {prefix}{h:02}:{m:02}\n"

def get_all_dungeon_state(group):
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
        ret = ""
        last_time = ""
        # 输出每个地城及其对应的 value
        for row in table.find_all('tr')[1:]:  # Skip the header row
            cols = row.find_all('td')
            date = cols[0].get_text(strip=True)
            dungeon = cols[1].get_text(strip=True)
            # Find the hidden input to get the value
            hidden_input = cols[2].find('input', type='hidden')
            value = hidden_input['value'] if hidden_input else None
            report_entries.append(
                {'ID': value, 'date': date, 'dungeon': dungeon})
            ret = f"上个地城 {dungeon}, 时间 {date},    ID {value}\n"
            last_time = date.split(" ")[1]
            break
        if d.wait('//*[@id="gadgettable-right-gadgets"]/div[3]/div/div/div/div/div/div[1]/a/span'):
            end_time = d.find_xpath('//*[@id="gadgetNextdungeonTime"]')
            if end_time:
                next_dungeon_ret = __get_time_str(end_time.text)
                end_time = " 结束时间 " + end_time.text
                next_name = d.find_xpath(
                    '//*[@id="gadgettable-right-gadgets"]/div[2]/div/div/div/div/div/b/a')
                next_name = "当前地城 "+next_name.text

                can_end = d.find_xpath(
                    '//*[@id="gadgettable-right-gadgets"]/div[2]/div/div/div/div/div/input')
                if can_end:
                    reduce_time = d.find_name("reduce_dungeon_time")
                    if reduce_time:
                        end_time = " 已点击提前, 结束时间 "+reduce_time.get_attribute("value")
                    can_end.click()
                ret += f"{next_name}{end_time}\n"

                ret += next_dungeon_ret
            else:
                ret += f"当前没有地城\n"
                if last_time:
                    ret += __get_time_str(last_time)
                else:
                    ret += f"找不到上个地城, 无法预估下个地城时间\n"
        else:
            ret += f"读取地城失败\n"

        print("get all dungeon state : "+ret)
        return True, ret
    else:
        return False, f'打开战报界面失败'



# __init_val()
__init_self_dg()
