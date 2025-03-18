import requests
import json
from urllib.parse import quote

from plugins.base.common.base import have_dungeon, get_group_id


def drop(group, name):
    groupid = get_group_id(str(group))
    return (True, "地城 {} 的掉落链接 https://www.christophero.xyz/groupDungeon/{}?groupId={}".format(name, quote(name), groupid)) if have_dungeon(name) else __drop_item(groupid, name)

def __drop_item(groupid, name):
    # 定义请求的 URL
    url = 'https://www.christophero.xyz/wod/item/dropAnalysis'
    # 定义请求头
    headers = {
        "Content-Type": "application/json"
    }
    # 定义要发送的数据
    data = {
        'serverName': 'delta',
        'name':  str(name),
        'groupId': groupid,
        'notExistInsert': 'false',
    }

    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code != 200:
        return False, "物品 [item:{}] 不存在, code {}".format(name, resp.status_code)
    json_r = json.loads(resp.text)
    if json_r['code'] == 404 or json_r['msg'] == '您所查询的道具不存在':
        return False, '所查询的道具 {} 不存在'.format(name)
    elif json_r['code'] == 200 and json_r['msg']=='请求成功':
        drop=''
        if json_r['data']['worldDrop']:
            drop='\n世界'
        if json_r['data']['shop']:
            drop+='\n市集购买'
        if json_r['data']['draw']:
            drop=drop+"\n抽奖"
        if json_r['data']['obtain']:
            drop=drop+"\n"+json_r['data']['obtain']
        for j_e in json_r['data']['dropList']:
            drop=drop+"\n{}({}-{})".format(j_e['dungeonName'], j_e['minLevel'], j_e['maxLevel'])
            if j_e['challenge'] != None:
                drop=drop+"<挑战{}>".format(j_e['challenge'])
            if j_e['certain'] == 1:
                drop=drop+" 必出1个"
            elif j_e['certain'] == 12:
                drop=drop+" 人手1个"
            if j_e['triggerItems']!= None:
                drop=drop+" + [item:{}]".format(j_e['triggerItems'])
            if j_e['note'] != None:
                drop=drop+"\n{}".format(j_e['note'])
        return True, '道具 [item:{}] 已掉落 {} 个\n获取途径:{}'.format(name, json_r['data']['count'], drop)
    return False, ""
