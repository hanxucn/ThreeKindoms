import random
import math

from skill_service import WeizhenhuaxiaSkill


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
    "self_skill": WeizhenhuaxiaSkill,  # 自带战法
    "type": "normal",  # 普通 or sp
    # 部队兵种适应度:pike 枪兵 S，shield 盾兵 A, bow 弓箭 C, cavalry 骑兵 S
    "troop_adaptability": {"pike": "s_level", "shield": "a_level", "bow": "c_level", "cavalry": "s_level"},
    # "level": 50,  # 45 or 50  这个值从前端传入参数
    # "add_property": {"power": 50},  # 默认升级全加力量，这里改用前端传递
    "default_attack_type": "physical",  # 武力 physical  or 谋略 intelligence or 综合 combined
    "has_dynamic": True,  # 是否有动态人物
    "take_troops": 10000,  # 默认初始带满兵1W，如果为 45级 则为 95000
}


class GeneralService:
    # 每个人物初始化时需要填入任务的基本信息和可分配的属性，
    #
    # is_dynamic: 是否是动态人物， 如果是会多 10 的属性分配
    # is_classic: 是否典藏，如果是会多 10 的属性分配
    # fusion_count: 进阶数，每进阶一个红度会减伤 2% 和增加对敌人伤害 2%，且多 10 点属性分配
    # take_troops_type: 初始带兵类型，有 4 种类型，分别为：盾兵 shield, 骑兵 cavalry, 弓箭 bow, 枪兵 pike
    # is_leader: 人物是否为主将
    # user_level: 人物等级
    # equipped_skills: 人物装配的其他两个技能
    # user_add_property：可分配属性，需要先调用 overall_can_allocation_property() 方法计算，由前端提供值
    def __init__(
            self,
            general_info,
            is_dynamic,
            is_classic,
            fusion_count,
            take_troops_type,
            is_leader=False,
            user_level=None,
            equipped_skills=None,
            user_add_property=None
    ):
        self.general_info = general_info
        self.skills = [self.general_info.self_skill].extend(equipped_skills)
        self.alive = True
        self.buff = {}
        self.debuff = {}
        self.default_take_troops = 10000
        self.is_dynamic = is_dynamic
        self.is_classic = is_classic
        self.fusion_count = fusion_count
        self.take_troops_type = take_troops_type
        self.is_leader = is_leader
        self.user_level = user_level if user_level else 50
        self.can_allocation_property = self.overall_can_allocation_property()
        self.skill_types = self.get_skill_types()
        self.default_user_add_property = {
            "power": self.can_allocation_property,
            "intelligence": 0,
            "speed": 0,
            "defense": 0
        }
        self.user_add_property = user_add_property
        self.counter_status_list = []

    def is_alive(self):
        return self.alive and self.general_info["take_troops"] > 0

    def get_skill_types(self):
        skill_types = set()
        for skill in self.skills:
            skill_types.add(skill.skill_type)
        return list(skill_types)

    def has_command_or_troop_skill(self):
        if "command" in self.skill_types or "troop" in self.skill_types:
            return True
        return False

    def has_active_or_troop_skill(self):
        if "active" in self.skill_types or "troop" in self.skill_types:
            return True
        return False

    def has_troop_skill(self):
        if "troop" in self.skill_types:
            return True
        return False

    def only_has_assault_skill(self):
        # 当人物只装备了突击战法
        if self.skill_types and len(self.skill_types) == 1 and self.skill_types[0] == "assault":
            return True
        return False

    def only_has_passive_skill(self):
        # 当人物只装备了被动战法
        if self.skill_types and len(self.skill_types) == 1 and self.skill_types[0] == "passive":
            return True
        return False

    def only_has_command_skill(self):
        # 当人物只装备了指挥战法
        if self.skill_types and len(self.skill_types) == 1 and self.skill_types[0] == "command":
            return True
        return False

    def get_user_add_property(self):
        return self.user_add_property

    def take_damage(self, damage):
        self.general_info["take_troops"] -= damage
        if self.general_info["take_troops"] <= 0:
            self.general_info["take_troops"] = 0
            self.alive = False

    def add_buff(self, status, duration):
        self.buff[status] = duration

    def remove_buff(self, status):
        if status in self.buff:
            del self.buff[status]

    def add_debuff(self, status, duration):
        self.debuff[status] = duration

    def remove_debuff(self, status):
        if status in self.debuff:
            del self.debuff[status]

    def update_statuses(self):
        for status in list(self.buff.keys()):
            self.buff[status] -= 1
            if self.buff[status] <= 0:
                self.remove_buff(status)

        for status in list(self.debuff.keys()):
            self.debuff[status] -= 1
            if self.debuff[status] <= 0:
                self.remove_debuff(status)

    def include_skill_type(self):
        skill_types = []
        for skill in self.skills:
            skill_types.append(skill.skill_type)
        return skill_types

    def execute_skills(self, defenders, battle_service, turn):
        for skill in self.skills:
            skill.apply_effect(self, battle_service, self.general_info, defenders, turn)

    def is_self_preparing_skill(self):
        if self.general_info.get("self_skill")().skill_type == "prepare_active":
            return True
        return False

    def receive_attack(self, attacker, battle_service):
        if "insight" in self.buff:
            for skill in self.skills:
                if skill.name == "qianlizoudanqi":
                    skill.counter_attack(self, attacker, battle_service)

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

    def get_general_property(self, general_info):
        """
        get final property value
        :param general_info: general_info
        :return:
        """
        # 计算将领最终武力基础值 + 等级 * 每级武力提升 + 满级时 50 点属性加成
        power_value = general_info["basic_power"] + (self.user_level - 1) * general_info["power_up"]

        intelligence_value = general_info["basic_intelligence"] + (
                self.user_level - 1) * general_info["intelligence_up"]

        speed_value = general_info["basic_speed"] + (self.user_level - 1) * general_info["speed_up"]

        defense_value = general_info["basic_defense"] + (self.user_level - 1) * general_info["defense_up"]

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

    def overall_can_allocation_property(self) -> int:
        """
        :return: overall can allocation user property
        """
        can_allocation_property = 0
        if self.general_info["has_dynamic"] and self.is_dynamic:
            can_allocation_property += 10

        if self.is_classic:
            can_allocation_property += 10

        if self.fusion_count < 0 or self.fusion_count > 5:
            raise Exception("user advanced count should between 0 ~ 5")
        can_allocation_property += self.fusion_count * 10

        can_allocation_property += (self.user_level // 10) * 10

        return can_allocation_property

    def ready_fight_general_property(self,  user_add_property, choose_arm_type):
        """
        获取准备战斗时将领的数据值，此数值计算为开始战斗前的最终属性数值。会影响
        :param user_add_property: 用户选择的加点，这个值从前端传入参数，是用户自己分配的加点（根据上面）
        :param choose_arm_type: 用户选择的兵种类型
        :return:
        """
        # 只计算原始没有任何其他情况到对应等级的属性
        origin_general_property = self.get_general_property(self.general_info)
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
    bs = GeneralService(guanyu, True, False, 5, 45)
    can_alloc_property = bs.overall_can_allocation_property()
    general_values = bs.ready_fight_general_property(
        {"power": 80, "intelligence": 0, "speed": 0, "defense": 20}, "shield"
    )
    print(general_values)
