from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import re
import csv
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote

from plugins.base.main import getCookie, getPostID

Sets = {}
# 注册插件
@register(name="have", description="查询宝库", version="0.1", author="x")
class MyPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        with open('sets.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                Sets[row[0]] = row[1]
        
        pass

    def doHave(self, ctx: EventContext):
        admin=0
        group=0
        if ctx.event.launcher_id != group and ctx.event.sender_id != admin:
            ctx.add_return("reply", [r'暂不支持跨群have'])
            return
        curTick = time.perf_counter()
        msg = ctx.event.text_message
        if msg == "have" or msg == "havei" or msg == "haves":
            ctx.add_return("reply", [r'组装链接格式: #havei 物品 或 #haves 套装名'])

        ret = re.match(r'have(2*)([is]) (.*)', msg)
        if ret:
            group = ret.group(1)
            type = ret.group(2)
            name = ret.group(3)
            count = 0

            self.ap.logger.info("have TEST, {}, {}, type{}, name{}, group{}".format(ctx.event.sender_id, msg, type, name, group))
            # 定义请求的 URL
            url = 'https://delta.world-of-dungeons.org/wod/spiel/hero/items.php?session_hero_id=0'
            # 定义请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'en,zh;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': getCookie(),
                'Host': 'delta.world-of-dungeons.org',
                'Origin': 'https://delta.world-of-dungeons.org',
                'Referer': 'https://delta.world-of-dungeons.org/wod/spiel/hero/items.php?view=groupcellar&session_hero_id=0',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Sec-CH-UA': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
                'Sec-CH-UA-Mobile': '?0',
                'Sec-CH-UA-Platform': '"Windows"',
            }
            # 定义要发送的数据
            data = {
                'session_hero_id':'',
                'wod_post_id':getPostID(),
                'wod_post_world':'CD',
                'klasse_id':'26',
                'klasse_name':'',
                'rasse_id':'8',
                'rasse_name':'',
                'gruppe_id':'',
                'gruppe_name':'',
                'clan_id':'',
                'clan_name':'',
                'stufe':'40',
                'heldenname':'',
                'spielername':'',
                'view':'groupcellar',
                'ITEMS_GROUPCELLAR_SORT_DIR':'ASC',
                'ITEMS_GROUPCELLAR_SORT_COL':'2',
                'ITEMS_GROUPCELLAR_PAGE':'1',
                'item_4name':'',
                'profile_data_item_4_profile_data':'HogNB0ny8I%2FFjaOg6FXrzZvwI0A1hZgI77jjRYoCRE1HuKQHl03uXQrDKEBJV1E%2FWgJhVic03ckalvZpFsbcSInxENF6pamLCvRdeYoi3CcM46bnZzcF8ln6yysSfEK7',
                'callback_js_code_item_4_callback_js_code':'m75eaKG1Bhz6dM0yUcEfULuntx4ML5jBgaT2mB0CB2hCtl3bNyFNmpO6xcKrr46PnasqZHSsfhaVVNCMPUWFu7QrinmlRL2n7hU7vJhSaxSjMgc9OI5U7zw2rlpLvDU2VRTJC7BrTcmNplCXzwU47KRPXaA%2BEWzvejCY842oiow%3D',
                'item_4hero_class':'0',
                'item_4hero_race':'0',
                'item_4location':'',
                'item_4unique':'',
                'item_4bonus_attr':'NULL',
                'item_4item_class':'0',
                'item_4any_skill':'0',
                'item_4skill':'',
                'item_4any_skillclass':'0',
                'item_4set':'0',
                'item_4item_condition':'0',
                'item_4sockets':'NULL',
                'item_4item_conditionMax':'6',
                'item_4usage_item':'',
                'item_4hero_level_enabled_posted':'1',
                'item_4hero_level':'40',
                'item_4hero_level_stored':'40',
                'item_4group_item':'',
                'item_4attribute_name':'eff_at_st',
                'item_4attribute_value':'',
                'item_4owner':'',
                'item_4profile_id':'0',
                'item_4is_open':'1'
            }
            if group == '2':
                data['session_hero_id'] = '',
                data['wod_post_id'] = getPostID(),
                data['wod_post_world'] = 'CD',
                data['klasse_id'] = '0',
                data['klasse_name'] = '',
                data['rasse_id'] = '0',
                data['rasse_name'] = '',
                data['gruppe_id'] = '',
                data['gruppe_name'] = '',
                data['stufe'] = '30',
                data['heldenname'] = '',
                data['item_4hero_level'] = '30',
                data['item_4hero_level_stored'] = '0',
                
                self.ap.logger.info("have, set daata ret {}, ".format(ctx.event.sender_id))
            else:
                data['pay_from_group_cash_box'] = '0',
                data['put_purchases_to'] = 'go_lager',
            

            if type == 's':
                id = 0
                if name in Sets:
                    id = Sets[name]
                else:
                    ctx.add_return("reply", ["{} 并不是套装, 操作耗时: {:.2f} {}团".format(
                        name, time.perf_counter() - curTick, 2 if group==2 else 1)])
                    return
                data['item_4set'] = str(id)
                resp = requests.post(url, headers=headers, data=data, timeout=30)

                str_end = '耗时:{}, {}团'.format(time.perf_counter() - curTick, 2 if group=='2' else 1)
                if resp.status_code != 200:
                    ctx.add_return("reply", ["套装 [set:{}] 查询出错, 操作{}, code {}".format(name, str_end, resp.status_code)])
                    return
                resp.encoding = 'utf-8'  # 或者使用 response.apparent_encoding
                soup = BeautifulSoup(resp.text, 'html.parser')
                ct_class = soup.find('table', class_='content_table')
                if ct_class==None:
                    self.ap.logger.info("have, request ret {}, 2, {}".format(ctx.event.sender_id, str_end))
                    logout = soup.find('title')
                    if logout == None:
                        ctx.add_return("reply", ["在宝库中查询物品 [item:{}] 失败, 可能cookie过期了, {}".format(name, str_end)])
                        return

                    ctx.add_return("reply", ["在宝库中查询物品 [item:{}] 失败, 可能cookie过期了, {}, message: {}".format(name, str_end, logout.text)])
                    return

                tbody = ct_class.find('tbody')
                rows = tbody.find_all('tr')

                noSet = tbody.find_all('p', class_ = 'message_success')
                if noSet:
                    ctx.add_return("reply", ["宝库中没有套装 [set:{}], 操作{}".format(name, str_end)])
                    self.ap.logger.info("have, request ret {}, {},no item???  link{}\n rows:{}".format(ctx.event.sender_id, str_end, [link.text for link in noSet], [link.text for link in rows]))
                else:
                    body_detail = '\n部件:\n'
                    for row in rows:
                        count = count+1
                        cells = row.find_all('td nowarp')
                        for cell in cells:
                            links = cell.find_all('a')
                            self.ap.logger.info("have, request ret {}, {}, link{}".format(ctx.event.sender_id, str_end, [link.text for link in links]))

                        detail = row.text
                        # self.ap.logger.info("have, request ret {}, 一件物品{}c".format(ctx.event.sender_id, detail.replace("\n","")))
                        if group=='2':
                            sre = re.match(r'(.*!) *.*宝库', detail.replace("\n",""))
                            if sre:
                                body_detail = body_detail + sre.group(1) +'\n'
                            else:
                                self.ap.logger.info("have, 2 group cant re!!!! ret {}, {}, rep {}, raw[]{}".format(ctx.event.sender_id, str_end, detail.replace("\n",""), [row.text]))
                                body_detail = ''
                        else:
                            sre = re.match(r'(.*!) *(.*)仓库团队', detail.replace("\n",""))
                            if sre:
                                # self.ap.logger.info("have, request ret {}, 一件物品{}, zz{}".format(ctx.event.sender_id, row.text, sre.group()))
                                body_detail = body_detail + sre.group(1) + " " + sre.group(2)+'\n'
                                # self.ap.logger.info("have, request ret {}, {}".format(ctx.event.sender_id, body_detail))
                            else:
                                self.ap.logger.info("have, cant re!!!! ret {}, {}, {}".format(ctx.event.sender_id, str_end, [row.text]))
                                body_detail = ''
                            
                            # self.ap.logger.info("have, request ret {}, {}".format(ctx.event.sender_id, [(cell.text) for cell in rows]))
                            # self.ap.logger.info("have, request ret {}, 套装{}, 件数{}".format(ctx.event.sender_id, name, count))


                    ctx.add_return("reply", ["套装 [set:{}] 宝库中有 {} 件, 操作{}, {}".format(name, count, str_end, body_detail)])
            elif type == 'i':
                data['item_4name'] = quote(name)
                data['item_4name'] = (name)
                resp = requests.post(url, headers=headers, data=data, timeout=30)
                str_end = '耗时:{}, {}团'.format(time.perf_counter() - curTick, 2 if group=='2' else 1)


                resp.encoding = 'utf-8'  # 或者使用 response.apparent_encoding
                soup = BeautifulSoup(resp.text, 'html.parser')
                # self.ap.logger.info("have, request ret {}, 1, {}".format(ctx.event.sender_id, soup))
                resp.encoding = 'utf-8'  # 或者使用 response.apparent_encoding
                ct_class = soup.find('table', class_='content_table')
                if ct_class==None:
                    self.ap.logger.info("have, if ct_class == None, request ret {}, 2".format(ctx.event.sender_id))
                    logout = soup.find('title')
                    if logout == None:
                        ctx.add_return("reply", ["在宝库中查询物品 [item:{}] 失败, 可能cookie过期了, {}".format(name, str_end)])
                        return

                    ctx.add_return("reply", ["在宝库中查询物品 [item:{}] 失败, 可能cookie过期了, {}, message: {}".format(name, str_end, logout.text)])
                    return

                tbody = ct_class.find('tbody')
                # if tbody == None:
                #     self.ap.logger.info("have, request ret {}, 3".format(ctx.event.sender_id))
                #     return
                rows = tbody.find_all('tr')
                noSet = tbody.find_all('p', class_ = 'message_success')
                if noSet:
                    for link in rows:
                        if link.text == '请输入您要搜索的内容，然后点击搜索.':
                            ctx.add_return("reply", ["在宝库中查询物品 [item:{}] 失败, cookie过期了, {}".format(name, str_end)])

                    ctx.add_return("reply", ["宝库中没有物品 [item:{}], 操作{}".format(name, str_end)])
                    self.ap.logger.info("have, if noSet  request ret {}, {} {}".format(ctx.event.sender_id, str_end, [link.text for link in rows]))
                else:
                    for row in rows:
                        count = count+1
                        cells = row.find_all('td nowarp')
                        for cell in cells:
                            links = cell.find_all('a')
                            # self.ap.logger.info("have, request ret {}, {}".format(ctx.event.sender_id, [link.text for link in links]))

                        # self.ap.logger.info("have, request ret {}, 套装{}, 件数{}".format(ctx.event.sender_id, name, count))

                    ctx.add_return("reply", ["物品 [item:{}] 宝库中有 {} 件, 操作{}".format(name, count,str_end)])
            # with open('soup.pkl', 'wb') as f:
            #     pickle.dump(soup, f)
            # self.ap.logger.info("have, request ret {}, {}".format(ctx.event.sender_id, resp.text))


    # 异步初始化
    async def initialize(self):
        pass

    # 当收到个人消息时触发
    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message
        if msg == "have" or msg == "havei" or msg == "haves":
            ctx.add_return("reply", [r'组装链接格式: #havei 物品 或 #haves 套装名'])

        ret = re.match(r'have(2*)([is]) (.*)', msg)
        if ret:
            self.doHave(ctx)
            # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_default()

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message
        if msg == "have" or msg == "havei" or msg == "haves":
            ctx.add_return("reply", [r'组装链接格式: #havei 物品 或 #haves 套装名'])

        ret = re.match(r'have(2*)([is]) (.*)', msg)
        if ret:
            self.doHave(ctx)
            # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_default()


    # 插件卸载时触发
    def __del__(self):
        pass
