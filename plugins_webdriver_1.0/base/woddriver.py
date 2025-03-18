baseParams = """
    baseParams = [
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
function getBaseSearchParams() {
  const searchParams = new URLSearchParams();
  $("input:hidden").each(function () {
    const $this = $(this);
    const key = $this.attr("name");
    if (baseParams.includes(key)) {
      searchParams.set($this.attr("name"), $this.val());
    }
  });
  return searchParams;
}
"""