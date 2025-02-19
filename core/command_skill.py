import random

from core.base_skill import Skill


class CommandSkill(Skill):
    name = None
    effect = {}

    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target)

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        return super().apply_effect(skill_own_attacker, attackers, defenders, battle_service, current_turn)


class ShengqilindiSkill(CommandSkill):
    """
    战斗开始后前2回合，使敌军群体随机（2人）每回合都有90%的几率陷入缴械状态，无法进行普通攻击
    """
    name = "shengqilindi"

    def __init__(
        self,
        name="shengqilindi",
        skill_type="command",
        attack_type="control",
        quality="S",
        source="inherited",
        source_general="caopi,yanliang",
        target="enemy_group",
        duration=2,
    ):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target)
        self.duration = duration

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        # 只在战斗前2回合生效
        if current_turn <= 2:
            # 随机选择敌军两人
            affected_defenders = random.sample(defenders, min(2, len(defenders)))
            for defender in affected_defenders:
                # 90%的几率使敌人陷入缴械状态
                if random.random() < 0.9:
                    defender.add_debuff("is_disarmed", 0, self.duration)


class YongwutongshenSkill(CommandSkill):
    """
    战斗开始的第2、4、6、8回合，对敌军群体（2人）逐渐造成75%、105%、135%、165%谋略伤害（受智力影响）
    """
    name = "yongwutongshen",
    effect = {
        "normal": {
            "probability": 1,
            "release_range": 2
        },
    }

    def __init__(
        self,
        name="yongwutongshen",
        skill_type="command",
        attack_type="intelligence",
        quality="S",
        source="inherited",
        source_general="simayi",
        target="enemy_group",
    ):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target)
        self.damage_schedule = {1: 75, 3: 105, 5: 135, 7: 165}  # 指定每个回合的伤害系数

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        # 仅在指定的回合数发动效果
        if current_turn in self.damage_schedule:
            skill_coefficient = self.damage_schedule[current_turn]
            release_range = 2  # 每次攻击2个敌人
            targets = battle_service.select_targets(defenders, release_range)
            # 使用 battle_service 的 skill_attack 方法来处理技能伤害计算
            battle_service.skill_attack(
                attacker=skill_own_attacker,
                defenders=defenders,
                skill=self,
                targets=targets,
                custom_coefficient=skill_coefficient  # 使用自定义伤害系数
            )


class LuanshijianxiongSkill(CommandSkill):
    """
    战斗中，使友军群体（2人）造成的兵刃伤害和谋略伤害提高16%（受智力影响），自己受到的兵刃伤害和谋略伤害降低18%（受智力影响），
    如果自己为主将，副将造成伤害时，会为主将恢复其伤害量10%的兵力
    """
    name = "luanshijianxiong"

    def __init__(
        self,
        name="luanshijianxiong",
        skill_type="command",
        attack_type="",
        quality="S",
        source="self_implemented",
        source_general="caocao",
        target="self_group",
    ):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target)

    def _init_commander_buff(self, self_groups):
        for general_obj in self_groups:
            if not general_obj.is_leader:
                general_obj.add_buff("luanshijianxiong", 10, duration=7)

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        if current_turn == 0:
            self._init_commander_buff(attackers)
        # 友军群体（2人）造成的兵刃伤害和谋略伤害提高16%
        intelligence_factor = 1 + skill_own_attacker.curr_intelligence / 2000  # 假设智力影响比例为每100点智力增加5%
        damage_increase = 16 * intelligence_factor
        allies = battle_service.select_targets(attackers, 2)
        for ally in allies:
            ally.add_buff("physical_damage_increase", damage_increase, duration=7)
            ally.add_buff("intelligence_damage_increase", damage_increase, duration=7)

        # 自己受到的兵刃伤害和谋略伤害降低18%
        damage_reduction = 18 * intelligence_factor
        skill_own_attacker.add_buff("physical_damage_reduction", damage_reduction, duration=7)
        skill_own_attacker.add_buff("intelligence_damage_reduction", damage_reduction, duration=7)
        battle_service.skill_attack(
            current_user=skill_own_attacker,
            defenders=defenders,
            skill=self,
            targets=defenders,
            is_damage_skill=False,
            self_group=attackers,
        )


class YingshilangguSkill(CommandSkill):
    """
    指挥技能：鹰视狼顾
    - 战斗前4回合，每回合有80%概率使自身获得7%攻心或奇谋几率（每种效果最多叠加2次）；
    - 第5回合起，每回合对1-2个敌军单体造成谋略伤害（伤害率154%，受智力影响）；
    - 自身为主将时，获得16%奇谋几率。
    """
    name = "yingshilanggu"
    effect = {
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

    def __init__(
        self,
        name="yingshilanggu",
        skill_type="command",
        attack_type="intelligence",
        quality="S",
        source="self_implemented",
        source_general="simayi",
        target="enemy_group",
    ):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target)
        self.attack_chance_buff_count = 0  # 记录攻心和奇谋的叠加次数

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        # 如果自身为主将，获得16%奇谋几率
        if skill_own_attacker.is_leader:
            skill_own_attacker.add_buff("intelligence_attack_double", 0.16, duration=7)
        if current_turn <= 4:
            # 战斗前4回合，有80%的概率获得7%攻心或奇谋几率，每种效果最多叠加2次
            if self.is_triggered(0.8):
                buff_type = "intelligence_attack_double" if random.random() < 0.5 else "intelligence_health_double"
                if self.attack_chance_buff_count < 2:
                    buff_info = skill_own_attacker.get_buff(buff_type)
                    if buff_info:
                        skill_own_attacker.add_buff(buff_type, buff_info["value"] + 0.07, duration=7)
                    else:
                        skill_own_attacker.add_buff(buff_type, 0.07, duration=7)
                    self.attack_chance_buff_count += 1
        elif current_turn >= 4:
            # 第5回合起，每回合对1-2个敌军单体造成谋略伤害
            battle_service.skill_attack(skill_own_attacker, defenders, self, targets=defenders)


class ZhenefangjuSkill(CommandSkill):
    """
    指挥技能：镇扼防拒
    - 每回合有50%概率（受智力影响）使我军单体（优先选除自己之外的副将）援护所有友军并获得休整状态
    - 休整状态：每回合恢复一次兵力，治疗率192%，受智力影响，持续1回合
    - 同时使其在1回合内受到普通攻击时，有55%概率（受智力影响）移除攻击者的增益状态
    """
    name = "zhenefangju"

    def __init__(
        self,
        name="zhenefangju",
        skill_type="command",
        attack_type="",
        quality="S",
        source="self_implemented",
        source_general="mancong",
        target="self_single",
    ):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target)

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        # 每回合有50%概率（受智力影响）选择我军单体获得效果
        intelligence_factor = 1 + skill_own_attacker.curr_intelligence / 1000  # 假设智力影响比例为每100点智力增加10%
        trigger_probability = 0.5 * intelligence_factor

        if self.is_triggered(trigger_probability):
            # 优先选择除自己外的副将
            potential_targets = [ally for ally in attackers if ally != skill_own_attacker and not ally.is_leader]
            if not potential_targets:
                potential_targets = [ally for ally in attackers if ally != skill_own_attacker]

            if potential_targets:
                target = random.choice(potential_targets)
                # 使目标获得援护所有友军的状态
                target.add_buff("guard_all", value=0, duration=1)
                # 获得休整状态，治疗率192%，受智力影响
                heal_coefficient = 192
                target.add_buff("is_restoration", heal_coefficient, duration=1)

                # 受到普通攻击时，有55%概率移除攻击者的增益状态
                remove_buff_probability = 0.55 * intelligence_factor
                target.add_buff("remove_attacker_buff_on_attack", remove_buff_probability, duration=1)
