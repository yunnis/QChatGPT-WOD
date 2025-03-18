from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import re

# 注册插件
@register(name="help", description="帮助", version="0.1", author="x")
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
        if msg == 'h' or msg == 'help':
            # 输出调试信息
            self.ap.logger.debug("help, {}, {}".format(ctx.event.sender_id, msg))
            # 回复消息 "hello, <发送者id>!"
            ctx.add_return("reply", ["目前支持命令:\nlink\ndrop\nhave(暂不支持多群)\n更新地城,常规地城,今日地城,明日地城,当前地城,取消地城\n等级,更新等级\n添加关键字"])
            # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_default()



    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message  # 这里的 event 即为 PersonNormalMessageReceived 的对象
        if  msg == 'help' or msg == 'h':
            # 输出调试信息
            self.ap.logger.debug("help, {}, {}".format(ctx.event.sender_id, msg))
            # 回复消息 "hello, <发送者id>!"
            ctx.add_return("reply", ["目前支持命令:\nlink\ndrop\nhave(暂不支持多群)\n更新地城,常规地城,今日地城,明日地城,当前地城,取消地城\n等级,更新等级\n添加关键字"])
            # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_default()


    # 插件卸载时触发
    def __del__(self):
        pass
