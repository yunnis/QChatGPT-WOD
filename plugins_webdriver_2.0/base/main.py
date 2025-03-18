from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类

import time

import plugins.base.bot_request

# 注册插件
@register(name="bot_request", description="机器人请求", version="0.1", author="x")
class MyPlugin(BasePlugin):
    # 插件加载时触发
    def __init__(self, host: APIHost):
        pass

    # 异步初始化
    async def initialize(self):
        pass

    def __plg_request(self, ctx):
        msg, who, group = ctx.event.text_message, ctx.event.sender_id, ctx.event.launcher_id
        print(msg, who, group)
        return (plugins.base.bot_request.bot_request(who, group, msg)) if msg else (False, "")

    # 当收到个人消息时触发
    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        curTick = time.perf_counter()
        _, ret_str = self.__plg_request(ctx)
        if ret_str != "":
            ctx.add_return("reply", ["{}\n操作耗时: {:.2f}".format(ret_str, time.perf_counter() - curTick)])
        # 阻止该事件默认行为（向接口获取回复）
        ctx.prevent_default()

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        curTick = time.perf_counter()
        _, ret_str = self.__plg_request(ctx)
        if ret_str != "":
            ctx.add_return("reply", ["{}\n操作耗时: {:.2f}".format(ret_str, time.perf_counter() - curTick)])
        # 阻止该事件默认行为（向接口获取回复）
        ctx.prevent_default()

    # 插件卸载时触发
    def __del__(self):
        pass

