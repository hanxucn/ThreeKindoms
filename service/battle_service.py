import random
import math


guanyu = {
    "name": "guanyu",
    "country": "shu",
    "basic_power": 97,
    "power_up": 2.68,
    "basic_defense": 97,
    "defense_up": 2.04,
    "basic_intelligence": 79,
    "intelligence_up": 1.05,
    "basic_speed": 74,
    "speed_up": 1.3,
    "self_tactics": {""},  # 自带战法
    "type": "legend",  # legend or sp
    "pike": "s_level",  # 枪兵 S
    "shield": "a_level",  # 盾兵 A
    "bow": "c_level",  # 弓箭 C
    "cavalry": "s_level",  # 骑兵 S
    "level": 50,  # 45 or 50
    "add_property": {"power": 50},  # 默认升级全加力量
    "default_attack_type": "physical",  # 武力 or 谋略伤害
    "advanced_count": 0,  # 进阶数由白板到满红分为 0 到 5，每有一个红度额外会多10点属性分配和2%增减伤
    "is_dynamic": False,  # 是否为动态
    "is_classic": False,  # 是否为典藏
}


class BattleService:
    def __init__(self, own_team, enemy_team):
        self.own_team = own_team
        self.enemy_team = enemy_team

    def _arms_to_property(self, arms_type):
        addition = 1
        if arms_type == "s_level":
            addition *= 1.2
        elif arms_type == "a_level":
            addition *= 1
        elif arms_type == "b_level":
            addition *= 0.85
        else:
            addition *= 0.7
        return addition

    def get_general_property(self, general_fight, property_type, property_up):
        """
        get final property value
        :param general_fight: general_fight_info
        :param property_type: basic_power / basic_intelligence / basic_speed
        :param property_up: power_up / intelligence_up / speed_up
        :return:
        """
        property_value = (
            general_fight["general"][property_up] * general_fight["general"]["level"]
        ) + general_fight["general"][property_type]
        if general_fight["general"]["add_property"] == "default":
            to_fight_type = general_fight["general"].get(general_fight["fight_arm"])
            ext = self.arms_to_property(to_fight_type)
            if general_fight["general"]["level"] < 50:
                final_value = (property_value + 40) * ext + 20
            else:
                final_value = (property_value + 50) * ext + 20
            if general_fight["group_same"]:
                final_value = final_value * 1.1
        return final_value

    def calculate_damage(
        self, attacker_level, defender_level, attacker_attr, defender_attr, attacker_troops,
        defender_troops, attacker_advanced_bonus, defender_advanced_bonus, attacker_basic_bonus,
        defender_basic_bonus, morale, troop_restriction, skill_coefficient, special_damage_bonus
    ):
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
        minimum_damage = min(attacker_troops / 50, 100)
        raw_damage = base_damage_with_modifier + minimum_damage

        # 4. 结算伤害
        morale_modifier = (100 - morale) * 0.007
        troop_modifier = 1 + (0.12 if troop_restriction else -0.12)
        final_damage = raw_damage * (1 - morale_modifier) * troop_modifier * (skill_coefficient / 100)

        # 5. 浮动伤害
        float_damage = final_damage * (0.86 + (0.94 - 0.86) * math.random())

        # 6. 最终伤害
        final_damage_with_bonus = float_damage * special_damage_bonus
        return math.ceil(final_damage_with_bonus)

    def calculate_base_damage(self, attacker_level, defender_level, attacker_attr, defender_attr, attacker_troops):
        attribute_damage = self.calculate_attribute_damage(attacker_level, defender_level, attacker_attr, defender_attr)
        troop_damage = self.calculate_troop_damage(attacker_troops)
        return max(attribute_damage + troop_damage, 0)

    def calculate_attribute_damage(self, attacker_level, defender_level, attacker_attr, defender_attr):
        attacker_multiplier = max((attacker_level - 20) / 50 + 1, 1)
        defender_multiplier = max((defender_level - 20) / 50 + 1, 1)
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
            attacker_level, defender_level, attacker_advanced_bonus,  defender_advanced_bonus
        )
        basic_bonus = (1 + attacker_basic_bonus / 100) * (1 + defender_basic_bonus / 100)
        return advanced_bonus * basic_bonus

    def calculate_advanced_bonus(
        self, attacker_level, defender_level, attacker_advanced_bonus, defender_advanced_bonus
    ):
        attacker_advanced = (2 + (attacker_level - 30) / 20) * attacker_advanced_bonus
        defender_advanced = (2 + (defender_level - 30) / 20) * defender_advanced_bonus
        return (1 + attacker_advanced / 100) * (1 + defender_advanced / 100)

    # def _general_hurt_value(self, diff_value):
    #     """
    #     伤害技术公式
    #     :param diff_value: 双方属性差值，己方武力 - 对方统帅
    #     :return:
    #     """
    #     if diff_value > 0:
    #         hurt_v = 0.0005 * (diff_value ** 2) + 0.9 * diff_value + 4.5
    #     else:
    #         hurt_v = random.randint(10, 30)
    #
    #     return hurt_v
    #
    # def _soldiers_number_hurt_value(self):

