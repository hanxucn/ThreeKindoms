import random
import math


guanyu = {
    "name": "guanyu",
    "country": "shu",
    "basic_power": 97,  # 默认1级初始武力值
    "power_up": 2.68,  # 每升 1 级提升的武力值
    "basic_defense": 97,  # 默认 1 级初始防御值
    "defense_up": 2.04,  # 每升 1 级提升的防御值
    "basic_intelligence": 79,  # 默认 1 级初始智力值
    "intelligence_up": 1.05,  # 每升 1 级提升的智力值
    "basic_speed": 74,  # 默认 1 级初始速度值
    "speed_up": 1.3,  # 每升 1 级提升的速度值
    "self_tactics": {""},  # 自带战法
    "type": "normal",  # 普通 or sp
    # 部队兵种适应度:pike 枪兵 S，shield 盾兵 A, bow 弓箭 C, cavalry 骑兵 S
    "troop_adaptability": {"pike": "s_level", "shield": "a_level", "bow": "c_level", "cavalry": "s_level"},
    # "level": 50,  # 45 or 50  这个值从前端传入参数
    # "add_property": {"power": 50},  # 默认升级全加力量，这里改用前端传递
    "default_attack_type": "physical",  # 武力 physical  or 谋略 intelligence or 综合 combined
    "advanced_count": 0,  # 进阶数由白板到满红分为 0 到 5，每有一个红度额外会多10点属性分配和2%增减伤
    "has_dynamic": False,  # 是否有动态人物
    # "is_classic": False,  # 是否为典藏，这个值从前端传入参数
}


class GeneralService:
    def __init__(self, general_info):
        self.general_info = general_info

    def _arms_type_to_property(self, general_adaptability):
        addition = 1
        if general_adaptability == "s_level":
            addition *= 1.2
        elif general_adaptability == "a_level":
            addition *= 1
        elif general_adaptability == "b_level":
            addition *= 0.85
        elif general_adaptability == "c_level":
            addition *= 0.7
        else:
            addition *= 1
        return addition

    def get_general_property(self, general_info, level):
        """
        get final property value
        :param general_info: general_info
        :param level: 45 or 50 级
        :return:
        """
        import ipdb; ipdb.set_trace()
        # 计算将领最终武力基础值 + 等级 * 每级武力提升 + 满级时 50 点属性加成
        power_value = general_info["basic_power"] + level * general_info["power_up"]

        intelligence_value = general_info["basic_intelligence"] + level * general_info["power_up"]

        speed_value = general_info["basic_speed"] + level * general_info["speed_up"]

        # ext = self._arms_type_to_property(general_info["troop_adaptability"])
        # final_power_value = (final_power_value + user_add_property.get("power", 0)) * ext
        # final_intelligence_value = (final_intelligence_value + user_add_property.get("intelligence", 0)) * ext
        # final_speed_value = (final_speed_value + user_add_property.get("speed", 0)) * ext
        # if is_same_group:
        #     final_power_value = int(final_power_value * 1.1)
        #     final_intelligence_value = int(final_intelligence_value * 1.1)
        #     final_speed_value = int(final_speed_value * 1.1)
        return {
            "power": power_value,
            "intelligence": intelligence_value,
            "speed": speed_value,
        }

    def calculate_damage(
        self, attacker_level, defender_level, attacker_attr, defender_attr, attacker_troops,
        defender_troops, attacker_advanced_bonus, defender_advanced_bonus, attacker_basic_bonus,
        defender_basic_bonus, morale, troop_restriction, skill_coefficient, special_damage_bonus
    ):
        """
        :param attacker_level: 攻击者等级
        :param defender_level: 防御者等级
        :param attacker_attr:
        :param defender_attr:
        :param attacker_troops:
        :param defender_troops:
        :param attacker_advanced_bonus:
        :param defender_advanced_bonus:
        :param attacker_basic_bonus:
        :param defender_basic_bonus:
        :param morale:
        :param troop_restriction:
        :param skill_coefficient:
        :param special_damage_bonus:
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
        minimum_damage = min(attacker_troops / 50, 100)
        raw_damage = base_damage_with_modifier + minimum_damage

        # 4. 结算伤害
        morale_modifier = (100 - morale) * 0.007
        troop_modifier = 1 + (0.12 if troop_restriction else -0.12)
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

    def _ready_fight_general_property(
        self, is_dynamic, is_classic, advanced_count, user_level, choose_arm_type, user_add_property
    ):
        # 只计算原始没有任何其他情况到对应等级的属性
        origin_general_property = self.get_general_property(self.general_info, user_level)
        general_property = {
            "power": origin_general_property["power"] + user_add_property["power"],
            "intelligence": origin_general_property["intelligence"] + user_add_property["intelligence"],
            "speed": origin_general_property["speed"] + user_add_property["speed"],
        }

        if self.general_info["has_dynamic"] and is_dynamic:
            general_property = {key: value + 10 for key, value in general_property.items()}

        if is_classic:
            general_property = {key: value + 10 for key, value in general_property.items()}

        if advanced_count < 0 or advanced_count > 5:
            raise Exception("user advanced count should between 0 ~ 5")
        general_property = {key: value + advanced_count * 10 for key, value in general_property.items()}

        if choose_arm_type:
            ext = self._arms_type_to_property(self.general_info["troop_adaptability"].get(choose_arm_type))
            general_property = {key: value * ext for key, value in general_property.items()}

        return general_property


if __name__ == "__main__":
    # Example usage:
    attacker_level = 50
    defender_level = 50
    attacker_attr = 250
    defender_attr = 120
    attacker_troops = 10000
    defender_troops = 10000
    attacker_advanced_bonus = 10
    defender_advanced_bonus = 5
    attacker_basic_bonus = 20
    defender_basic_bonus = 15
    morale = 100
    troop_restriction = True  # True if attacker troop restricts defender, False otherwise
    skill_coefficient = 100  # percentage
    special_damage_bonus = 1.2  # 20% additional damage

    bs = GeneralService(guanyu)
    general_values = bs._ready_fight_general_property(
        True, False, 5, 50, None,
        {"power": 50, "intelligence": 0, "speed": 0}
    )
    print(general_values)
