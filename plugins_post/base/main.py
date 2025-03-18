from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import re

__default_group='0'
__default_hero='0'
Cookie_Part = ''
Cookie = ''
PostID = ''
GroupIDMaps = {'qq_group' : 'wod_group_id', 'qq_group' : 'wod_group_id'}
HeroIDMaps = {'qq_group' : 'wod_hero_id', 'qq_group' : 'wod_hero_id'}
groups = (0, 1)

def set_cookie(target, c):
    global Cookie, Cookie_Part
    if c != Cookie_Part:
        old = Cookie
        Cookie = f'your cookie {c}'
        target.ap.logger.critical(f"update cookie {Cookie}\nnew {c} \nold {old}")
    
def set_pid(target, p):
    global PostID
    if p != PostID:
        old = PostID
        PostID = p
        target.ap.logger.critical(f"update PostID {PostID}\nold {old}")

def get_group_id(group):
    return GroupIDMaps[group] if group in GroupIDMaps else __default_group

def get_hero_id(group):
    return HeroIDMaps[group] if group in HeroIDMaps else __default_hero

def getCookie():
    global Cookie
    return Cookie
def getPostID():
    global PostID
    return PostID

# 注册插件
@register(name="base", description="基础库", version="0.1", author="x")
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
        global Cookie
        global PostID
        if msg == "getCookie":
            ctx.add_return("reply", ['c {}'.format(Cookie)])
            return
        elif msg == "getPostID":
            ctx.add_return("reply", ['pid {}'.format(PostID)])
            return

        ret = re.match('setCookie (.*)', msg)
        if ret:
            Cookie = ret.group(1)
            ctx.add_return("reply", [f'设置Cookie成功, {Cookie}'])
            # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_default()
            return
        else:
            ret = re.match('setPostID (.*)', msg)
            if ret:
                PostID = ret.group(1)

                ctx.add_return("reply", [f'设置PostID成功, {PostID}'])
                # 阻止该事件默认行为（向接口获取回复）
                ctx.prevent_default()
                return


    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        return



    # 插件卸载时触发
    def __del__(self):
        pass
