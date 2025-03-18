import os
import json

from plugins.base.common.base import groups

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

def __init_user_key():
    global Keys
    if os.path.exists('userKey.json'):
        with open('userKey.json', 'r+') as json_file:
            Keys = json.load(json_file)
            print(f'*** 读取{len(Keys)} 个自定义关键字, {Keys}')

def add_user_key(group, key, value):
    global Keys
    group = str(group)
    Keys[group][key] = str(value)
    with open('userKey.json', 'w') as json_file:
        json.dump(Keys, json_file, indent=4)  # 使用 indent=4 进行格式化
    return True, f"增加关键字 [{key}] 成功, 内容 [{value}]"

def del_user_key(group, key):
    global Keys
    group = str(group)
    if key in Keys[group]:
        del Keys[group][key]
        with open('userKey.json', 'w') as json_file:
            json.dump(Keys, json_file, indent=4)  # 使用 indent=4 进行格式化
        return True, f"删除关键字 [{key}] 成功]"
    else:
        return False, f"删除关键字 [{key}] 失败, 不要删除没有的关键字啊]"

def get_user_key(group, key):
    global Keys
    group = str(group)
    return (True, Keys[group][key]) if key in Keys[group] else (False, "")

__init_user_key()
