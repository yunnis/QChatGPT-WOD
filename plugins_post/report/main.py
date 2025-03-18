from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import requests
import time
import json
import os
import prettytable as pt
from bs4 import BeautifulSoup
import tabulate

from plugins.base.main import Cookie, PostID, groups, get_hero_id

base_head = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en,zh;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': Cookie,
    'Host': 'delta.world-of-dungeons.org',
    # 每个请求自己填写
    # 'Referer': 'https://delta.world-of-dungeons.org/wod/spiel/dungeon/dungeon.php?session_hero_id=0',
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
# 注册插件
@register(name="report", description="战报", version="0.1", author="x")
class MyPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        pass

    # 异步初始化
    async def initialize(self):
        pass

    def _get_list(self, group, ctx: EventContext):
        curTick = time.perf_counter()
        hero_id = get_hero_id(group)
        url = f'https://delta.world-of-dungeons.org/wod/spiel/dungeon/report.php?session_hero_id={hero_id}'
        headers = {
            'Referer': f'https://delta.world-of-dungeons.org/wod/spiel/dungeon/report.php?session_hero_id={hero_id}',
        }
        headers.update(base_head)
        resp = requests.get(url, headers=headers)
        resp.encoding = 'utf-8'  # 或者使用 response.apparent_encoding
        if resp.status_code == 200:
            with open(f'reportlist_{int(curTick)}.html', 'w', encoding='utf-8') as file:
                file.write(resp.text)  # 如果是二进制内容，可以使用 response.content
            soup = BeautifulSoup(resp.text, 'html.parser')
            table = soup.find('table', class_='content_table')
            if not table:
                ctx.add_return("reply", ["获取战报列表 失败, 没有战报或cookie失效, 操作耗时: {:.2f}".format( time.perf_counter() - curTick)])
                return

            report_entries = []
            report_table = pt.PrettyTable()
            report_table.field_names = ['ID', '地城', '日期']
            # 输出每个地城及其对应的 value
            num = 0
            for row in table.find_all('tr')[1:]:  # Skip the header row
                if num >= 5:
                    break
                num+=1
                cols = row.find_all('td')
                date = cols[0].get_text(strip=True)
                dungeon = cols[1].get_text(strip=True)
                
                # Find the hidden input to get the value
                hidden_input = cols[2].find('input', type='hidden')
                value = hidden_input['value'] if hidden_input else None

                report_entries.append({'ID': value, 'dungeon': dungeon, 'date': date})
                report_table.add_row([value, dungeon, date])

            # ret_str = '\n'.join(f"id:{e['value']}, D:{e['dungeon']:}, 时间:{e['date']} " for e in report_entries)
            ret_str = report_table.get_string()
            ret_str = tabulate.tabulate(report_entries, tablefmt="github", showindex="always")
            self.ap.logger.critical(ret_str)
            ctx.add_return("reply", ["获取战报列表 成功操作耗时: {:.2f}\n{}".format(time.perf_counter() - curTick, ret_str)])


            return
        else:
            ctx.add_return("reply", ["获取战报列表 失败 操作耗时: {:.2f}".format( time.perf_counter() - curTick)])

    def doReport(self, ctx):
        msg = ctx.event.text_message  # 这里的 event 即为 PersonNormalMessageReceived 的对象
        group = ctx.event.launcher_id
        fun = None
        match msg:
            case '战报列表':
                fun = self._get_list

        if fun != None:
            fun(group, ctx)
            ctx.prevent_default()

    # 当收到个人消息时触发
    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        self.doReport(ctx)

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        self.doReport(ctx)

    # 插件卸载时触发
    def __del__(self):
        pass
