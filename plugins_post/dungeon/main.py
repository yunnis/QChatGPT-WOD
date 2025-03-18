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

from plugins.base.main import getCookie, getPostID, set_cookie, set_pid, groups

hero_ids = (wod_hero_id, wod_hero_id)

#ctx.add_return("reply", f'test target {ctx.event.launcher_id}')
# setattr(self, f'xx_{num}, None)
#(getattr(self, f'xx_{num}'))
base_head = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en,zh;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    # 'Cookie': Cookie,
    'Host': 'delta.world-of-dungeons.org',
    # 每个请求自己填写
    # 'Referer': 'https://delta.world-of-dungeons.org/wod/spiel/dungeon/dungeon.php?session_hero_id=000',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}
base_datas = {
    # 请求根据group获取
    'spielername': '',
    'TABLE_DEFAULT_SORT_DIR': 'DESC',
    'TABLE_DEFAULT_SORT_COL': '7',
    'TABLE_DEFAULT_PAGE': '1',
    'dungeon_1name': '',
    'profile_data_dungeon_1_profile_data': 'HogNB0ny8I%2FFjaOg6FXrzZvwI0A1hZgI77jjRYoCRE3TJQgF4vgCjZAkyYaqnVkaUCz5Aj1abQ4Ia2kvccXiWcIRV6oVff3elHx6QuFSULUbPCjalPU2%2BypnkRGdG62g',
    'callback_js_code_dungeon_1_callback_js_code': '9hAUpnwetF8TrxnkIxgBdD27k4isavkaEEd%2FPwhJTLL8yf4MvBsSYedcxPRse51t2x6Aw2bcXKHHlyCszAStN2nnub0CncNJMDrZQePru5mpXW3It99S%2FD%2BJypTOewMQ%2FT9%2BeXLlhJZ7vK%2Bj9IAKgKVS%2BEFJPGzy61GBgu60fBk%3D',
    'dungeon_1level': '',
    'dungeon_1level_to': '',
    'dungeon_1level_allowed': '',
    'dungeon_1level_allowed_to': '',
    'dungeon_1groupLevel': '40',
    'dungeon_1profile_id': '0',
    'dungeon_1is_open': '1',
    'TABLE_DEFAULT_PSNR%5B1%5D': '20',
    'TABLE_DEFAULT_PSNR%5B2%5D': '20',
    'TABLE_DATED_SORT_DIR': 'ASC',
    'TABLE_DATED_SORT_COL': '14',
    'TABLE_DATED_PAGE': '1',
    'dungeon_2name': '',
    'profile_data_dungeon_2_profile_data': 'HogNB0ny8I%2FFjaOg6FXrzZvwI0A1hZgI77jjRYoCRE26Yi3zTNw4kxlf3EBWtEk1b6aVuW%2BFUuN8kSMRggg8h3JkxoL2NsUxavZXWRdyOxUUEMX5AKRE3eAUHOs1WJk3',
    'callback_js_code_dungeon_2_callback_js_code': 'hjeqjpM%2BqZ3O91mfrGQpvhGIqpJEtjGwgXlmEmXfIQzBrxMpR69Guzy7%2B7UjXgADJMzqeXDJhCUPVMr4x2KfpOKujjttFf22twLrAnOMemRyC0FkOn1zx6YBUufUkR7Ckg4pf2y%2F2z74zxDx8svUS6Kwihgpc54Xeb1xFKyGmQQ%3D',
    'dungeon_2level': '',
    'dungeon_2level_to': '',
    'dungeon_2level_allowed': '',
    'dungeon_2level_allowed_to': '',
    'dungeon_2groupLevel': '40',
    'dungeon_2profile_id': '0',
    'dungeon_2is_open': '1',
    'TABLE_DATED_PSNR%5B1%5D': '20',
    'TABLE_DATED_PSNR%5B2%5D': '20'
}
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

    def _get_datas(self, group):
        if group == groups[0]:
            return {
                'session_hero_id': '',
                'wod_post_id': getPostID(),
                'wod_post_world': 'CD',
                'pay_from_group_cash_box': '0',
                'put_purchases_to': 'go_lager',
                'klasse_id': '26',
                'klasse_name': '',
                'rasse_id': '8',
                'rasse_name': '',
                'gruppe_id': '',
                'gruppe_name': '',
                'clan_id': '',
                'clan_name': '',
                'stufe': str(getattr(self, f'hero_lv_{group}')),
                'heldenname': '',
            }
        elif group == groups[1]:
            return {
                'session_hero_id': '',
                'wod_post_id': getPostID(),
                'wod_post_world': 'CD',
                'klasse_id': '3',
                'klasse_name': '',
                'rasse_id': '8',
                'rasse_name': '',
                'gruppe_id': '',
                'gruppe_name': '',
                'clan_id': '',
                'clan_name': '',
                'stufe': str(getattr(self, f'hero_lv_{group}')),
                'heldenname': ''
            }
        else:
            return None

    def _init_dungeon(self, json_d, group, hero_lv):
        d_common = getattr(self, f'd_common_{group}')
        d_today = getattr(self, f'd_today_{group}')
        d_tomorrow = getattr(self, f'd_tomorrow_{group}')
        min_lv = getattr(self, f'min_lv_{group}')
        for d in json_d['data']:
            if d['type']=='P' and d['minLevel'] <= min_lv and d['maxLevel'] >= hero_lv:
                d_common[d['name']] = d['sysId']
            elif d['type']=='L' and d['minLevel'] <= min_lv and d['maxLevel'] >= hero_lv:
                start_time = datetime.fromisoformat(d['startTime'])
                now = datetime.now()
                if start_time < now < datetime.fromisoformat(d['endTime']):
                    d_today[d['name']] = d['sysId']
                elif now < start_time < now+timedelta(hours=24):
                    d_tomorrow[d['name']] = d['sysId']

    def update_dungeon(self, group, ctx: EventContext):
        today_str = datetime.now().strftime("%Y%m%d")
        tick_name = f'test_{group}'
        d_common = getattr(self, f'd_common_{group}')
        d_today = getattr(self, f'd_today_{group}')
        d_tomorrow = getattr(self, f'd_tomorrow_{group}')
        if os.path.exists('dungeons.json'):
            with open('dungeons.json', 'r+') as json_file:
                d_j = json.load(json_file)
                if d_j['time'] == today_str:
                    if not d_j.get(tick_name):
                        d_j[tick_name] = time.time()
                        self.ap.logger.info("dont have tick, init tick, json name {}, value {}".format(tick_name, d_j[tick_name]))
                    is_next_day = self._check_timestamp((d_j[tick_name]))
                    if not d_common or is_next_day:
                        d_j[tick_name] = time.time()
                        d_common.clear()
                        d_today.clear()
                        d_tomorrow.clear()
                        self._init_dungeon(d_j, group, getattr(self, f'hero_lv_{group}'))
                        self.ap.logger.critical("update by local file dungeon {}, is next day {}, today size {}".format(today_str, is_next_day, len(d_today)))
                        with open('dungeons.json', 'w') as json_file:
                            json.dump(d_j, json_file, ensure_ascii=False, indent=4)  # indent=4 让 JSON 文件更美观
                    return
                json_file.seek(0)
                json_file.truncate()

        curTick = time.perf_counter()
        headers = {
            "Content-Type": "application/json",
        }
        resp = requests.post('https://www.christophero.xyz/wod/dungeon/listCommon', json=headers)
        if resp.status_code != 200:
            self.ap.logger.critical("cnat update dungeon {}".format( today_str))
            return
        resp.encoding = 'utf-8'  # 或者使用 response.apparent_encoding
        dungeons = json.loads(resp.text)
        if dungeons['code'] == 200 and dungeons['msg']=='请求成功':
            dungeons['time'] = today_str
            dungeons[tick_name] = time.time()
            self.ap.logger.critical("update by wiki web dungeon {}".format( today_str))
            with open('dungeons.json', 'w') as json_file:
                json.dump(dungeons, json_file, ensure_ascii=False, indent=4)  # indent=4 让 JSON 文件更美观
        d_common.clear()
        d_today.clear()
        d_tomorrow.clear()
        self._init_dungeon(dungeons, group, getattr(self, f'hero_lv_{group}'))

        ctx.prevent_default()

    def reply_common(self, group, ctx: EventContext):
        self.update_dungeon(group,ctx)
        ctx.add_return("reply", ["常规地城列表\n{}".format("\n".join(e for e in getattr(self, f'd_common_{group}').keys()))])

    def reply_today(self, group, ctx: EventContext):
        self.update_dungeon(group,ctx)
        ctx.add_return("reply", ["今日地城列表\n{}".format("\n".join(e for e in getattr(self, f'd_today_{group}').keys()))])
    
    def reply_tomorrow(self, group, ctx: EventContext):
        self.update_dungeon(group,ctx)
        ctx.add_return("reply", ["明日地城列表\n{}".format("\n".join(e for e in getattr(self, f'd_tomorrow_{group}').keys()))])

    def cur_dungeon(self, group, ctx: EventContext):
        curTick = time.perf_counter()
        hero_id = getattr(self, f'hero_id_{group}')
        url = f'https://delta.world-of-dungeons.org/wod/spiel/dungeon/dungeon.php?session_hero_id={hero_id}'
        headers = {
            'Cookie': getCookie(),
            'Referer': f'https://delta.world-of-dungeons.org/wod/spiel/dungeon/dungeon.php?session_hero_id={hero_id}',
        }
        headers.update(base_head)
        resp = requests.get(url, headers=headers)
        resp.encoding = 'utf-8'  # 或者使用 response.apparent_encoding
        if resp.status_code == 200:
            with open('get_cur_d.html', 'w', encoding='utf-8') as file:
                file.write(resp.text)  # 如果是二进制内容，可以使用 response.content
            soup = BeautifulSoup(resp.text, 'html.parser')

            cur_d = ""
            cur_d_info = soup.find(text=re.compile("下一个地城"))
            if cur_d_info:
                cur_d = cur_d_info.find_next('b').text
            else:
                ctx.add_return("reply", ["获取当前地城 失败, 解析地城名错误 操作耗时: {:.2f}".format(time.perf_counter() - curTick)])
                return

            end_time = ""
            end_time_info = soup.find(text=re.compile("冒险将结束于"))
            if end_time_info:
                end_time = end_time_info.split("：")[-1].strip()
            else:
                ctx.add_return("reply", ["获取当前地城 失败, 解析完成时间错误 操作耗时: {:.2f}".format(time.perf_counter() - curTick)])

            visit_str = "无需提前"
            visit_now_info = soup.find('input', {'name':'visit_now'})
            if visit_now_info:
                visit_now_text = visit_now_info['value']
                self.ap.logger.info("地城返回 解析提前结束 , {}, v_info  {}, q_v {}".format(ctx.event.sender_id, visit_now_text, quote(visit_now_text)))
                vdata = {
                    'visit_now': quote(visit_now_text),
                }
                vdata.update(base_datas)
                vdata.update(self._get_datas(group))

                vresp = requests.post(url, headers=headers, data=vdata)
                if resp.status_code == 200:
                    self.ap.logger.error(f"切换地城返回 提前结束成功 , {ctx.event.sender_id}, v_info  {visit_now_info}")
                    visit_str = visit_now_text
            elif visit_now_info != None:
                self.ap.logger.error("切换地城返回 解析提前结束失败 , {}, v_info  {}".format(ctx.event.sender_id, visit_now_info))

            self.ap.logger.info("cur  dungeon , {}, time  {}".format(ctx.event.sender_id, end_time))
            ctx.add_return("reply", ["当前地城 {} , 结束时间 {}, {} 操作耗时: {:.2f}".format(cur_d, end_time, visit_str, time.perf_counter() - curTick)])
            return
        else:
            ctx.add_return("reply", ["获取当前地城 失败,  操作耗时: {:.2f}".format(time.perf_counter() - curTick)])

    def cancle_dungeon(self, group, ctx: EventContext):
        curTick = time.perf_counter()
        hero_id = getattr(self, f'hero_id_{group}')
        url = f'https://delta.world-of-dungeons.org/wod/spiel/dungeon/dungeon.php?session_hero_id={hero_id}'
        headers = {
            'Cookie': getCookie(),
            'Origin': 'https://delta.world-of-dungeons.org',
            'Referer': f'https://delta.world-of-dungeons.org/wod/spiel/dungeon/dungeon.php?session_hero_id={hero_id}',
        }
        headers.update(base_head)
        data = {
            'unvisit': '',
        }
        data.update(base_datas)
        data.update(self._get_datas(group))
        resp = requests.post(url, headers=headers, data=data)
        resp.encoding = 'utf-8'  # 或者使用 response.apparent_encoding
        if resp.status_code == 200:
            with open('cancle_d.html', 'w', encoding='utf-8') as file:
                file.write(resp.text)  # 如果是二进制内容，可以使用 response.content
        
            ctx.add_return("reply", ["取消成功 操作耗时: {:.2f}".format( time.perf_counter() - curTick)])
            return
        else:
            ctx.add_return("reply", ["获取当前地城 失败,  操作耗时: {:.2f}".format(time.perf_counter() - curTick)])

    def open_item(self, group, ctx: EventContext):
        curTick = time.perf_counter()
        hero_id = getattr(self, f'hero_id_{group}')
        url = f'https://delta.world-of-dungeons.org/wod/spiel/hero/items.php?view=groupcellar&session_hero_id={hero_id}'
        headers = {
            'Cookie': getCookie(),
            'Referer': f'https://delta.world-of-dungeons.org/wod/spiel/hero/items.php?view=groupcellar&session_hero_id={hero_id}',
        }
        headers.update(base_head)
        resp = requests.get(url, headers=headers)
        resp.encoding = 'utf-8'  # 或者使用 response.apparent_encoding
        if resp.status_code == 200:
            with open('open_item.html', 'w', encoding='utf-8') as file:
                file.write(resp.text)  # 如果是二进制内容，可以使用 response.content
            ctx.add_return("reply", ["开宝库 成功 操作耗时: {:.2f}".format( time.perf_counter() - curTick)])
            cookie = resp.cookies
            if cookie:
                set_cookie(self, '; '.join([f'{c.name}={c.value}' for c in cookie]))
            soup = BeautifulSoup(resp.text, 'html.parser')
            form = soup.find('form', {'name': 'the_form'})
            if form:
                wod_post_id_input = form.find('input', {'name': 'wod_post_id'})
                if wod_post_id_input:
                    set_pid(self, wod_post_id_input['value'])
            return
        else:
            ctx.add_return("reply", ["开宝库 失败,  操作耗时: {:.2f}".format(time.perf_counter() - curTick)])

    def get_lv(self, group, ctx: EventContext):
        cacha_lv = getattr(self, f'hero_lv_{group}')
        min_lv = getattr(self, f'min_lv_{group}')
        if cacha_lv != 0:
            ctx.add_return("reply", [f'缓存等级{cacha_lv}, 最小等级 {min_lv}'])
            return
        self.calc_lv(group, ctx, False)

    def calc_lv(self, group, ctx: EventContext, is_init):
        curTick = time.perf_counter()
        hero_id = getattr(self, f'hero_id_{group}')
        url = f'https://delta.world-of-dungeons.org/wod/spiel/dungeon/group.php?session_hero_id={hero_id}'
        headers = {
            'Cookie': getCookie(),
            'Referer': f'https://delta.world-of-dungeons.org/wod/spiel/settings/heroes.php?session_hero_id={hero_id}',
        }
        headers.update(base_head)
        resp = requests.get(url, headers=headers)
        resp.encoding = 'utf-8'  # 或者使用 response.apparent_encoding
        if resp.status_code == 200:
            with open('get_lv.html', 'w', encoding='utf-8') as file:
                file.write(resp.text)  # 如果是二进制内容，可以使用 response.content
            # ctx.add_return("reply", ["获取等级 成功 操作耗时: {:.2f}".format( time.perf_counter() - curTick)])
            cacha_lv = getattr(self, f'hero_lv_{group}')
            soup = BeautifulSoup(resp.text, 'html.parser')
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
            else:
                self.ap.logger.info(f'total {total_lv}, count eq 0, cant calc lv')
                if not is_init:
                    ctx.add_return("reply", [f"获取等级 失败, 总等级 {total_lv}, 人数 {count}, 缓存等级 {cacha_lv}, 最小等级 {min_lv}, 操作耗时: {format(time.perf_counter() - curTick):.2}"])
            return
        else:
            if not is_init:
                ctx.add_return("reply", ["获取等级 失败,  操作耗时: {}".format(time.perf_counter() - curTick)])


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

        if msg == "更新地城":
            self.update_dungeon(group, ctx)
            return
        elif msg== "常规地城":
            self.reply_common(group, ctx)
            return
        elif msg== "今日地城":
            self.reply_today(group, ctx)
            return
        elif msg == "当前地城":
            self.cur_dungeon(group, ctx)
            return
        elif msg== "明日地城":
            self.reply_tomorrow(group, ctx)
            return
        elif msg == "取消地城":
            self.cancle_dungeon(group, ctx)
        elif msg == "包":
            self.open_item(group, ctx)
        elif msg == "等级":
            self.get_lv(group, ctx)
        elif msg == "更新等级":
            self.calc_lv(group, ctx, False)

        ret = re.match(r'切 (.*)', msg)
        if ret:
            name = ret.group(1)
            self.ap.logger.info("dungeon TEST, {}, {}, name{}".format(ctx.event.sender_id, msg, name))
            d_id = 0
            d_today = getattr(self, f'd_today_{group}')
            if name in d_common:
                d_id = d_common[name]
            elif name in d_today:
                d_id = d_today[name]
            else:
                ctx.add_return("reply", ["地城 {} 不可达啊, 操作耗时: {:.2f}".format(name, time.perf_counter() - curTick)])
                return
            hero_id = getattr(self, f'hero_id_{group}')
            url = f'https://delta.world-of-dungeons.org/wod/spiel/dungeon/dungeon.php?session_hero_id={hero_id}'
            # 定义请求头
            # headers ={
            #     'Cookie': getCookie(),
            #     # 'Origin': 'https://delta.world-of-dungeons.org',
            #     'Referer': f'https://delta.world-of-dungeons.org/wod/spiel/dungeon/dungeon.php?session_hero_id={hero_id}',
            # }
            # headers.update(base_head)
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en,zh;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Content-Length": "1845",
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": getCookie(),
                "Host": "delta.world-of-dungeons.org",
                "Origin": "https://delta.world-of-dungeons.org",
                "Referer": "https://delta.world-of-dungeons.org/wod/spiel/dungeon/dungeon.php?session_hero_id=0",
                "Sec-CH-UA": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                "Sec-CH-UA-Mobile": "?0",
                "Sec-CH-UA-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
            }
            # 定义要发送的数据
            data = {
                'session_hero_id': str(hero_id),
                'wod_post_id': getPostID(),
                'wod_post_world': 'CD',
                'klasse_id': '3',
                'klasse_name': '',
                'rasse_id': '8',
                'rasse_name': '',
                'gruppe_id': '',
                'gruppe_name': '',
                'clan_id': '',
                'clan_name': '',
                'stufe':  str(getattr(self, f'hero_lv_{group}')),
                'heldenname': '',
                'spielername': '',
                'TABLE_DEFAULT_SORT_DIR': 'DESC',
                'TABLE_DEFAULT_SORT_COL': '7',
                'TABLE_DEFAULT_PAGE': '1',
                'dungeon_1name': '',
                'profile_data_dungeon_1_profile_data': 'HogNB0ny8I%2FFjaOg6FXrzZvwI0A1hZgI77jjRYoCRE3TJQgF4vgCjZAkyYaqnVkaUCz5Aj1abQ4Ia2kvccXiWcIRV6oVff3elHx6QuFSULUbPCjalPU2%2BypnkRGdG62g',
                'callback_js_code_dungeon_1_callback_js_code': '9hAUpnwetF8TrxnkIxgBdD27k4isavkaEEd%2FPwhJTLL8yf4MvBsSYedcxPRse51t2x6Aw2bcXKHHlyCszAStN2nnub0CncNJMDrZQePru5mpXW3It99S%2FD%2BJypTOewMQ%2FT9%2BeXLlhJZ7vK%2Bj9IAKgKVS%2BEFJPGzy61GBgu60fBk%3D',
                'dungeon_1level': '',
                'dungeon_1level_to': '',
                'dungeon_1level_allowed': '',
                'dungeon_1level_allowed_to': '',
                'dungeon_1groupLevel': str(getattr(self, f'hero_lv_{group}')),
                'dungeon_1profile_id': '0',
                'dungeon_1is_open': '1',
                'TABLE_DEFAULT_PSNR%5B1%5D': '20',
                'visit%5B{}%5D'.format(d_id): '%E6%8E%A2%E7%B4%A2',
                'TABLE_DEFAULT_PSNR%5B2%5D': '20',
                'TABLE_DATED_SORT_DIR': 'ASC',
                'TABLE_DATED_SORT_COL': '14',
                'TABLE_DATED_PAGE': '1',
                'dungeon_2name': '',
                'profile_data_dungeon_2_profile_data': 'HogNB0ny8I%2FFjaOg6FXrzZvwI0A1hZgI77jjRYoCRE26Yi3zTNw4kxlf3EBWtEk1b6aVuW%2BFUuN8kSMRggg8h3JkxoL2NsUxavZXWRdyOxUUEMX5AKRE3eAUHOs1WJk3',
                'callback_js_code_dungeon_2_callback_js_code': 'hjeqjpM%2BqZ3O91mfrGQpvhGIqpJEtjGwgXlmEmXfIQzBrxMpR69Guzy7%2B7UjXgADJMzqeXDJhCUPVMr4x2KfpOKujjttFf22twLrAnOMemRyC0FkOn1zx6YBUufUkR7Ckg4pf2y%2F2z74zxDx8svUS6Kwihgpc54Xeb1xFKyGmQQ%3D',
                'dungeon_2level': '',
                'dungeon_2level_to': '',
                'dungeon_2level_allowed': '',
                'dungeon_2level_allowed_to': '',
                'dungeon_2groupLevel': str(getattr(self, f'hero_lv_{group}')),
                'dungeon_2profile_id': '0',
                'dungeon_2is_open': '1',
                'TABLE_DATED_PSNR%5B1%5D': '20',
                'TABLE_DATED_PSNR%5B2%5D': '20',
            }
            # data.update(self._get_datas(group))
            # data.update(base_datas)
            # data['dungeon_1groupLevel'] = str(getattr(self, f'hero_lv_{group}'))
            # data['dungeon_2groupLevel'] = str(getattr(self, f'hero_lv_{group}'))
            # data['visit%5B{}%5D'.format(d_id)] = '%E6%8E%A2%E7%B4%A2'
     
            self.ap.logger.info("dungeon TEST requessts info , {}, {}, url: {}\n cookie: {} \n data: {}".format(group, msg, url, headers, data))
            self.ap.logger.info("dungeon TEST hero id: {} \n cookie: {}\n postID: {}".format(hero_id, getCookie, getPostID))
            resp = requests.post(url, headers=headers, data=data)
            resp.encoding = 'utf-8'  # 或者使用 response.apparent_encoding
            if resp.status_code == 200:
                with open('output.html', 'w', encoding='utf-8') as file:
                    file.write(resp.text)  # 如果是二进制内容，可以使用 response.content

                soup = BeautifulSoup(resp.text, 'html.parser')
                cur_d = ""
                cur_d_info = soup.find(text=re.compile("下一个地城"))
                if cur_d_info:
                    cur_d = cur_d_info.find_next('b').text
                else:
                    self.ap.logger.error("切换地城返回 解析地城名失败 , {}, d_info  {}".format(ctx.event.sender_id, cur_d_info))

                end_time = ""
                end_time_info = soup.find(text=re.compile("冒险将结束于"))
                if end_time_info:
                    end_time = end_time_info.split("：")[-1].strip()
                else:
                    self.ap.logger.error("切换地城返回 解析完成时间失败 , {}, t_info  {}".format(ctx.event.sender_id, end_time_info))
                    return

                visit_str = "无需提前"
                visit_now_info = soup.find('input', {'name':'visit_now'})
                if visit_now_info:
                    visit_now_text = visit_now_info['value']
                    self.ap.logger.info("切换地城返回 解析提前结束 , {}, v_info  {}, q_v {}".format(ctx.event.sender_id, visit_now_text, quote(visit_now_text)))
                    vdata = {
                        'visit_now': quote(visit_now_text),
                    } 
                    data.update(base_datas)
                    data.update(self._get_datas(group))

                    vresp = requests.post(url, headers=headers, data=vdata)
                    if resp.status_code == 200:
                        self.ap.logger.error("切换地城返回 提前结束成功 , {}, v_info  {}".format(ctx.event.sender_id, visit_now_info))
                        visit_str = visit_now_text
                elif visit_now_info != None:
                    self.ap.logger.error("切换地城返回 解析提前结束失败 , {}, v_info  {}".format(ctx.event.sender_id, visit_now_info))


                self.ap.logger.info("change  dungeon , {}, time  {}".format(ctx.event.sender_id, end_time))
                ctx.add_return("reply", ["切换地城 {} 成功, 结束时间 {}, {}, 操作耗时: {:.2f}".format(cur_d, end_time, visit_str , time.perf_counter() - curTick)])
                return
            else:
                ctx.add_return("reply", ["切换地城 [{}] 失败拉, 操作耗时: {:.2f}, code {}".format(name, time.perf_counter() - curTick, resp.status_code)])

    # 异步初始化
    async def initialize(self):
        pass

    # 当收到个人消息时触发
    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        self.dodungeon(ctx)
        # 阻止该事件默认行为（向接口获取回复）
        ctx.prevent_default()

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        self.dodungeon(ctx)
        # 阻止该事件默认行为（向接口获取回复）
        ctx.prevent_default()


    # 插件卸载时触发
    def __del__(self):
        pass
