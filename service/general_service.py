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
    "self_skill": {""},  # 自带战法
    "skills": {},  # 选择的战法
    "type": "normal",  # 普通 or sp
    # 部队兵种适应度:pike 枪兵 S，shield 盾兵 A, bow 弓箭 C, cavalry 骑兵 S
    "troop_adaptability": {"pike": "s_level", "shield": "a_level", "bow": "c_level", "cavalry": "s_level"},
    # "level": 50,  # 45 or 50  这个值从前端传入参数
    # "add_property": {"power": 50},  # 默认升级全加力量，这里改用前端传递
    "default_attack_type": "physical",  # 武力 physical  or 谋略 intelligence or 综合 combined
    "fusion_count": 0,  # 进阶数由白板到满红分为 0 到 5，每有一个红度额外会多10点属性分配和2%增减伤
    "has_dynamic": True,  # 是否有动态人物
    "take_troops": 10000,  # 默认初始带满兵1W，如果为 45级 则为 95000
    # "is_classic": False,  # 是否为典藏，这个值从前端传入参数
}


class GeneralService:
    def __init__(self, general_info):
        self.general_info = general_info
        self.skills = {}  # 自带战法 加上选择的额外两个战法
        self.alive = True
        self.statuses = {}
        self.buffs = {}

    def is_alive(self):
        return self.alive and self.general_info["take_troops"] > 0

    def take_damage(self, damage):
        self.general_info["take_troops"] -= damage
        if self.general_info["take_troops"] <= 0:
            self.general_info["take_troops"] = 0
            self.alive = False

    def add_status(self, status, duration):
        self.statuses[status] = duration

    def add_buff(self, buff, amount):
        if buff in self.buffs:
            self.buffs[buff] += amount
        else:
            self.buffs[buff] = amount

    def add_debuff(self, debuff, amount):
        if debuff in self.buffs:
            self.buffs[debuff] -= amount
        else:
            self.buffs[debuff] = -amount

    def execute_skills(self, defenders, battle_service):
        for skill in self.skills:
            skill.apply_effect(self, defenders, battle_service)

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
        # 计算将领最终武力基础值 + 等级 * 每级武力提升 + 满级时 50 点属性加成
        power_value = general_info["basic_power"] + (level - 1) * general_info["power_up"]

        intelligence_value = general_info["basic_intelligence"] + (level - 1) * general_info["intelligence_up"]

        speed_value = general_info["basic_speed"] + (level - 1) * general_info["speed_up"]

        defense_value = general_info["basic_defense"] + (level - 1) * general_info["defense_up"]

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
            "defense": defense_value,
        }

    def overall_can_allocation_property(self, is_dynamic, is_classic, fusion_count, user_level):
        """
        :param is_dynamic: 是否是动态人物， 如果是会多 10 的属性分配
        :param is_classic: 是否典藏，如果是会多 10 的属性分配
        :param fusion_count: 进阶数，每进阶一个红度会减伤 2% 和增加对敌人伤害 2%，且多 10 点属性分配
        :param user_level: 将领等级，每提升 10 级会有 10 点额属性分配
        :return:
        """
        can_allocation_property = 0
        if self.general_info["has_dynamic"] and is_dynamic:
            can_allocation_property += 10

        if is_classic:
            can_allocation_property += 10

        if fusion_count < 0 or fusion_count > 5:
            raise Exception("user advanced count should between 0 ~ 5")
        can_allocation_property += fusion_count * 10

        can_allocation_property += (user_level // 10) * 10

        return can_allocation_property

    def ready_fight_general_property(self,  user_add_property, choose_arm_type, user_level):
        """
        获取准备战斗时将领的数据值
        :param user_add_property: 用户选择的加点，这个值从前端传入参数，是用户自己分配的加点（根据上面）
        :param choose_arm_type: 用户选择的兵种类型
        :param user_level: 将领的等级
        :return:
        """
        # 只计算原始没有任何其他情况到对应等级的属性
        origin_general_property = self.get_general_property(self.general_info, user_level)
        import ipdb; ipdb.set_trace()
        general_property = {
            "power": round(origin_general_property["power"] + user_add_property["power"], 2),
            "intelligence": round(origin_general_property["intelligence"] + user_add_property["intelligence"], 2),
            "speed": round(origin_general_property["speed"] + user_add_property["speed"], 2),
            "defense": round(origin_general_property["defense"] + user_add_property["defense"], 2),
        }
        if choose_arm_type:
            ext = self._arms_type_to_property(self.general_info["troop_adaptability"].get(choose_arm_type))
            general_property = {key: value * ext for key, value in general_property.items()}

        return general_property


if __name__ == "__main__":
    bs = GeneralService(guanyu)
    import ipdb; ipdb.set_trace()
    can_alloc_property = bs.overall_can_allocation_property(True, False, 5, 45)
    general_values = bs.ready_fight_general_property(
        {"power": 80, "intelligence": 0, "speed": 0, "defense": 20}, "shield", 45
    )
    print(general_values)
