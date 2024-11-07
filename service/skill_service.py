import random


"""
buff: 增加伤害的数量 -> damage_bonus_<增伤百分数> 
"""


class SkillService:
    """
    战法服务类，用于管理和提供技能的相关操作。
    """
    def __init__(self):
        self.skills = {}

    def get_skill(self, skill_name):
        """
        根据技能名称获取技能实例。
        :param skill_name: 技能名称
        :return: 技能实例
        """
        return self.skills.get(skill_name)


if __name__ == "__main__":
    # 创建技能

    skill_yongwutongshen = YongwutongshenSkill(
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

    skill_luanshijianxiong = LuanshijianxiongSkill(
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

    skill_yingshilanggu = YingshilangguSkill(
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



    skill_jifengzhouyu = JifengzhouyuSkill(
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

    skill_wudangfeijun = Skill(
        name="无当飞军",
        skill_type="troop",
        attack_type="intelligence",
        quality="S",
        source="自带战法",
        source_general="王平",
        target="self_team",
        effect={
            "probability": 1.0,
            "required_troop": "archer",
            "buffs": {
                "defense": 22,
                "speed": 22,
                "range": "all",
                "target": "self",
            },
            "initial_effect": {
                "status": "poison",
                "duration": 3,
                "attack_coefficient": 88
            }
        },
    )
