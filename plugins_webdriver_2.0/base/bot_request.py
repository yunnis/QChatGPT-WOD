import traceback as __tb
import imp

import plugins.base.bot_command
import plugins.base.bot_command.help as __h
import plugins.base.bot_command.user_key as __uk
import plugins.base.bot_command.drop as __d
import plugins.base.bot_command.link as __l
import plugins.base.bot_command.dungeon as __dg
import plugins.base.bot_command.super_command as __su
import plugins.base.bot_command.report as __rp

__bot_requests = {
    'su'   : [True,  ],
    'h'    : [True, lambda c_, msgs: __h.get_command_list()],
    'help' : [True, lambda group, msgs: __h.get_command_list()],

    'drop' : [True, lambda group, msgs: __d.drop(group, msgs[1])],

    'linki' : [True, lambda group, msgs: __l.linki(msgs[1])],
    'links' : [True, lambda group, msgs: __l.links(msgs[1])],

    '添加': [True, lambda group, msgs: __uk.add_user_key(group, msgs[1], msgs[2]) if not __has_request(msgs[1]) else __user_key_error(msgs[0])],
    '删除': [True, lambda group, msgs: __uk.del_user_key(group, msgs[1]) if not __has_request(msgs[1]) else __user_key_error(msgs[0])],

    "地城":  [True, lambda group, msgs: __dg.get_all_dungeon_state(group)],
    "更新地城":  [True, lambda group, msgs: __dg.update_dungeon(group, True)],
    "常规地城":  [True, lambda group, msgs: __dg.reply_common(group)],
    "今日地城":  [True, lambda group, msgs: __dg.reply_today(group)],
    "明日地城":  [True, lambda group, msgs: __dg.reply_tomorrow(group)],
    "限时地城":  [True, lambda group, msgs: __dg.reply_time(group)],
    "自定地城":  [True, lambda group, msgs: __dg.reply_self(group)],
    "添加地城":  [True, lambda group, msgs: __dg.add_self_dungeon(group, msgs[1], msgs[2])],
    "地城状态":  [True, lambda group, msgs: __dg.dungeon_state(group)],
    "当前地城":  [True, lambda group, msgs: __dg.cur_dungeon(group)],
    "取消地城":  [True, lambda group, msgs: __dg.cancle_dungeon(group)],
    "等级":     [True, lambda group, msgs: __dg.get_lv(group)],
    "更新等级":  [True, lambda group, msgs: __dg.calc_lv(group, False)],  # 添加第三个参数
    "切":       [True, lambda group, msgs: __dg.change_dungeon(group, msgs[1])],

    "战报列表": [True, lambda group, msgs: __rp.get_list(group, 5)],
    "上个地城": [True, lambda group, msgs: __rp.get_list(group, 1)],
    "完成率"  : [True, lambda group, msgs: __rp._parse_pass(group, msgs[1] if len(msgs) > 1 else None)],
    "解析buff": [True, lambda group, msgs: __rp.__parse_buff(group, msgs[1] if len(msgs) > 1 else None)],
    "buff"   : [True, lambda group, msgs: __rp.__get_buff(group, msgs[1], msgs[2], msgs[3], msgs[4], msgs[5], None)],
}

__su_requests = {
    "登录":     [True, lambda msgs: __su.login_wod()],
    "rjs":     [True, lambda msgs: __su.reload_js()],
    "rpyc":    [True, lambda msgs: __su.reload_py()],
    "rpy":     [True, lambda msgs: imp.reload(msgs[1])],
    "打开":     [True, lambda msgs: __su.open_url(msgs[1])],
    "ejs":     [True, lambda msgs: __su.exec_js(msgs[1])],
    "epy":     [True, lambda msgs: __su.exec_py(msgs[1])],
    "setsr":  [True, lambda msgs: __set_requests(__su_requests, msgs[1], msgs[2])],
    "setbr":  [True, lambda msgs: __set_requests(__bot_requests, msgs[1], msgs[2])],
}

def __set_requests(request: dict, key, value):
    if key in request:
        if request[key][0] != bool(value):
            request[key][0] = bool(value)
            return True, f'set {key} succ, {value}'
        else:
            return True, f'{key} is {value}, no set require'
    return False, f'{key} not in requests'

def __has_request(key):
    return key in __bot_requests
    
def __user_key_error(info):
    return False, (f'关键字 {info} 是机器人指令, 禁止覆盖')

def bot_request(who, group, msg: str):
    try:
        print(f'bot_request, {who} {group} {msg}')
        msgs = msg.split()
        if not group or group == 0:
            group = list(__dg.GroupIDMaps.keys())[1]
        if __has_request(msgs[0]):
            if not __bot_requests[msgs[0]][0]:
                return False, f'{msgs[0]} 暂时关闭'
                # 不用所有 bot_requests 的lambda 都写参数msgs的写法
                # return bot_requests[msgs[0]][1](msgs) if 'msgs' in bot_requests[msgs[0]][1].__code__.co_varnames else bot_requests[msgs[0]][1]()
            return __bot_requests[msgs[0]][1](group, msgs) if msgs[0] != 'su' else __su_request(who, msgs[1:])
        return __uk.get_user_key(group, msgs[0])
    except Exception as e:
        print(f'\nbot_request 出现问题拉, {who} {group} {msg}, 出错: {e}\n{e}\n')
        print(f'调用栈:')
        __tb.print_exc()
        return False, f'{msg}出错了, 错误是: {e}'

def __su_request(who, msgs: str):
    print(f'su_request, {who} {msgs}')
    if who != 0:
        return False, f'嗯?'
    if msgs[0] not in __su_requests:
        return False, f'{msgs[0]} 不存在'
    if not __su_requests[msgs[0]][0]:
        return False, f'{msgs[0]} 已关闭'

    return __su_requests[msgs[0]][1](msgs)

