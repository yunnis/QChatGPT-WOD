from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import re
import time
import importlib

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import plugins.base.jscode as jscode
import plugins.base.pycode as pycode
import plugins.base.driver as driver

GroupIDMaps = {'0' : '0', '0' : '0'}
HeroIDMaps = {'0' : '0', '0' : '0'}
groups = (0, 0)

def get_group_id(group):
    return GroupIDMaps[group] if group in GroupIDMaps else '0'

def get_hero_id(group):
    return HeroIDMaps[group] if group in HeroIDMaps else '0'

def decorator_time(func):
    # 异步装饰器
    async def wrapper(self, *args):
        curTick = time.perf_counter()
        ctx = None
        # kwargs 取参数
        # if 'ctx' in kwargs:
            # ctx = kwargs['ctx']
        # 异步调用被修饰的方法
        ret, ret_str = await func(self, *args)

        # args 取参数
        if args:
            ctx = args[0]
        if ctx:
            ctx.add_return("reply", ["{}, 操作耗时: {:.2f}".format(ret_str, time.perf_counter() - curTick)])
            ctx.prevent_default()
        else:
            self.ap.logger.error("无法找到ctx")

    return wrapper

# 注册插件
@register(name="base", description="基础库", version="0.1", author="x")
class MyPlugin(BasePlugin):

    __driver = None
    # 插件加载时触发
    def __init__(self, host: APIHost):
        if self.__driver == None:
            self.__driver = driver.WodDriver(host)

    # 异步初始化
    async def initialize(self):
        if self.__driver:
            self.ap.logger.critical("init driver end ")
        pass

    # 当收到个人消息时触发
    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message  # 这里的 event 即为 PersonNormalMessageReceived 的对象
        if msg == "base":
            # ctx.add_return("reply", ['pid {}'.format(PostID)])
            return True, 'p {}'.format("装修中")
        elif msg == "登录":
            self.ap.logger.critical(f"尝试登录, group{ctx.event.launcher_id}, who{ctx.event.sender_id}")
            _, ret_str = self.__driver.login()
            ctx.add_return("reply", ['{}'.format(ret_str)])
            ctx.prevent_default()
        elif msg == "加载js":
            importlib.reload(jscode)
        elif msg == "加载代码":
            importlib.reload(pycode)
        
        
        ret = re.match(r'open (.*)', msg)
        if ret:
            url = ret.group(1)
            self.__driver.open(url)
            return
        
        ret = re.match('执行js (.*)', msg)
        if ret:
            var = ret.group(1)
            if getattr(jscode, var):
                ret, ret_str = self.__driver.exce_js(getattr(jscode, var))
                if not ret_str:
                    ctx.add_return("reply", ['{} 执行 {}'.format(ret_str, "成功" if ret else "失败")])
                    return

                if not isinstance(ret_str, str):
                    ret_str = str(ret_str)

                ctx.add_return("reply", ['{} 执行 {}'.format(ret_str[:15], "成功" if ret else "失败")])
            else:
                ctx.add_return("reply", ['{} 无法在jscode中找到, 是否执行 加载js 了? 还是输入错误'.format(var)])
            ctx.prevent_default()

        ret = re.match('执行代码 (.*)', msg)
        if ret:
            var = ret.group(1)
            if getattr(pycode, var):
                ret, ret_str = exec(getattr(pycode, var))
                if not ret_str:
                    ctx.add_return("reply", ['{} 执行 {}'.format(ret_str, "成功" if ret else "失败")])
                    return

                if not isinstance(ret_str, str):
                    ret_str = str(ret_str)

                ctx.add_return("reply", ['{} 执行 {}'.format(ret_str[:15], "成功" if ret else "失败")])
            else:
                ctx.add_return("reply", ['{} 无法在pycode中找到, 是否执行 加载代码 了? 还是输入错误'.format(var)])
            ctx.prevent_default()

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        return



    # 插件卸载时触发
    def __del__(self):
        pass
