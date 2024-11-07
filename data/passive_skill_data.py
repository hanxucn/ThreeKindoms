from core.passive_skill import PassiveSkill


skill_meihuo = PassiveSkill(
    name="meihuo",
    skill_type="passive",
    attack_type="",
    quality="S",
    source="inherited",
    source_general="zhenji",
    target="enemy_group",
    effect={
        "normal": {
            "probability": 1,
            "attack_coefficient": 0,
            "release_range": 1,
            "target": "enemy",
            "to_enemy_buff": {
                "status": ["is_confusion", "is_silenced", "is_weakness"],  # 混乱 技穷 虚弱
                "duration": 1,
                "buff_probability": 0.45,
            },
        },
    },
)

skill_qianlizoudanqi = PassiveSkill(
    name="qianlizoudanqi",
    skill_type="passive",
    attack_type="physical",
    quality="S",
    source="events",
    source_general=None,
    target="self",
    effect={
        "normal": {
            "attack_coefficient": 238
        }
    }

)

skill_yanrenpaoxiao = PassiveSkill(
    name="yanrenpaoxiao",
    skill_type="passive",
    attack_type="physical",
    quality="S",
    source="self_implemented",
    source_general="zhangfei",
    target="enemy_group",
    effect={
        "normal": {
            "attack_coefficient": 104,
            "release_range": 3,
            "target": "enemy",
            "release_turn_with_attack_coefficient": {2: 104, 4: 104},
            "to_enemy_buff": {
                "status": ["defense_reduction"],
                "duration": 2,
                "value": -50,
                "prerequisite": ["is_disarmed", "is_silenced"],
            },
        },
        "leader": {
            "attack_coefficient": 104,
            "release_range": 3,
            "target": "enemy",
            "release_turn_with_attack_coefficient": {2: 104, 4: 104, 6: 88},
            "to_enemy_buff": {
                "status": ["defense_reduction"],
                "duration": 2,
                "value": -50,
                "prerequisite": ["is_disarmed", "is_silenced"],
            },
        },
    },
)

skill_shibiesanri = PassiveSkill(
    name="shibiesanri",
    skill_type="passive",
    attack_type="intelligence",
    quality="S",
    source="inherited",
    source_general="lvmeng",
    target="enemy_group",
    effect={
        "normal": {
            "probability": 1,
            "attack_coefficient": 180,
            "release_range": 3,
            "target": "enemy",
            "self_buff": {
                "status": ["is_evasion"],  # 规避状态
                "duration": 3,
                "buff_probability": 0.3,
            },
        },
    },
)
