
from core.active_skill import ActiveSkill

skill_weizhenhuaxia = ActiveSkill(
    name="weizhenhuaxia",
    skill_type="prepare_active",
    attack_type="physical",
    quality="S",
    source="self_implemented",
    source_general="关羽",
    target="enemy_group",
    effect={
        # normal 表示正常情况下的技能描述； leader 表示如果装备此战法的为主将有不同的技能描述
        "normal": {
            "probability": 0.35,
            "attack_coefficient": 146,  # 此为 DamageService 里的 skill_coefficient
            "release_range": 3,
            "target": "enemy",
            "to_enemy_buff": {
                "status": ["is_disarmed", "is_silenced"],
                "release_range": 3,
                "duration": 1,
            },
            "status_probability": 0.5,
            "self_buff": {
                "type": "physical_damage",
                "damage_bonus": 36,
                "duration": 2,
            }
        },
        "leader": {
            "probability": 0.35,
            "attack_coefficient": 146,
            "release_range": 3,
            "target": "enemy",
            "to_enemy_buff": {
                "status": ["is_disarmed", "is_silenced"],
                "release_range": 3,
                "duration": 1,
            },
            "status_probability": 0.65,
            "self_buff": {
                "type": "physical_damage",
                "damage_bonus": 36,
                "duration": 2,
            }
        }
    },
    activation_type="prepare",
)

skill_weimoumikang = ActiveSkill(
    name="weimoumikang",
    skill_type="prepare_active",
    attack_type="physical",
    quality="S",
    source="inherited",
    source_general=None,
    target="enemy_group",
    effect={
        # normal 表示正常情况下的技能描述； leader 表示如果装备此战法的为主将有不同的技能描述
        "normal": {
            "probability": 0.4,
            "attack_coefficient": 158,  # 此为 DamageService 里的 skill_coefficient
            "release_range": 2,
            "target": "enemy",
            "to_enemy_buff": {
                "status": ["is_weakness"],
                "release_range": 2,
                "duration": 2,
            },
            "status_probability": 1,
        }
    },
    activation_type="prepare",
)

skill_hengsaoqianjun = ActiveSkill(
    name="hengsaoqianjun",
    skill_type="instant_active",
    attack_type="physical",
    quality="S",
    source="inherited",
    source_general=None,
    target="enemy_group",
    effect={
        "normal": {
            "probability": 0.4,
            "attack_coefficient": 100,  # 此为 DamageService 里的 skill_coefficient
            "release_range": 3,
            "target": "enemy",
            "to_enemy_buff": {
                "prerequisite ": ["is_disarmed", "is_silenced"],
                "status": ["is_taunted"],
                "release_range": 3,
                "duration": 1,
            },
            "status_probability": 0.3,
        }
    },
    activation_type="instant",
)

skill_jiangmenhunv = ActiveSkill(
    name="jiangmenhunv",
    skill_type="instant_active",
    attack_type="physical",
    quality="S",
    source="self_implemented",
    source_general="guanyinping",
    target="enemy_group",
    effect={
        "normal": {
            "probability": 0.6,
            "release_range": 2,
            "target": "enemy",
            "attack_coefficient": 128,
            "to_enemy_buff": {
                "prerequisite ": {"target_attack_count": 3},
                "status": ["is_taunted"],
                "release_range": 2,
                "duration": 1,
                "additional_damage_coefficient": 20,  # 拥有虎嗔状态时，收到伤害时额外增加20%伤害，最多叠加三次
            },
            "status_probability": 1,
        },
    },
    activation_type="instant",
)

skill_jiangdongmenghu = ActiveSkill(
    name="jiangdongmenghu",
    skill_type="instant_active",
    attack_type="physical",
    quality="S",
    source="self_implemented",
    source_general="孙坚",
    target="enemy_group",
    effect={
        "normal": {
            "probability": 0.5,
            "release_range": "2",
            "target": "enemy",
            "attack_coefficient": 126,
            "status": ["taunt"],
            "status_duration": 2
        },
        "leader": {
            "probability": 0.5,
            "release_range": 2,
            "target": "enemy",
            "attack_coefficient": 126,
            "status": ["taunt"],
            "status_duration": 2,
            "self_buff": {
                "damage_reduction": -20
            }
        }

    },
    activation_type="instant",
)

skill_shimianmaifu = ActiveSkill(
    name="十面埋伏",
    skill_type="prepare_active",
    attack_type="intelligence",
    quality="S",
    source="自带战法",
    source_general="程昱",
    target="enemy_group",
    effect={
        "normal": {
            "probability": 0.35,
            "coefficient": 74,
            "release_range": "2",
            # 禁疗状态和叛逃状态
            "status": ["no_healing", "defection"],
            "status_duration": 2,
            "attack_coefficient": 96,
        }
    },
    activation_type="prepare",
)

skill_jifengzhouyu = ActiveSkill(
    name="jifengzhouyu",
    skill_type="instant_active",
    attack_type="physical",
    quality="S",
    source="inherited",
    source_general="sp-zhangliang,sp-zhangbao",
    target="enemy_single",
    effect={
        "normal": {
            "probability": 0.4,
            "release_range": 1,
            "target": "enemy",
            "attack_coefficient": 78,
            "status": ["is_nohealing"],
            "status_duration": 1,
        }
    },
    activation_type="instant",
)
