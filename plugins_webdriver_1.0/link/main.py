from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
from urllib.parse import quote
import re

# 注册插件
@register(name="link", description="组装链接", version="0.1", author="x")
class MyPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        pass

    # 异步初始化
    async def initialize(self):
        pass

    # 当收到个人消息时触发
    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message  # 这里的 event 即为 PersonNormalMessageReceived 的对象
        self.ap.logger.debug("link , {}, {}".format(ctx.event.sender_id, msg))
        if msg == "link" or msg == "linki" or msg == "links" or msg == "l":
            self.ap.logger.debug("link 格式错误, {}, {}".format(ctx.event.sender_id, msg))
            ctx.add_return("reply", [r'组装链接格式: #linki 物品 或 #links 套装'])
            ctx.prevent_default()
        else:
            ret = re.match(r'link([is]) (.*)', msg)
            if ret:
                type = ret.group(1)
                name = ret.group(2)
                str_type = 'item'
                cn_type = '物品'
                if type == 'i':
                    str_type = 'item'
                    cn_type = '物品'
                elif type == 's':
                    str_type = 'set'
                    cn_type = '套装'

                # 输出调试信息
                self.ap.logger.debug("link, {}, {}".format(ctx.event.sender_id, msg))

                # link = "https://delta.world-of-dungeons.org/wod/spiel/hero/item.php?name={}&is_popup=0&world=CD".format(quote(name))
                # 回复消息 "hello, <发送者id>!"
                ctx.add_return("reply", ["[{}]{}的链接 https://delta.world-of-dungeons.org/wod/spiel/hero/{}.php?name={}&is_popup=0&world=CD".format(cn_type, name, str_type, quote(name))])

                # 阻止该事件默认行为（向接口获取回复）
                ctx.prevent_default()

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message  # 这里的 event 即为 PersonNormalMessageReceived 的对象
        self.ap.logger.debug("link , {}, {}".format(ctx.event.sender_id, msg))
        if msg == "link" or msg == "linki" or msg == "links" or msg == "l":
            self.ap.logger.debug("link 格式错误, {}, {}".format(ctx.event.sender_id, msg))
            ctx.add_return("reply", [r'组装链接格式: #linki 物品 或 #links 套装'])
            ctx.prevent_default()
        else:
            ret = re.match(r'link([is]) (.*)', msg)
            if ret:
                type = ret.group(1)
                name = ret.group(2)
                str_type = 'item'
                cn_type = '物品'
                if type == 'i':
                    str_type = 'item'
                    cn_type = '物品'
                elif type == 's':
                    str_type = 'set'
                    cn_type = '套装'

                # 输出调试信息
                self.ap.logger.debug("link, {}, {}".format(ctx.event.sender_id, msg))

                # link = "https://delta.world-of-dungeons.org/wod/spiel/hero/item.php?name={}&is_popup=0&world=CD".format(quote(name))
                # 回复消息 "hello, <发送者id>!"
                ctx.add_return("reply", ["[{}]{}的链接 https://delta.world-of-dungeons.org/wod/spiel/hero/{}.php?name={}&is_popup=0&world=CD".format(cn_type, name, str_type, quote(name))])

                # 阻止该事件默认行为（向接口获取回复）
                ctx.prevent_default()



    # 插件卸载时触发
    def __del__(self):
        pass
