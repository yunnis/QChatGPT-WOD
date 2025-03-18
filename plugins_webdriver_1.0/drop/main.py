from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import os
import re
import requests
from bs4 import BeautifulSoup
import time
import json

from urllib.parse import quote

import plugins.base.main as base

dungeons = {}

# 注册插件
@register(name="drop", description="掉落查询", version="0.1", author="x")
class MyPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        if os.path.exists('dungeon.json') and os.path.getsize('dungeon.json'):
            with open('dungeon.json', 'r+', encoding='utf-8') as json_file:
                json_d = json.load(json_file)
                for d in json_d:
                    dungeons[d['name']] = d['sysId']
        pass

    def dodrop(self, ctx: EventContext):
        curTick = time.perf_counter()
        msg = ctx.event.text_message
        group = ctx.event.launcher_id
        if msg == "drop" or msg == "d":
            ctx.add_return("reply", [r'组装链接格式: #drop 物品'])
        ret = re.match(r'drop (.*)', msg)
        if ret:
            name = ret.group(1)
            groupid = base.get_group_id(str(group))
            if dungeons.get(name):
                ctx.add_return("reply", [
                    "地城 {} 的掉落链接 https://www.christophero.xyz/groupDungeon/{}?groupId={}".format(name, quote(name), groupid)])
                return


            self.ap.logger.info("drop TEST, {}, {}, name{}".format(ctx.event.sender_id, msg, name))
            # 定义请求的 URL
            url = 'https://www.christophero.xyz/wod/item/dropAnalysis'
            # 定义请求头
            headers = {
                "Content-Type": "application/json"
            }
            # 定义要发送的数据
            data = {
                'serverName': 'delta',
                'name':  str(name),
                'groupId': groupid,
                'notExistInsert': 'false',
            }
 
            resp = requests.post(url, headers=headers, json=data)
            if resp.status_code != 200:
                ctx.add_return("reply", ["物品 [item:{}] 不存在, 操作耗时: {:.2f}, code {}".format(name, time.perf_counter() - curTick, resp.status_code)])
                return
            # resp.encoding = 'utf-8'  # 或者使用 response.apparent_encoding
            json_r = json.loads(resp.text)
            # self.ap.logger.info("reps json {}".format( json_r))
            if json_r['code'] == 404 or json_r['msg'] == '您所查询的道具不存在':
                ctx.add_return("reply", ['您所查询的道具 {} 不存在'.format(name)])
                return
            elif json_r['code'] == 200 and json_r['msg']=='请求成功':
                drop=''
                if json_r['data']['worldDrop']:
                    drop='\n世界'
                if json_r['data']['shop']:
                    drop+='\n市集购买'
                if json_r['data']['draw']:
                    drop=drop+"\n抽奖"
                if json_r['data']['obtain']:
                    drop=drop+"\n"+json_r['data']['obtain']
                for j_e in json_r['data']['dropList']:
                    drop=drop+"\n{}({}-{})".format(j_e['dungeonName'], j_e['minLevel'], j_e['maxLevel'])
                    if j_e['challenge'] != None:
                        drop=drop+"<挑战{}>".format(j_e['challenge'])
                    if j_e['certain'] == 1:
                        drop=drop+" 必出1个"
                    elif j_e['certain'] == 12:
                        drop=drop+" 人手1个"
                    if j_e['triggerItems']!= None:
                        drop=drop+" + [item:{}]".format(j_e['triggerItems'])
                    if j_e['note'] != None:
                        drop=drop+"\n{}".format(j_e['note'])
                ctx.add_return("reply", ['道具 [item:{}] 已掉落 {} 个\n获取途径:{}'.format(name, json_r['data']['count'], drop)])
                
            

    # 异步初始化
    async def initialize(self):
        pass

    # 当收到个人消息时触发
    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message
        if msg == "drop" or msg == "d":
            ctx.add_return("reply", [r'组装链接格式: #drop 物品'])
            ctx.prevent_default()
        ret = re.match(r'drop (.*)', msg)
        if ret:
            self.dodrop(ctx)
            # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_default()

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message
        if msg == "drop" or msg == "d":
            ctx.add_return("reply", [r'组装链接格式: #drop 物品'])
            ctx.prevent_default()
        ret = re.match(r'drop (.*)', msg)
        if ret:
            self.dodrop(ctx)
            # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_default()


    # 插件卸载时触发
    def __del__(self):
        pass
