
from core import command_skill

skill_yongwutongshen = command_skill.CommandSkill(
    name="yongwutongshen",
    skill_type="command",
    attack_type="intelligence",
    quality="S",
    source="inherited",
    source_general="simayi",
    target="enemy_group",
    effect={
        "normal": {
            "probability": 1,
            "release_range": 2
        },
    }
)


skill_luanshijianxiong = command_skill.LuanshijianxiongSkill(
    name="luanshijianxiong",
    skill_type="command",
    attack_type="",
    quality="S",
    source="self_implemented",
    source_general="caocao",
    target="self_group",
    effect={},
    self_groups=[],
)


skill_yingshilanggu = command_skill.YingshilangguSkill(
    name="yingshilanggu",
    skill_type="command",
    attack_type="intelligence",
    quality="S",
    source="self_implemented",
    source_general="simayi",
    target="enemy_group",
    effect={
        "normal": {
            "probability": 1,
            "self_buff": [
                {
                    "name": "intelligence_attack_double",
                    "duration": 7,
                    "damage_bonus": 200,
                    "release_probability": 7,
                    "probability": 0.8
                },
                {
                    "name": "intelligence_health_double",
                    "duration": 7,
                    "health_bonus": 200,
                    "probability": 0.8
                },
            ],
            "max_buff_count": 2,
            "attack_coefficient": 154,
            "target": "enemy",
            "release_range": [1, 2]
        },
        "leader": {
            "probability": 1,
            "self_buff": [
                {
                    "name": "intelligence_attack_double",
                    "duration": 7,
                    "damage_bonus": 200,
                    "release_probability": 0.16,
                    "probability": 1
                },
                {
                    "name": "intelligence_attack_double",
                    "duration": 7,
                    "damage_bonus": 200,
                    "release_probability": 7,
                    "probability": 0.8
                },
                {
                    "name": "intelligence_health_double",
                    "duration": 7,
                    "health_bonus": 200,
                    "probability": 0.8
                },
            ],
            "max_buff_count": 2,
            "attack_coefficient": 154,
            "target": "enemy",
            "release_range": [1, 2]
        },
    }
)
