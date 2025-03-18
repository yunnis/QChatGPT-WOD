from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import os
import json
import re

from plugins.base.main import groups

Keys = {
    f'{groups[0]}':
        {
            '啊?' : "我不倒啊",
        },
    f'{groups[1]}':
        {
            '啊?' : "我不倒啊",
        }
}

# 注册插件
@register(name="uesrkey", description="自定义关键字", version="0.1", author="x")
class MyPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        global Keys
        if os.path.exists('userKey.json'):
            with open('userKey.json', 'r+') as json_file:
                Keys = json.load(json_file)
                host.ap.logger.info(f'读取{len(Keys)} 个自定义关键字, {Keys}')
        pass

    # 异步初始化KK
    async def initialize(self):
        pass

    def doUesrKey(self, ctx: EventContext):
        global Keys
        group = ctx.event.launcher_id
        if not group or group == 0:
            group = groups[0]
        group = str(group)

        msg = ctx.event.text_message
        if msg in Keys[group]:  # 如果消息为hello
            ctx.add_return("reply", ["{}".format(Keys[group][msg])])

        ret = re.match(r'添加关键字 (.*) (.*)', msg)
        if ret:
            key = ret.group(1)
            msg = ret.group(2)
            Keys[group][key] = str(msg)
            ctx.add_return("reply", [f"增加关键字 [{key}] 成功, 内容 [{msg}]"])
            with open('userKey.json', 'w') as json_file:
                json.dump(Keys, json_file, indent=4)  # 使用 indent=4 进行格式化
                self.ap.logger.critical(f'{group} 写入{len(Keys[group])} 个自定义关键字')

        ret = re.match(r'删除关键字 (.*)', msg)
        if ret:
            key = ret.group(1)
            if key in Keys[group]:
                del Keys[group][key]
                ctx.add_return("reply", [f"删除关键字 [{key}] 成功]"])
                with open('userKey.json', 'w') as json_file:
                    json.dump(Keys, json_file, indent=4)  # 使用 indent=4 进行格式化
                    self.ap.logger.critical(f'{group} 删除一个关键字 写入{len(Keys[group])} 个自定义关键字')
            else:
                ctx.add_return("reply", [f"删除关键字 [{key}] 失败, 不要删除没有的关键字啊]"])

    # 当收到个人消息时触发
    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message  # 这里的 event 即为 PersonNormalMessageReceived 的对象
        if msg == '添加关键字':
            ctx.add_return("reply", [f"格式: 添加关键字 关键字 内容"])
        else:
            self.doUesrKey(ctx)
        # 阻止该事件默认行为（向接口获取回复）
        ctx.prevent_default()

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message  # 这里的 event 即为 PersonNormalMessageReceived 的对象
        if msg == '添加关键字':
            ctx.add_return("reply", [f"格式: 添加关键字 关键字 内容"])
        else:
            self.doUesrKey(ctx)
        # 阻止该事件默认行为（向接口获取回复）
        ctx.prevent_default()

    # 插件卸载时触发
    def __del__(self):
        pass
