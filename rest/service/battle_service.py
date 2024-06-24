# -*- coding: utf-8 -*-


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
    "self_tactics": {""},
    "type": "legend",  # legend or sp
    "pike": "s_level",
    "shield": "a_level",
    "bow": "c_level",
    "cavalry": "s_level",
    "level": 50,  # 45 or 50
    "add_property": "default",  # default or add by user(front-end)
    "default_attack_type": "physical",
    "advance_level": "full",  # full 、half、single
}


class BattleService(object):
    def __init__(self, own_team, enemy_team):
        self.own_team = own_team
        self.enemy_team = enemy_team

    def arms_to_property(self, arms_type):
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

    def hurt_value(self, diff_value):
        if diff_value > 0:
            hurt_v = 0.0005 * (diff_value ** 2) + 0.9 * diff_value + 4.5
        else:  # diff_value < 0

