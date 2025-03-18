# 虽然用了window 但是刷新页面还是找不到, 所以不用变量了, 直接把这个写到js代码里
baseParams = """
    window.baseParams = [
      "session_hero_id",
      "wod_post_id",
      "wod_post_world",
      "klasse_id",
      "klasse_name",
      "rasse_id",
      "rasse_name",
      "gruppe_id",
      "gruppe_name",
      "clan_id",
      "clan_name",
      "stufe",
      "heldenname",
      "spielername",
    ];
"""

func_getBaseSearchParams = """
window.getBaseSearchParams = function() {
  const searchParams = new URLSearchParams();
  $("input:hidden").each(function () {
    const $this = $(this);
    const key = $this.attr("name");
    if (window.baseParams.includes(key)) {
      searchParams.set($this.attr("name"), $this.val());
    }
  });
  return searchParams;
}
"""

nextD = """return $('.block_inner:contains("下一个地城：")');"""

baseSearchParams = """
    const baseParams = [
    "session_hero_id",
    "wod_post_id",
    "wod_post_world",
    "klasse_id",
    "klasse_name",
    "rasse_id",
    "rasse_name",
    "gruppe_id",
    "gruppe_name",
    "clan_id",
    "clan_name",
    "stufe",
    "heldenname",
    "spielername",
  ];
  const searchParams = new URLSearchParams();
  $("input:hidden").each(function () {
    const $this = $(this);
    const key = $this.attr("name");
    if (baseParams.includes(key)) {
      searchParams.set($this.attr("name"), $this.val());
    }
  });
"""
rep_str = {
  "d1" : baseSearchParams + """
    let baseUrl = location.origin + "/wod/spiel/dungeon/dungeon.php?";
    const groupLv = searchParams.get("stufe");
    searchParams.set("TABLE_DEFAULT_SORT_DIR", "DESC");
    searchParams.set("TABLE_DEFAULT_SORT_COL", "7");
    searchParams.set("TABLE_DEFAULT_PAGE", "1");
    searchParams.set("TABLE_DEFAULT_PSNR[1]", "20");
    searchParams.set("TABLE_DEFAULT_PSNR[2]", "20");
    searchParams.set("TABLE_DATED_SORT_DIR", "ASC");
    searchParams.set("TABLE_DATED_SORT_COL", "14");
    searchParams.set("TABLE_DATED_PAGE", "1");
    searchParams.set("dungeon_1name", "不可能存在的地城");
    searchParams.set(
    "profile_data_dungeon_1_profile_data",
    "HogNB0ny8I/FjaOg6FXrzZvwI0A1hZgI77jjRYoCRE27wTAWqILHdEzHicsmJZl6X7ZRBEIW822E5+rsUoHjcPHJM1dTqbJE0c1Ad4c6gLXcUjcGy5WB8H0lm1qobBxf"
    );
    searchParams.set(
    "callback_js_code_dungeon_1_callback_js_code",
    "9hAUpnwetF8TrxnkIxgBdD27k4isavkaEEd/PwhJTLL8yf4MvBsSYedcxPRse51t2x6Aw2bcXKHHlyCszAStN2nnub0CncNJMDrZQePru5mpXW3It99S/D+JypTOewMQ/T9+eXLlhJZ7vK+j9IAKgKVS+EFJPGzy61GBgu60fBk="
    );
    searchParams.set("dungeon_1level", "99");
    searchParams.set("dungeon_1level_to", "99");
    searchParams.set("dungeon_1level_allowed", "99");
    searchParams.set("dungeon_1level_allowed_to", "99");
    searchParams.set("dungeon_1groupLevel", groupLv);
    searchParams.set("dungeon_1profile_id", "0");
    searchParams.set("dungeon_1is_open", "1");
  """,
  "d2" : """
      searchParams.set("dungeon_2name", "不可能存在的地城");
      searchParams.set(
      "profile_data_dungeon_1_profile_data",
      "HogNB0ny8I/FjaOg6FXrzZvwI0A1hZgI77jjRYoCRE26Yi3zTNw4kxlf3EBWtEk1b6aVuW+FUuN8kSMRggg8h3JkxoL2NsUxavZXWRdyOxUUEMX5AKRE3eAUHOs1WJk3"
      );
      searchParams.set(
      "callback_js_code_dungeon_1_callback_js_code",
      "hjeqjpM+qZ3O91mfrGQpvhGIqpJEtjGwgXlmEmXfIQzBrxMpR69Guzy7+7UjXgADJMzqeXDJhCUPVMr4x2KfpOKujjttFf22twLrAnOMemRyC0FkOn1zx6YBUufUkR7Ckg4pf2y/2z74zxDx8svUS6Kwihgpc54Xeb1xFKyGmQQ="
      );
      searchParams.set("dungeon_2level", "99");
      searchParams.set("dungeon_2level_to", "99");
      searchParams.set("dungeon_2level_allowed", "99");
      searchParams.set("dungeon_2level_allowed_to", "99");
      searchParams.set("dungeon_2groupLevel", groupLv);
      searchParams.set("dungeon_2profile_id", "0");
      searchParams.set("dungeon_2is_open", "1");
      baseUrl += "session_hero_id=" + searchParams.get("session_hero_id");
      ajaxAlert("切换中，请稍候...");
      console.log(baseUrl)
      console.log(searchParams.toString())
      fetch(baseUrl, {
      headers: {
          accept:
          "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
          "content-type": "application/x-www-form-urlencoded",
      },
      method: "POST",
      body: searchParams.toString(),
      })
      .then((resp) => {
          // location.replace(location.href);
          return resp.text();
      })
      .then((html) => {
          console.log(html);
          let $curT = $("#gadgetNextdungeonTime");
          if (!$curT.length) {
          // 处理偶尔出现的刷新后英雄变化的问题
          let [baseUrl, params] = location.href.split("?");
          const urlParams = new URLSearchParams(params);
          if (!urlParams.has("session_hero_id")) {
              urlParams.set("session_hero_id", searchParams.get("session_hero_id"));
              params = urlParams.toString();
          }
          location.replace(baseUrl + "?" + params);
          return;
          }
          let $curB = $curT.prevAll("b:first");
          let $curC = $curT.nextAll("div[id^=CombatDungeonConfigSelector]:first");
          let $newT = $(html).find("#gadgetNextdungeonTime");
          let $newB = $newT.prevAll("b:first");
          let $newC = $newT.nextAll("div[id^=CombatDungeonConfigSelector]:first");
          $curT.replaceWith($newT);
          $curB.replaceWith($newB);
          $curC.replaceWith($newC);
          ajaxAlert("已切换！");
          setTimeout(function () {
          _ajaxCloseModalDialog("ajax_dialog");
          }, 800);
      });
    """,

    'cancle_d' : baseSearchParams +
    """
    const $nextDungeonDiv = $('.block_inner:contains("下一个地城：")');
    if (!$nextDungeonDiv.length) return;

    let baseUrl = location.origin + "/wod/spiel/dungeon/dungeon.php?is_popup=1";
    const groupLv = searchParams.get("stufe");
    searchParams.set("TABLE_DEFAULT_SORT_DIR", "DESC");
    searchParams.set("TABLE_DEFAULT_SORT_COL", "7");
    searchParams.set("TABLE_DEFAULT_PAGE", "1");
    searchParams.set("TABLE_DEFAULT_PSNR[1]", "20");
    searchParams.set("TABLE_DEFAULT_PSNR[2]", "20");
    searchParams.set("TABLE_DATED_SORT_DIR", "ASC");
    searchParams.set("TABLE_DATED_SORT_COL", "14");
    searchParams.set("TABLE_DATED_PAGE", "1");

    searchParams.set("dungeon_1name", "不可能存在的地城");
    searchParams.set(
      "profile_data_dungeon_1_profile_data",
      "HogNB0ny8I/FjaOg6FXrzZvwI0A1hZgI77jjRYoCRE27wTAWqILHdEzHicsmJZl6X7ZRBEIW822E5+rsUoHjcPHJM1dTqbJE0c1Ad4c6gLXcUjcGy5WB8H0lm1qobBxf"
    );
    searchParams.set(
      "callback_js_code_dungeon_1_callback_js_code",
      "9hAUpnwetF8TrxnkIxgBdD27k4isavkaEEd/PwhJTLL8yf4MvBsSYedcxPRse51t2x6Aw2bcXKHHlyCszAStN2nnub0CncNJMDrZQePru5mpXW3It99S/D+JypTOewMQ/T9+eXLlhJZ7vK+j9IAKgKVS+EFJPGzy61GBgu60fBk="
    );
    searchParams.set("dungeon_1level", "99");
    searchParams.set("dungeon_1level_to", "99");
    searchParams.set("dungeon_1level_allowed", "99");
    searchParams.set("dungeon_1level_allowed_to", "99");
    searchParams.set("dungeon_1groupLevel", groupLv);
    searchParams.set("dungeon_1profile_id", "0");
    searchParams.set("dungeon_1is_open", "1");
    searchParams.set("dungeon_2name", "不可能存在的地城");
    searchParams.set(
      "profile_data_dungeon_1_profile_data",
      "HogNB0ny8I/FjaOg6FXrzZvwI0A1hZgI77jjRYoCRE26Yi3zTNw4kxlf3EBWtEk1b6aVuW+FUuN8kSMRggg8h3JkxoL2NsUxavZXWRdyOxUUEMX5AKRE3eAUHOs1WJk3"
    );
    searchParams.set(
      "callback_js_code_dungeon_1_callback_js_code",
      "hjeqjpM+qZ3O91mfrGQpvhGIqpJEtjGwgXlmEmXfIQzBrxMpR69Guzy7+7UjXgADJMzqeXDJhCUPVMr4x2KfpOKujjttFf22twLrAnOMemRyC0FkOn1zx6YBUufUkR7Ckg4pf2y/2z74zxDx8svUS6Kwihgpc54Xeb1xFKyGmQQ="
    );
    searchParams.set("dungeon_2level", "99");
    searchParams.set("dungeon_2level_to", "99");
    searchParams.set("dungeon_2level_allowed", "99");
    searchParams.set("dungeon_2level_allowed_to", "99");
    searchParams.set("dungeon_2groupLevel", groupLv);
    searchParams.set("dungeon_2profile_id", "0");
    searchParams.set("dungeon_2is_open", "1");

    searchParams.set("unvisit", "取消探险");
    fetch(baseUrl, {
      headers: {
        accept:
          "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
      },
      method: "POST",
      body: searchParams.toString(),
    }).then((resp) => {
      location.reload();
    });
    """
}

