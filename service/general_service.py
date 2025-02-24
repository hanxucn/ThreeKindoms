import logging
from service.skill_service import SkillService
from typing import Optional, List, Dict, Union

# guanyu = {
#     "name": "guanyu",
#     "country": "shu",
#     "basic_power": 97,  # 默认1级初始武力值
#     "power_up": 2.68,  # 每升 1 级提升的武力值
#     "basic_defense": 97,  # 默认 1 级初始防御值
#     "defense_up": 2.04,  # 每升 1 级提升的防御值
#     "basic_intelligence": 79,  # 默认 1 级初始智力值
#     "intelligence_up": 1.05,  # 每升 1 级提升的智力值
#     "basic_speed": 74,  # 默认 1 级初始速度值
#     "speed_up": 1.3,  # 每升 1 级提升的速度值
#     "self_skill": WeizhenhuaxiaSkill,  # 自带战法
#     "type": "normal",  # 普通 or sp
#     # 部队兵种适应度:pike 枪兵 S，shield 盾兵 A, bow 弓箭 C, cavalry 骑兵 S
#     "troop_adaptability": {"pike": "s_level", "shield": "a_level", "bow": "c_level", "cavalry": "s_level"},
#     # "level": 50,  # 45 or 50  这个值从前端传入参数
#     # "add_property": {"power": 50},  # 默认升级全加力量，这里改用前端传递
#     "default_attack_type": "physical",  # 武力 physical  or 谋略 intelligence or 综合 combined
#     "has_dynamic": True,  # 是否有动态人物
#     "take_troops": 10000,  # 默认初始带满兵1W，如果为 45级 则为 95000
# }


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
        name,
        general_info,
        is_dynamic,
        is_classic,
        fusion_count,
        take_troops_type,
        is_leader=False,
        user_level=None,
        equipped_skill_names: Optional[List[Dict[str, str]]] = None,
        user_add_property=None,
    ):
        self.name = name
        # 验证 equipped_skill_names 格式
        if equipped_skill_names is not None:
            if not isinstance(equipped_skill_names, list):
                raise ValueError("equipped_skill_names must be a list")
            for item in equipped_skill_names:
                if not isinstance(item, dict) or "name" not in item or "type" not in item:
                    raise ValueError("Each item in equipped_skill_names must be a dict with 'name' and 'type' keys")

        self.general_info = general_info
        # Change skill_names to store both name and type
        self.skill_names = [{"name": self.general_info["self_skill_name"].get("name"), "type": self.general_info["self_skill_name"].get("type")}]
        if equipped_skill_names:
            self.skill_names.extend([{"name": item.get("name"), "type": item.get("type")} for item in equipped_skill_names])
        self.alive = True
        self.buff = {}
        self.debuff = {}
        self.curr_take_troops = {"current_troops": 10000, "wounded_troops": 0}
        self.is_dynamic = is_dynamic
        self.is_classic = is_classic
        self.fusion_count = fusion_count
        self.take_troops_type = take_troops_type
        self.is_leader = is_leader
        self.user_level = user_level if user_level else 50
        self.can_allocation_property = self.overall_can_allocation_property()
        self.skills = self.get_skills()
        self.skill_types = self.get_skill_types()
        self.default_user_add_property = {
            "power": 0,
            "intelligence": 0,
            "speed": 0,
            "defense": 0
        }
        self.user_add_property = user_add_property
        self.counter_status_list = []
        self.receive_attack_cnt = 0
        self.curr_power = self.general_info["basic_power"] + (self.user_level - 1) * self.general_info["power_up"] + self.user_add_property["power"]
        self.curr_intelligence = self.general_info["basic_intelligence"] + (self.user_level - 1) * self.general_info["intelligence_up"] + self.user_add_property["intelligence"]
        self.curr_speed = self.general_info["basic_speed"] + (self.user_level - 1) * self.general_info["speed_up"] + self.user_add_property["speed"]
        self.curr_defense = self.general_info["basic_defense"] + (self.user_level - 1) * self.general_info["defense_up"] + self.user_add_property["defense"]

    def is_alive(self):
        return self.alive and self.general_info["take_troops"] > 0

    def get_skills(self):
        skills = {}
        skill_service = SkillService()
        for skill_info in self.skill_names:
            skill = skill_service.get_skill(skill_info["name"], skill_info["type"])
            if skill:
                skills[skill_info["name"]] = skill
        return skills

    def get_skill_types(self):
        skill_types = set()
        for skill in self.skills.values():
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

    def set_user_add_property(self, user_add_property):
        self.user_add_property = user_add_property

    def get_user_add_property(self):
        return self.user_add_property

    def take_damage(self, damage):
        wounded_troops = int(damage * 0.9)
        self.curr_take_troops["current_troops"] -= damage
        self.curr_take_troops["wounded_troops"] += wounded_troops
        if self.curr_take_troops["current_troops"] <= 0:
            self.curr_take_troops["current_troops"] = 0
            self.alive = False

    def get_buff(self, status):
        return self.buff.get(status, {})

    def get_debuff(self, status):
        return self.debuff.get(status, {})

    def add_buff(self, status, value, duration=7):
        self.buff[status] = {"value": value, "duration": duration}

    def remove_buff(self, status):
        if status in self.buff:
            del self.buff[status]

    def add_debuff(self, status, value, duration=7):
        self.debuff[status] = {"value": value, "duration": duration}

    def remove_debuff(self, status):
        if status in self.debuff:
            del self.debuff[status]

    def clean_all_debuffs(self):
        self.debuff = {}

    def clean_all_buffs(self):
        self.buff = {}

    def update_statuses(self):
        for status in list(self.buff.keys()):
            self.buff[status]["duration"] -= 1
            if self.buff[status]["duration"] <= 0:
                self.remove_buff(status)

        for status in list(self.debuff.keys()):
            self.debuff[status]["duration"] -= 1
            if self.debuff[status]["duration"] <= 0:
                self.remove_debuff(status)

    def include_skill_type(self):
        skill_types = []
        for skill in self.skills:
            skill_types.append(skill.skill_type)
        return skill_types

    def execute_skills(self, attacker, attackers, defenders, battle_service, turn):
        for skill in self.skills.values():
            skill.apply_effect(attacker, attackers, defenders, battle_service, turn)

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

    def get_general_property(
        self,
        general_info,
        user_add_property=None,
        power_extra=0,
        intelligence_extra=0,
        speed_extra=0,
        defense_extra=0
    ):
        """
        get final property value
        :param general_info: general_info
        :param user_add_property: 用户选择的加点，这个值从前端传入参数，是用户自己分配的加点（根据上面）
        :param power_extra: 额外增加的武力值
        :param intelligence_extra: 额外增加的智力值
        :param speed_extra: 额外增加的速度值
        :param defense_extra: 额外增加的防御值
        :return:
        """
        # 计算将领最终武力基础值 + 等级 * 每级武力提升 + 满级时 50 点属性加成
        power_value = general_info["basic_power"] + (self.user_level - 1) * general_info["power_up"] + power_extra

        intelligence_value = general_info["basic_intelligence"] + (
            self.user_level - 1) * general_info["intelligence_up"] + intelligence_extra

        speed_value = general_info["basic_speed"] + (self.user_level - 1) * general_info["speed_up"] + speed_extra

        defense_value = (
            general_info["basic_defense"] + (self.user_level - 1) * general_info["defense_up"] + defense_extra
        )
        logging.info(f"当前将领 {general_info['name']} 的基础属性计算结果：力量 {power_value}，智力 {intelligence_value}，速度 {speed_value}，防御 {defense_value}")

        if not (self.user_add_property or user_add_property):
            logging.warning("错误：未设置加点属性！")

        user_add_property = self.user_add_property or user_add_property

        general_property = {
            "power": power_value + user_add_property["power"],
            "intelligence": intelligence_value + user_add_property["intelligence"],
            "speed": speed_value + user_add_property["speed"],
            "defense": defense_value + user_add_property["defense"],
        }
        if not self.take_troops_type:
            logging.error("错误：未设置将领兵种类型！")
            raise Exception("Need set general take_troops_type")
        ext = self._arms_type_to_property(self.general_info["troop_adaptability"].get(self.take_troops_type))
        general_property = {key: round((value * ext), 2) for key, value in general_property.items()}
        self.curr_power = general_property["power"]
        self.curr_intelligence = general_property["intelligence"]
        self.curr_speed = general_property["speed"]
        self.curr_defense = general_property["defense"]
        logging.info(f"将领 {general_info['name']} 最终计算属性为：{general_property}")
        return general_property

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


if __name__ == "__main__":
    from config.generals import guanyu

    bs = GeneralService(guanyu["name"], guanyu, True, False, 5, 45)
    can_alloc_property = bs.overall_can_allocation_property()
    general_values = bs.get_general_property(
        bs.general_info,
        {"power": 80, "intelligence": 0, "speed": 0, "defense": 20},
        "shield",
    )
    print(general_values)
