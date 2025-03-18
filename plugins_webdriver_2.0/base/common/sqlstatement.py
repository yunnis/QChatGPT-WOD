insert_battle_report = """
insert into battle_report values(%s, %s, %s, %s, %s, (%s));
"""

select_battle_report = """
select report_id, name, report_time, max_layout, player
from battle_report where report_id = %s limit 1;
"""

insert_report_layer = """
insert into report_layer values(DEFAULT, %s, %s, %s, %s, %s);
"""

# 回合表太冗余了, 统计一层的数据, 要查多个记录再汇总
insert_report_round = """
insert into report_round values(DEFAULT, %s, %s, %s);
"""
select_report_layer = """
select layer_id, layer_num, round_count, player_info
from report_layer where report_id = %s and layer_num = %s limit 1;
"""