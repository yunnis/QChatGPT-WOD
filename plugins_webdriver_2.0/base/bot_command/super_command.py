import importlib

import plugins.base.common.jscode as jscode
import plugins.base.common.pycode as pycode
import plugins.base.base.driver as driver

def login_wod():
    print(f"尝试登录")
    return driver.WodDriver.get_instance().login()

def reload_js():
    importlib.reload(jscode)
def reload_py():
    importlib.reload(pycode)

def open_url(url):
    driver.WodDriver.get_instance().open(url)
    return True, "打开"

def exec_js(var):
    if getattr(jscode, var):
        ret, ret_str = driver.WodDriver.get_instance().exce_js(getattr(jscode, var))
        if not ret_str:
            return ret, '{} 执行 {}'.format(ret_str, "成功" if ret else "失败")

        if not isinstance(ret_str, str):
            ret_str = str(ret_str)
        return ret, '{} 执行 {}'.format(ret_str[:15], "成功" if ret else "失败")

    return False, '{} 无法在jscode中找到, 是否执行 加载js 了? 还是输入错误'.format(var)

def exec_py(var):
    if getattr(pycode, var):
        ret, ret_str = exec(getattr(pycode, var))
        if not ret_str:
            return ret, '{} 执行 {}'.format(ret_str, "成功" if ret else "失败")

        if not isinstance(ret_str, str):
            ret_str = str(ret_str)

        return ret, '{} 执行 {}'.format(ret_str[:15], "成功" if ret else "失败")

    return False, '{} 无法在pycode中找到, 是否执行 加载代码 了? 还是输入错误'.format(var)

def exec(var):
    try:
        return True, str(list(exec(var)))
    except Exception as e:
        return False, f"exec error {e}"
