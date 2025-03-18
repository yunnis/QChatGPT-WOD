GroupIDMaps = {'0' : '0', '0' : '0'}
HeroIDMaps = {'0' : '0', '0' : '0'}
groups = (0, 0)

dungeons = {}
players = {
    groups[0]: {
        0: '',
        0: '',
        0: '',
        0: '',
        0: '',
        0: '',
        0: '',
        0: '',
        0: '',
        0: '',
        0: '',
        0: '',
    }
}

def get_group_id(group):
    group = str(group)
    return GroupIDMaps[group] if group in GroupIDMaps else None

def get_hero_id(group):
    group = str(group)
    return HeroIDMaps[group] if group in HeroIDMaps else None

def get_player(group):
    return 

def init_dungeon():
    import os
    import json
    global dungeons
    if os.path.exists('dungeon.json') and os.path.getsize('dungeon.json'):
        with open('dungeon.json', 'r+', encoding='utf-8') as json_file:
            json_d = json.load(json_file)
            for d in json_d:
                dungeons[d['name']] = d['sysId']
            print(f'\n*** 共初始化 {len(dungeons)} 个地城\n')

def have_dungeon(name):
    return name in dungeons


init_dungeon()
