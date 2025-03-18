from urllib.parse import quote

def linki(name):
    return True, "[物品]{}的链接 https://delta.world-of-dungeons.org/wod/spiel/hero/item.php?name={}&is_popup=0&world=CD".format(name, quote(name))

def links(name):
    return True, "[套装]{}的链接 https://delta.world-of-dungeons.org/wod/spiel/hero/set.php?name={}&is_popup=0&world=CD".format(name, quote(name))
