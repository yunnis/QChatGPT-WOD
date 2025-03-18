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

    def __help(self, ctx):
        # 输出调试信息
        self.ap.logger.debug("help, {}".format(ctx.event.sender_id))
        # 回复消息 "hello, <发送者id>!"
        ctx.add_return("reply", ["目前支持命令:\nlinki 物品,links 套装\ndrop 物品,drop 地城\nhave(暂时关闭)\n更新地城,常规地城,今日地城,明日地城,上个地城,当前地城,取消地城,切 地城\n等级,更新等级\n添加关键字\n战报列表"])
        # 阻止该事件默认行为（向接口获取回复）
        ctx.prevent_default()

    # 当收到个人消息时触发
    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message  # 这里的 event 即为 PersonNormalMessageReceived 的对象
        if msg == 'h' or msg == 'help':
            self.__help(ctx)

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message  # 这里的 event 即为 PersonNormalMessageReceived 的对象
        if  msg == 'help' or msg == 'h':
            self.__help(ctx)

    # 插件卸载时触发
    def __del__(self):
        pass
