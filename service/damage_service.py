import random
import math

from general_service import GeneralService


class DamageService:

    def _is_troop_restriction(self, attacker, defender) -> int:
        """
        判断兵种克制关系
        :param attacker:
        :param defender:
        :return:
            1 - 攻击方兵种克制防御方兵种
            0 - 无克制关系
            -1 - 防御方兵种克制攻击方兵种
        """
        restriction_relation = {
            "pick": "cavalry",
            "cavalry": "shield",
            "shield": "bow",
            "bow": "pick",
        }
        attacker_troop_type = attacker.general_info.take_troops_type
        defender_troop_type = defender.general_info.take_troops_type
        if restriction_relation.get(attacker_troop_type) == defender_troop_type:
            return 1  # Attacker counters defender
        elif restriction_relation.get(defender_troop_type) == attacker_troop_type:
            return -1  # Defender counters attacker
        else:
            return 0  # No counter relationship

    def calculate_damage(
        self, attacker_level, defender_level, attacker_attr, defender_attr, attacker_troops,
        defender_troops, attacker_advanced_bonus, defender_advanced_bonus, attacker_basic_bonus,
        defender_basic_bonus, morale, troop_restriction, skill_coefficient, special_damage_bonus=1
    ):
        """
        :param attacker_level: 攻击者等级
        :param defender_level: 防御者等级
        :param attacker_attr: 攻击者属性值（如武力或智力）
        :param defender_attr: 防御者属性值（如统率或智力）
        :param attacker_troops: 攻击者带兵数量
        :param defender_troops: 防御者带兵数量
        :param attacker_advanced_bonus:  攻击者进阶数量（红度）
        :param defender_advanced_bonus:  防御者进阶数量（红度）
        :param attacker_basic_bonus: 攻击者普通增伤，如战法
        :param defender_basic_bonus: 防御者普通减伤，如战法，减伤上限90%
        :param morale: 士气值
        :param troop_restriction: 是否存在兵种克制
        :param skill_coefficient: 技能系数（技能面板上的百分比）
        :param special_damage_bonus: 特殊增伤，例如技能里SP荀彧的减伤或周泰的增伤
        :return:
        """
        # 1. 基础伤害
        base_damage = self.calculate_base_damage(
            attacker_level, defender_level, attacker_attr, defender_attr, attacker_troops
        )

        # 2. 基础增减伤
        basic_damage_modifier = self.calculate_basic_damage_modifier(
            attacker_level,
            defender_level,
            attacker_advanced_bonus,
            defender_advanced_bonus,
            attacker_basic_bonus,
            defender_basic_bonus,
        )

        # 3. 原始伤害
        base_damage_with_modifier = base_damage * basic_damage_modifier
        if attacker_troops >= 5000:
            minimum_damage = 100
        else:
            minimum_damage = attacker_troops * 0.02
        raw_damage = base_damage_with_modifier + minimum_damage

        # 4. 结算伤害
        # 4.1 士气降低伤害降低
        morale_modifier = (100 - morale) * 0.007

        # 4.2 如果攻击者兵种克制防御者，则伤害增加， 如果攻击者兵种被防御者克制，则伤害减少，没有克制关系则不变
        if troop_restriction == 1:
            troop_restriction_val = 0.12
        elif troop_restriction == -1:
            troop_restriction_val = -0.12
        else:
            troop_restriction_val = 0
        troop_modifier = 1 + troop_restriction_val

        final_damage = raw_damage * (1 - morale_modifier) * troop_modifier * (skill_coefficient / 100)

        # 5. 浮动伤害
        float_damage = final_damage * (round(random.uniform(0.86, 0.94), 2))

        # 6. 最终伤害
        final_damage_with_bonus = float_damage * special_damage_bonus
        return math.ceil(final_damage_with_bonus)

    def calculate_base_damage(self, attacker_level, defender_level, attacker_attr, defender_attr, attacker_troops):
        attribute_damage = self.calculate_attribute_damage(attacker_level, defender_level, attacker_attr, defender_attr)
        troop_damage = self.calculate_troop_damage(attacker_troops)
        return max(attribute_damage + troop_damage, 0)

    def calculate_attribute_damage(self, attacker_level, defender_level, attacker_attr, defender_attr):
        attacker_multiplier = max(attacker_level - 20, 0) / 50 + 1
        defender_multiplier = max(defender_level - 20, 0) / 50 + 1
        return attacker_attr * attacker_multiplier - defender_attr * defender_multiplier

    def calculate_troop_damage(self, troops):
        if troops <= 2000:
            return troops / 10
        else:
            return math.ceil((math.log2(troops) - 9) * 100)

    def calculate_basic_damage_modifier(
        self,
        attacker_level,
        defender_level,
        attacker_advanced_bonus,
        defender_advanced_bonus,
        attacker_basic_bonus,
        defender_basic_bonus,
    ):
        advanced_bonus = self.calculate_advanced_bonus(
            attacker_level, defender_level, attacker_advanced_bonus, defender_advanced_bonus
        )
        basic_bonus = (1 + attacker_basic_bonus / 100) * (1 + defender_basic_bonus / 100)
        return advanced_bonus * basic_bonus

    def calculate_advanced_bonus(
         self, attacker_level, defender_level, attacker_advanced_bonus, defender_advanced_bonus
    ):
        attacker_advanced = (2 + (attacker_level - 30) / 20) * attacker_advanced_bonus
        defender_advanced = (2 + (defender_level - 30) / 20) * defender_advanced_bonus
        return (1 + attacker_advanced / 100) * (1 + defender_advanced / 100)
