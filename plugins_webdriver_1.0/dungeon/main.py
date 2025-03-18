from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import re
import requests
import time
import json
from datetime import datetime, timedelta
import os
from bs4 import BeautifulSoup
from urllib.parse import quote

from plugins.base.main import  groups
import plugins.base.jscode as base
import plugins.base.driver as driver

hero_ids = (0, 0)

#ctx.add_return("reply", f'test target {ctx.event.launcher_id}')
# setattr(self, f'xx_{num}, None)
#(getattr(self, f'xx_{num}'))
def decorator_time(func):
    # 异步装饰器
    async def wrapper(self, *args):
        curTick = time.perf_counter()
        ctx = None
        # kwargs 取参数
        # if 'ctx' in kwargs:
            # ctx = kwargs['ctx']
        # 异步调用被修饰的方法
        ret, ret_str = await func(self, *args)

        # args 取参数
        if args:
            ctx = args[0]
        if ctx:
            ctx.add_return("reply", ["{}, 操作耗时: {:.2f}".format(ret_str, time.perf_counter() - curTick)])
            ctx.prevent_default()
        else:
            self.ap.logger.error("无法找到ctx")

    return wrapper


heros = {}
hero_names = {}

def get_hero_names(group):
    return hero_names[group] if group in hero_names else None

# 注册插件
@register(name="dungeon", description="地城", version="0.1", author="x")
class MyPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        for group in groups:
            setattr(self, f'd_today_{group}', {})
            setattr(self, f'd_common_{group}', {})
            setattr(self, f'd_tomorrow_{group}', {})
            setattr(self, f'hero_lv_{group}', 0)
            setattr(self, f'min_lv_{group}', 0)
        
        setattr(self, f'hero_id_{groups[0]}', hero_ids[0])
        setattr(self, f'hero_id_{groups[1]}', hero_ids[1])

    def _check_timestamp(self, timestamp):
        today = datetime.now().replace(hour=6,minute=0,second=0,microsecond=0)
        six_am_today_ts = datetime.timestamp(today)
        self.ap.logger.info("check time stamp input {}, six {}, not bigger six {}, diff {} ".format(int(timestamp), int(six_am_today_ts),
        int(timestamp)<= int(six_am_today_ts), int(timestamp)- int(six_am_today_ts) ))
        return int(timestamp) <= int(six_am_today_ts)

    def _init_dungeon(self, json_d, group, hero_lv):
        d_common = getattr(self, f'd_common_{group}')
        d_today = getattr(self, f'd_today_{group}')
        d_tomorrow = getattr(self, f'd_tomorrow_{group}')
        d_common.clear()
        d_today.clear()
        d_tomorrow.clear()
        min_lv = getattr(self, f'min_lv_{group}')
        now = datetime.now()
        self.ap.logger.critical(f'init dungeon, now{now}')
        for d in json_d['data']:
            if d['type']=='P' and d['minLevel'] <= min_lv and d['maxLevel'] >= hero_lv:
                d_common[d['name']] = d['sysId']
            elif d['type']=='L' and d['minLevel'] <= min_lv and d['maxLevel'] >= hero_lv:
                start_time = datetime.fromisoformat(d['startTime'])
                if start_time < now < datetime.fromisoformat(d['endTime']):
                    d_today[d['name']] = d['sysId']
                elif now < start_time < now+timedelta(hours=24):
                    d_tomorrow[d['name']] = d['sysId']

    def update_dungeon(self, group, ctx: EventContext, foucs_update = False):
        today_str = datetime.now().strftime("%Y%m%d")
        tick_name = f'test_{group}'
        is_first = False
        d_common = getattr(self, f'd_common_{group}')
        d_today = getattr(self, f'd_today_{group}')
        d_tomorrow = getattr(self, f'd_tomorrow_{group}')
        if os.path.exists('dungeons.json') and os.path.getsize('dungeons.json'):
            with open('dungeons.json', 'r+') as json_file:
                d_j = json.load(json_file)
                if d_j['time'] == today_str:
                    if not d_j.get(tick_name):
                        d_j[tick_name] = time.time()
                        self.ap.logger.info("dont have tick, init tick, json name {}, value {}".format(tick_name, d_j[tick_name]))
                        is_first = True
                    is_next_day = self._check_timestamp((d_j[tick_name]))
                    if not d_common or is_next_day or foucs_update or is_first:
                        d_j[tick_name] = time.time()
                        self._init_dungeon(d_j, group, getattr(self, f'hero_lv_{group}'))
                        self.ap.logger.critical("update by local file dungeon {}, is next day {}, today size {}".format(today_str, is_next_day, len(d_today)))
                        with open('dungeons.json', 'w') as json_file:
                            json.dump(d_j, json_file, ensure_ascii=False, indent=4)  # indent=4 让 JSON 文件更美观
                    return True, "本地文件更新"
                json_file.seek(0)
                json_file.truncate()

        curTick = time.perf_counter()
        headers = {
            "Content-Type": "application/json",
        }
        resp = requests.post('https://www.christophero.xyz/wod/dungeon/listCommon', headers=headers)
        if resp.status_code != 200:
            self.ap.logger.critical("cnat update dungeon {}".format( today_str))
            return False, f"wiki无法链接, 状态码{resp.status_code}"
        resp.encoding = 'utf-8'  # 或者使用 response.apparent_encoding
        dungeons = json.loads(resp.text)
        if dungeons['code'] == 200 and dungeons['msg']=='请求成功':
            dungeons['time'] = today_str
            dungeons[tick_name] = time.time()
            self.ap.logger.critical("update by wiki web dungeon {}".format( today_str))
            with open('dungeons.json', 'w') as json_file:
                json.dump(dungeons, json_file, ensure_ascii=False, indent=4)  # indent=4 让 JSON 文件更美观
        self._init_dungeon(dungeons, group, getattr(self, f'hero_lv_{group}'))
        self.ap.logger.critical("update by wiki web dungeon today size {}".format(len(d_today)))
        return True, "wiki更新成功"

    def reply_common(self, group, ctx: EventContext):
        self.update_dungeon(group,ctx)
        # ctx.add_return("reply", ["常规地城列表\n{}".format("\n".join(e for e in getattr(self, f'd_common_{group}').keys()))])
        return True, "常规地城列表\n{}\n".format('\n'.join(e for e in getattr(self, f'd_common_{group}').keys()))

    def reply_today(self, group, ctx: EventContext):
        self.update_dungeon(group,ctx)
        # ctx.add_return("reply", ["今日地城列表\n{}".format("\n".join(e for e in getattr(self, f'd_today_{group}').keys()))])
        return True, "今日地城列表\n{}\n".format('\n'.join(e for e in getattr(self, f'd_today_{group}').keys()))
    
    def reply_tomorrow(self, group, ctx: EventContext):
        self.update_dungeon(group,ctx)
        # ctx.add_return("reply", ["明日地城列表\n{}".format("\n".join(e for e in getattr(self, f'd_tomorrow_{group}').keys()))])
        return True, "明日地城列表\n{}\n".format('\n'.join(e for e in getattr(self, f'd_tomorrow_{group}').keys()))

    def get_lv(self, group, ctx: EventContext):
        cacha_lv = getattr(self, f'hero_lv_{group}')
        min_lv = getattr(self, f'min_lv_{group}')
        if cacha_lv != 0:
            # ctx.add_return("reply", [f'缓存等级{cacha_lv}, 最小等级 {min_lv}'])
            return True, f'缓存等级{cacha_lv}, 最小等级 {min_lv}'
        return self.calc_lv(group, ctx, False)

    def calc_lv(self, group, ctx: EventContext, is_init):
        curTick = time.perf_counter()
        hero_id = getattr(self, f'hero_id_{group}')
        url = f'http://delta.world-of-dungeons.org/wod/spiel/dungeon/group.php?session_hero_id={hero_id}'
        d = driver.WodDriver.get_instance()
        resp = d.open_get_page(url)
        # resp.encoding = 'utf-8'  # 或者使用 response.apparent_encoding
        if resp:
            global heros, hero_names
            hero_names[group] = {}
            heros[group] = {}
            with open('get_lv.html', 'w', encoding='utf-8') as file:
                file.write(resp)  # 如果是二进制内容，可以使用 response.content
            # ctx.add_return("reply", ["获取等级 成功 操作耗时: {:.2f}".format( time.perf_counter() - curTick)])
            cacha_lv = getattr(self, f'hero_lv_{group}')
            soup = BeautifulSoup(resp, 'html.parser')
            subline_spans = soup.find_all('span', class_ = 'content_table_subline')
            total_lv = 0
            count = 0
            min_lv = 41
            for s in subline_spans:
                ret = re.match(r'.*等级(\d+).*', s.get_text())
                if ret:
                    cur_lv = int(ret.group(1))
                    total_lv += cur_lv
                    count += 1
                    hero_info = d.find_xpath(f'//*[@id="smarttabs__members_inner"]/div[5]/table/tbody/tr[{count}]/td[2]/span[1]/a')
                    if hero_info:
                        # 提取 ID 和名字
                        href = hero_info.get_attribute('href')
                        id_match = re.search(r'id=(\d+)', href)  # 使用正则表达式提取 ID
                        hero_id = id_match.group(1) if id_match else None
                        name = hero_info.text
                        if hero_id:
                            heros[group][hero_id] = name
                            hero_names[group][name] = hero_id
                    if min_lv > cur_lv:
                        min_lv = cur_lv
            if count != 0:
                lv = total_lv//count
                cacha_min_lv = getattr(self, f'min_lv_{group}')
                self.ap.logger.info(f'total {total_lv}, count {count}, lv {total_lv/count}, lvv {lv}, cache_lv {cacha_lv}')
                setattr(self, f'hero_lv_{group}', lv)
                setattr(self, f'min_lv_{group}', min_lv)
                if min_lv != cacha_min_lv or cacha_lv != lv:
                    self.update_dungeon(group, ctx)
                if not is_init:
                    ctx.add_return("reply", [f"获取等级 成功, 总等级 {total_lv}, 人数 {count}, 缓存等级 {cacha_lv}, 计算等级{total_lv/count:.2f}, 新等级 {lv}, 最小等级 {min_lv}, 操作耗时: {(time.perf_counter() - curTick):.2f}"])
                    return True, f"获取等级 成功, 总等级 {total_lv}, 人数 {count}, 缓存等级 {cacha_lv}, 计算等级{total_lv/count:.2f}, 新等级 {lv}, 最小等级 {min_lv}, 操作耗时: {(time.perf_counter() - curTick):.2f}"
            else:
                self.ap.logger.info(f'total {total_lv}, count eq 0, cant calc lv')
                if not is_init:
                    ctx.add_return("reply", [f"获取等级 失败, 总等级 {total_lv}, 人数 {count}, 缓存等级 {cacha_lv}, 最小等级 {min_lv}, 操作耗时: {format(time.perf_counter() - curTick):.2}"])
                    return False, f"获取等级 失败, 总等级 {total_lv}, 人数 {count}, 缓存等级 {cacha_lv}, 最小等级 {min_lv}, 操作耗时: {format(time.perf_counter() - curTick):.2}"
        else:
            if not is_init:
                ctx.add_return("reply", ["获取等级 失败,  操作耗时: {}".format(time.perf_counter() - curTick)])
                return False, "获取等级 失败,  操作耗时: {}".format(time.perf_counter() - curTick)

    def cur_dungeon(self, group, ctx):
        hero_id = getattr(self, f'hero_id_{group}')
        url = f'http://delta.world-of-dungeons.org/wod/spiel/dungeon/group.php?session_hero_id={hero_id}'
        d = driver.WodDriver.get_instance()
        d.open(url)
        # if not d.wait('//*[@id="smarttabs__members_inner"]/p[7]'):
        #     return False, f"获取当前地城 失败, 页面超时"
        # 等团队金库加载出来
        if not d.wait('//*[@id="gadgettable-right-gadgets"]/div[3]/div/div/div/div/div/div[1]/a/span'):
            return False, f"获取当前地城 失败, 超时 或者 没有下个地城"
        end_time = d.find_xpath('//*[@id="gadgetNextdungeonTime"]')
        if end_time:
            end_time = " 结束时间 " + end_time.text
        else:
            return False, f"获取当前地城 失败, 无法解析时间"
        next_name = d.find_xpath('//*[@id="gadgettable-right-gadgets"]/div[2]/div/div/div/div/div/b/a')
        if next_name:
            next_name = "当前地城 "+next_name.text
        else:
            return False, f"获取当前地城 失败, 无法地城时间"

        can_end = d.find_xpath('//*[@id="gadgettable-right-gadgets"]/div[2]/div/div/div/div/div/input')
        if can_end:
            reduce_time = d.find_name("reduce_dungeon_time")
            if reduce_time:
                end_time = " 已点击提前, 结束时间 "+reduce_time.get_attribute("value")
            can_end.click()

        return True, f"{next_name}{end_time}"

    def cancle_dungeon(self, group, ctx: EventContext):
            hero_id = getattr(self, f'hero_id_{group}')
            url = f'http://delta.world-of-dungeons.org/wod/spiel/dungeon/group.php?session_hero_id={hero_id}'
            d = driver.WodDriver.get_instance()
            if url != d.geturl():
                d.open(url)

            if not d.wait('//*[@id="gadgettable-right-gadgets"]/div[3]/div/div/div/div/div/div[1]/a/span'):
                return False, f"取消地城 失败, 页面超时"
            # if not d.wait('//*[@id="smarttabs__members_inner"]/p[7]'):
            #     return False, f"取消地城 失败, 页面超时"
            exec_ret = d.exce_js(base.rep_str['cancle_d'])
            return exec_ret, f"取消地城 {'成功' if exec_ret else '失败'}"
    
    def dungeon_state(self, group):
        return True, f"常规地城列表 {len(getattr(self, f'd_common_{group}'))} 个\n今日地城列表 {len(getattr(self, f'd_today_{group}'))} 个\n明日地城列表 {len(getattr(self, f'd_tomorrow_{group}'))} 个\n"
    
    def get_player(self, group):
        return True, '\n'.join(f'{hero_id}-{name}' for hero_id, name in heros[group].items())

    def dodungeon(self, ctx: EventContext):
        curTick = time.perf_counter()
        msg = ctx.event.text_message
        group = ctx.event.launcher_id
        if not group or group == 0:
            group = groups[1]
        d_common = getattr(self, f'd_common_{group}')
        if getattr(self, f'hero_lv_{group}') == 0:
            self.calc_lv(group, ctx, True)
        if not d_common:
            self.update_dungeon(group, ctx)
        # 消息处理逻辑
        command_map = {
        "更新地城": lambda: self.update_dungeon(group, ctx, True),
        "常规地城": lambda: self.reply_common(group, ctx),
        "今日地城": lambda: self.reply_today(group, ctx),
        "明日地城": lambda: self.reply_tomorrow(group, ctx),
        "地城状态": lambda: self.dungeon_state(group),
        "当前地城": lambda: self.cur_dungeon(group, ctx),
        "取消地城": lambda: self.cancle_dungeon(group, ctx),
        "等级": lambda: self.get_lv(group, ctx),
        "更新等级": lambda: self.calc_lv(group, ctx, False),  # 添加第三个参数
        "玩家列表": lambda: self.get_player(group),
        }

        if msg in command_map:
            return command_map[msg]()

        ret = re.match(r'切 (.*)', msg)
        if ret:
            name = ret.group(1)
            self.ap.logger.info("dungeon TEST, {}, {}, name{}".format(ctx.event.sender_id, msg, name))
            d_id = 0
            d_today = getattr(self, f'd_today_{group}')
            d_id = d_common.get(name) or d_today.get(name) or getattr(self, f'd_tomorrow_{group}').get(name)
            if d_id is None:
                return False, "地城 {} 不可达啊, 操作耗时: {:.2f}".format(name, time.perf_counter() - curTick)
            hero_id = getattr(self, f'hero_id_{group}')
            url = f'http://delta.world-of-dungeons.org/wod/spiel/dungeon/group.php?session_hero_id={hero_id}'
            d = driver.WodDriver.get_instance()
            if url != d.geturl():
                d.open(url)

            if not d.wait('//*[@id="gadgettable-right-gadgets"]/div[3]/div/div/div/div/div/div[1]/a/span'):
                return False, f"切换 {name} 失败, 页面超时"
            # if not d.wait('//*[@id="smarttabs__members_inner"]/p[7]'):
            #     return False, f"切换 {name} 失败, 页面超时"
            js_code = base.rep_str['d1'] + f"searchParams.set(`visit[{d_id}]`, '探索');" + base.rep_str['d2']
            exec_ret = d.exce_js(js_code)
                
            # d.wait('//*[@id="gadgettable-right-gadgets"]/div[2]/div/div/div/div/div/b/a')
            time.sleep(2)
            end_time = ""
            if exec_ret:
                if d.find_xpath('//*[@id="gadgetNextdungeonTime"]'):
                    end_time = " 结束时间:" + d.find_xpath('//*[@id="gadgetNextdungeonTime"]').text
            next_name = d.find_xpath('//*[@id="gadgettable-right-gadgets"]/div[2]/div/div/div/div/div/b/a')
            count = 0
            while not next_name and count < 10:
                # time.sleep(1)
                next_name = d.find_xpath('//*[@id="gadgettable-right-gadgets"]/div[2]/div/div/div/div/div/b/a')

            can_end = d.find_xpath('//*[@id="gadgettable-right-gadgets"]/div[2]/div/div/div/div/div/input')
            if can_end:
                reduce_time = d.find_name("reduce_dungeon_time")
                if reduce_time:
                    end_time = " 已点击提前, 结束时间 "+reduce_time.get_attribute("value")
                can_end.click()

            return exec_ret, f"切换 {name} {'成功' if exec_ret else '失败'}{end_time}"

        return True, ""
    # 异步初始化
    async def initialize(self):
        pass

    # 当收到个人消息时触发
    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        curTick = time.perf_counter()
        ret , strs = self.dodungeon(ctx)
        # 阻止该事件默认行为（向接口获取回复）
        if strs != "":
            ctx.add_return("reply", ["{}, 操作耗时: {:.2f}".format(strs, time.perf_counter() - curTick)])
        ctx.prevent_default()

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        curTick = time.perf_counter()
        ret , strs = self.dodungeon(ctx)
        # 阻止该事件默认行为（向接口获取回复）
        if strs != "":
            ctx.add_return("reply", ["{}, 操作耗时: {:.2f}".format(strs, time.perf_counter() - curTick)])
        ctx.prevent_default()


    # 插件卸载时触发
    def __del__(self):
        pass
