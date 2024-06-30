
from db.mongodb import db

skills_collection = db["skills"]

skills = [
    {
        "name": "威震华夏",
        "type": "active",
        "quality": "S",
        "source": "自带战法",
        "source_general": "关羽",
        "troop_restrictions": ["骑兵", "弓兵", "枪兵", "盾兵", "器械"],
        "target": "group",
        "probability": 0.35,
        "effect": {
            "prepare_rounds": 1,
            "damage_coefficient": 146,
            "status_effects": [
                {"status": "缴械", "probability": 0.5, "duration": 1},
                {"status": "计穷", "probability": 0.5, "duration": 1}
            ],
            "self_buff": {
                "type": "兵刃伤害",
                "amount": 36,
                "duration": 2
            },
            "main_general_buff": {
                "type": "控制效果概率",
                "amount": 0.65
            }
        }
    },
    {
        "name": "江东猛虎",
        "type": "active",
        "quality": "S",
        "source": "自带战法",
        "source_general": "孙坚",
        "troop_restrictions": ["骑兵", "弓兵", "枪兵", "盾兵", "器械"],
        "target": "group",
        "probability": 0.5,
        "effect": {
            "damage_coefficient": 103,
            "status_effects": [
                {"status": "嘲讽", "duration": 2}
            ]
        }
    },
    {
        "name": "百步穿杨",
        "type": "active",
        "quality": "S",
        "source": "自带战法",
        "source_general": "黄忠",
        "troop_restrictions": ["骑兵", "弓兵", "枪兵", "盾兵", "器械"],
        "target": "group",
        "probability": 0.35,
        "effect": {
            "prepare_rounds": 1,
            "self_buff": {
                "type": "会心几率",
                "amount": 25,
                "duration": 2
            },
            "damage_coefficient": 180,
            "enhanced_damage_coefficient": 240,
            "enhanced_condition": "控制状态"
        }
    },
    {
        "name": "暗度陈仓",
        "type": "active",
        "quality": "S",
        "source": "自带战法",
        "source_general": "邓艾",
        "troop_restrictions": ["骑兵", "弓兵", "枪兵", "盾兵", "器械"],
        "target": "single",
        "probability": 0.5,
        "effect": {
            "prepare_rounds": 1,
            "damage_coefficient": 260,
            "damage_type": "谋略",
            "status_effects": [
                {"status": "震慑", "duration": 2}
            ]
        }
    },
    {
        "name": "天下无双",
        "type": "active",
        "quality": "S",
        "source": "自带战法",
        "source_general": "吕布",
        "troop_restrictions": ["骑兵", "弓兵", "枪兵", "盾兵", "器械"],
        "target": "single",
        "probability": 0.35,
        "effect": {
            "duel": True,
            "self_buff": {
                "type": "兵刃伤害减少",
                "amount": 7,
                "duration": 2
            }
        }
    },
    {
        "name": "熯天炽地",
        "type": "active",
        "quality": "S",
        "source": "传承战法",
        "source_general": "陆逊",
        "troop_restrictions": ["骑兵", "弓兵", "枪兵", "盾兵", "器械"],
        "target": "group",
        "probability": 0.35,
        "effect": {
            "prepare_rounds": 1,
            "damage_coefficient": 102,
            "damage_type": "谋略",
            "status_effects": [
                {"status": "灼烧", "damage_coefficient": 72, "duration": 2}
            ]
        }
    },
    {
        "name": "瞋目横矛",
        "type": "active",
        "quality": "S",
        "source": "传承战法",
        "source_general": "张飞",
        "troop_restrictions": ["骑兵", "枪兵", "盾兵", "器械"],
        "target": "self",
        "probability": 0.4,
        "effect": {
            "self_buff": {
                "type": "武力",
                "amount": 50,
                "duration": 2
            },
            "group_attack": {
                "damage_coefficient": 55,
                "duration": 2
            }
        }
    },
    {
        "name": "临战先登",
        "type": "active",
        "quality": "S",
        "source": "自带战法",
        "source_general": "乐进",
        "troop_restrictions": ["骑兵", "弓兵", "枪兵", "盾兵", "器械"],
        "target": "group",
        "probability": 1.0,
        "effect": {
            "damage_coefficient": 150,
            "self_status": {"status": "虚弱", "duration": 1}
        }
    },
    {
        "name": "五雷轰顶",
        "type": "active",
        "quality": "S",
        "source": "自带战法",
        "source_general": "张角",
        "troop_restrictions": ["骑兵", "弓兵", "枪兵", "盾兵", "器械"],
        "target": "group",
        "probability": 0.45,
        "effect": {
            "prepare_rounds": 1,
            "damage_coefficient": 136,
            "damage_type": "谋略",
            "multi_target": 5,
            "status_effects": [
                {"status": "震慑", "probability": 0.3, "duration": 1}
            ],
            "main_general_buff": {
                "type": "震慑概率",
                "amount": 0.2,
                "conditions": ["水攻", "沙暴"]
            }
        }
    },
    {
        "name": "十面埋伏",
        "type": "active",
        "quality": "S",
        "source": "自带战法",
        "source_general": "程昱",
        "troop_restrictions": ["骑兵", "弓兵", "枪兵", "盾兵", "器械"],
        "target": "group",
        "probability": 0.35,
        "effect": {
            "damage_coefficient": 74,
            "ignore_defense": True,
            "status_effects": [
                {"status": "禁疗", "duration": 2},
                {"status": "叛逃", "duration": 2}
            ],
            "follow_up_effects": [
                {"damage_coefficient": 96, "damage_type": "谋略", "conditions": ["负面状态"]}
            ]
        }
    },
    {
        "name": "机鉴先识",
        "type": "command",
        "quality": "S",
        "source": "自带战法",
        "source_general": "SP荀彧",
        "troop_restrictions": ["骑兵", "盾兵", "弓兵", "枪兵", "器械"],
        "target": "self_team",
        "effect": {
            "prepare_rounds": 1,
            "buffs": {
                "type": "警戒",
                "amount": 2,
                "probability": 0.42,
                "duration": 3,
                "max_stacks": 4,
                "damage_reduction": 40
            },
            "main_general_buff": {
                "type": "状态反弹",
                "probability": 0.75,
                "conditions": ["缴械", "计穷", "混乱", "震慑"],
                "duration": 2
            }
        }
    },
    {
        "name": "盛气凌敌",
        "type": "command",
        "quality": "S",
        "source": "传承战法",
        "source_general": ["曹丕", "颜良"],
        "troop_restrictions": ["骑兵", "弓兵", "枪兵", "盾兵", "器械"],
        "target": "enemy_team",
        "effect": {
            "debuffs": {
                "type": "缴械",
                "probability": 0.9,
                "duration": 2
            }
        }
    },
    {
        "name": "横戈跃马",
        "type": "command",
        "quality": "S",
        "source": "传承战法",
        "source_general": ["郝昭", "凌统"],
        "troop_restrictions": ["骑兵", "弓兵", "枪兵", "盾兵", "器械"],
        "target": "all",
        "effect": {
            "buffs": [
                {"type": "普通攻击伤害", "amount": 20, "duration": 3},
                {"type": "突击战法伤害", "amount": 20, "duration": 3}
            ],
            "debuffs": [
                {"type": "谋略伤害", "amount": -30, "duration": 3}
            ]
        }
    },
    {
        "name": "奇计良谋",
        "type": "command",
        "quality": "S",
        "source": "传承战法",
        "source_general": ["蒋琬", "鲁肃"],
        "troop_restrictions": ["骑兵", "弓兵", "枪兵", "盾兵", "器械"],
        "target": "self_team",
        "effect": {
            "debuffs": [
                {"type": "兵刃伤害", "amount": -28, "affected_by": "武力", "duration": 3},
                {"type": "谋略伤害", "amount": -28, "affected_by": "智力", "duration": 3}
            ]
        }
    },
    {
        "name": "暴戾无仁",
        "type": "assault",
        "quality": "S",
        "source": "传承战法",
        "source_general": "董卓",
        "troop_restrictions": ["骑兵", "弓兵", "枪兵", "盾兵", "器械"],
        "target": "single",
        "probability": 0.35,
        "effect": {
            "damage_coefficient": 196,
            "status_effects": [
                {"status": "混乱", "duration": 1}
            ]
        }
    },
    {
        "name": "速乘其利",
        "type": "assault",
        "quality": "S",
        "source": "传承战法",
        "source_general": ["王元姬", "SP朱儁"],
        "troop_restrictions": ["骑兵", "盾兵", "弓兵", "枪兵", "器械"],
        "target": "single",
        "probability": 0.35,
        "effect": {
            "damage_coefficient": 185,
            "status_effects": [
                {"status": "计穷", "duration": 1}
            ]
        }
    },
    {
        "name": "白马义从",
        "type": "troop",
        "quality": "S",
        "source": "自带战法",
        "source_general": "公孙瓒",
        "troop_restrictions": ["弓兵"],
        "target": "self_team",
        "probability": 1.0,
        "effect": {
            "buffs": [
                {"type": "行军速度", "amount": 50, "duration": 2},
                {"type": "先攻", "amount": 1, "duration": 2},
                {"type": "主动战法发动率", "amount": 10, "duration": 2}
            ]
        }
    },
    {
        "name": "无当飞军",
        "type": "troop",
        "quality": "S",
        "source": "自带战法",
        "source_general": "王平",
        "troop_restrictions": ["弓兵"],
        "target": "self_team",
        "probability": 1.0,
        "effect": {
            "buffs": [
                {"type": "统率", "amount": 22, "duration": 3},
                {"type": "速度", "amount": 22, "duration": 3}
            ],
            "initial_effects": [
                {"status": "中毒", "damage_coefficient": 80, "duration": 3}
            ]
        }
    }
]

skills_collection.insert_many(skills)
print("所有技能信息已成功插入到 MongoDB 中")
