import random

from damage_service import DamageService


"""
buff: 增加伤害的数量 -> damage_bonus_<增伤百分数> 
"""


class Skill:
    name = None

    def __init__(self, name, skill_type, quality, source, source_general, target, effect):
        self.name = name
        self.skill_type = skill_type
        self.quality = quality
        self.source = source
        self.source_general = source_general
        self.target = target
        self.effect = effect

    def is_triggered(self, probability) -> bool:
        """
        Determine if a skill is triggered based on the given probability.

        Args:
        probability (float): The probability of triggering the skill, represented as a percentage (0-100).

        Returns:
        bool: True if the skill is triggered, False otherwise.
        """
        return random.random() < probability

    def simulate_trigger(self, probability, turns=8):
        """Simulate skill trigger status for each turn"""
        return [self.is_triggered(probability) for _ in range(turns)]

    def apply_effect(self, battle_service, attacker, defenders, current_turn):
        raise NotImplementedError("Subclasses should implement this method")


class ActiveSkill(Skill):
    def __init__(self, name, skill_type, quality, source, source_general, target, effect, activation_type="prepare"):
        super().__init__(name, skill_type, quality, source, source_general, target, effect)
        self.activation_type = activation_type
        self.skill_type = "active"
        self.trigger_list = self.simulate_trigger(self.effect.get("probability", 1))

    def active_skill_type(self, battle_service, attacker, defenders):
        if self.is_triggered(self.effect.get("probability", 1)):
            # 如果是准备战法，当此回合判定 is_triggered 发动成功，战法效果会在下一回合开始
            if self.activation_type == "prepare":
                self.prepare_effect(attacker, defenders, battle_service)
            # 如果是瞬时战法，当此回合判定 is_triggered 发动成功，战法效果会在人物当前回合开始
            elif self.activation_type == "instant":
                self.instant_effect(attacker, defenders, battle_service)

    def simulate_trigger(self, probability, turns=8):
        """Simulate skill trigger status for each turn"""
        trigger_list = [False] * turns
        if self.activation_type == "instant":
            trigger_list = [self.is_triggered(probability) for _ in range(turns)]
        elif self.activation_type == "prepare":
            for turn in range(turns):
                if self.is_triggered(probability):
                    if turn + 1 < turns:
                        trigger_list[turn + 1] = True
        return trigger_list

    def apply_effect(self, battle_service, attacker, defenders, current_turn):
        if self.trigger_list[current_turn]:
            if self.activation_type == "prepare":
                self.prepare_effect(attacker, defenders, battle_service)
            elif self.activation_type == "instant":
                self.instant_effect(attacker, defenders, battle_service)

    def prepare_effect(self, attacker, defenders, battle_service):
        pass

    def instant_effect(self, attacker, defenders, battle_service):
        # Implement the instant effect logic for your specific skill here
        pass


class PassiveSkill(Skill):
    def __init__(self, name, skill_type, quality, source, source_general, target, effect):
        super().__init__(name, skill_type, quality, source, source_general, target, effect)
        self.skill_type = "passive"


class HealingSkill(ActiveSkill):
    def __init__(
            self, name, skill_type, quality, source, source_general, target, effect, activation_type, healing_rate
    ):
        super().__init__(name, skill_type, quality, source, source_general, target, effect, activation_type)
        self.healing_rate = healing_rate

    def instant_effect(self, attacker, defenders, battle_service):
        # Implementing healing logic
        for defender in defenders:
            if random.random() < self.effect.get("probability"):
                healing_amount = self.calculate_healing(attacker)
                defender.heal(healing_amount)
                print(f"{self.name} heals {defender.name} for {healing_amount} troops.")

    def calculate_healing(self, attacker):
        highest_stat = max(attacker.strength, attacker.intelligence)
        return highest_stat * self.healing_rate


class WeizhenhuaxiaSkill(ActiveSkill):
    """
    准备1回合，对敌军全体进行猛攻（伤害率146%），使其有50%概率进入缴械（无法进行普通攻击）、计穷（无法发动主动战法）状态，
    独立判定，持续1回合，并使自己造成的兵刃伤害提升36%，持续2回合；自身为主将时，造成控制效果的概率提高65%
    """
    name = "weizhenhuaxia"

    def __init__(self, name, skill_type, quality, source, source_general, target, effect, activation_type):
        super().__init__(name, skill_type, quality, source, source_general, target, effect, activation_type)
        self.trigger_list = self.simulate_trigger(self.effect["normal"]["probability"])

    def prepare_effect(self, attacker, defenders, battle_service):
        if attacker.is_leader:
            skill_effect = self.effect["leader"]
        else:
            skill_effect = self.effect["normal"]
        for defender in defenders:
            if self.is_triggered(skill_effect.get("status_probability", 0)):
                defender.add_debuff("is_disarmed", 1)  # 缴械
            if self.is_triggered(skill_effect.get("status_probability", 0)):
                defender.add_debuff("is_silenced", 1)  # 计穷
        if "damage_bonus" in skill_effect.get("self_buff", {}):
            damage_bonus = skill_effect["self_buff"]["damage_bonus"]
            attacker.add_buff(f"damage_bonus_{damage_bonus}", 2)

    def apply_effect(self, battle_service, attacker, defenders, current_turn):
        if self.trigger_list[current_turn]:
            battle_service.skill_attack(attacker, defenders, self)


class QianlizoudanqiSkill(PassiveSkill):
    """
    战斗中，自身准备发动自带准备战法时，有70%几率（受武力影响）获得洞察状态（免疫所有控制效果）并提高50武力，持续2回合，
    在此期间，自身受到普通攻击时，对攻击者进行一次反击（伤害率238%），每回合最多触发1次
    """
    name = "qianlizoudanqi"

    def __init__(self, name, skill_type, quality, source, source_general, target, effect):
        super().__init__(name, skill_type, quality, source, source_general, target, effect)
        self.counter_triggered = False

    def check_and_apply_effect(self, battle_service, attacker, current_turn):
        if attacker.is_self_preparing_skill() and self.is_triggered_by_power(attacker):
            attacker.add_buff("insight", 2)
            attacker.add_buff("power_up_50", 2)
            print(f"获得洞察状态并提高50武力，持续2回合。")

    def is_triggered_by_power(self, attacker):
        power = attacker.get_general_property(attacker.general_info, 45)["power"]
        probability = min(1, 0.7 + power / 1000)  # 受武力影响的触发概率
        return random.random() < probability

    def counter_attack(self, defender, attacker, battle_service):
        if not self.counter_triggered:
            damage_service = DamageService()
            power_up = 50 if attacker.buff.get("power_up_50") else 0
            attack_attr = attacker.get_general_property(defender.general_info)["power"] + power_up
            defend_attr = defender.get_general_property(attacker.general_info)["defense"]
            damage = damage_service.calculate_damage(
                attacker.user_level, defender.user_level, attack_attr, defend_attr,
                attacker.default_take_troops, defender.default_take_troops,
                attacker.fusion_count, defender.fusion_count, 10, 10, 100, False, self.effect["counter_damage_rate"]
            )
            attacker.take_damage(damage)
            self.counter_triggered = True
            print(f"执行反击，造成{damage}点伤害。")

    def is_get_normal_attack(self, attacker, battle_service, current_turn):
        normal_attack_records = battle_service.normal_attack_records.get(attacker.name)
        if normal_attack_records and current_turn in normal_attack_records:
            return True
        return False

    def apply_effect(self, battle_service, attacker, defenders, current_turn):
        attack_source = battle_service.was_attacked_in_current_round(attacker)
        if attack_source:
            self.counter_attack(attacker, attack_source, battle_service)

    def reset_counter(self):
        self.counter_triggered = False


if __name__ == "__main__":
    # 创建技能
    skill_weizhenhuaxia = ActiveSkill(
        name="威震华夏",
        skill_type="prepare_active",
        quality="S",
        source="自带战法",
        source_general="关羽",
        target="enemy_group",
        effect={
            # normal 表示正常情况下的技能描述； leader 表示如果装备此战法的为主将有不同的技能描述
            "normal": {
                "probability": 0.35,
                "attack_coefficient": 146,  # 此为 DamageService 里的 skill_coefficient
                "release_range": 3,
                "target": "enemy",
                "to_enemy_buff": {
                    "status": ["no_normal_attack", "no_skill_release"],
                    "release_range": 3,
                    "duration": 1,
                },
                "status_probability": 0.5,
                "self_buff": {
                    "type": "physical_damage",
                    "damage_bonus": 36,
                    "duration": 2,
                }
            },
            "leader": {
                "probability": 0.35,
                "attack_coefficient": 146,
                "release_range": 3,
                "target": "enemy",
                "to_enemy_buff": {
                    "status": ["no_normal_attack", "no_skill_release"],
                    "release_range": 3,
                    "duration": 1,
                },
                "status_probability": 0.65,
                "self_buff": {
                    "type": "physical_damage",
                    "damage_bonus": 36,
                    "duration": 2,
                }
            }
        },
        activation_type="prepare",
    )

    skill_jiangdongmenghu = ActiveSkill(
        name="江东猛虎",
        skill_type="instant_active",
        quality="S",
        source="自带战法",
        source_general="孙坚",
        target="enemy_group",
        effect={
            "normal": {
                "probability": 0.5,
                "release_range": "2",
                "target": "enemy",
                "attack_coefficient": 126,
                "status": ["taunt"],
                "status_duration": 2
            },
            "leader": {
                "probability": 0.5,
                "release_range": "2",
                "target": "enemy",
                "attack_coefficient": 126,
                "status": ["taunt"],
                "status_duration": 2,
                "self_buff": {
                    "damage_reduction": -20
                }
            }

        },
        activation_type="instant",
    )

    skill_qianlizoudanqi = PassiveSkill(
        name="qianlizoudanqi",
        skill_type="passive",
        quality="S",
        source="events",
        source_general=None,
        target="self",
        effect={
            "normal": {

            }
        }

    )

    skill_shimianmaifu = ActiveSkill(
        name="十面埋伏",
        skill_type="prepare_active",
        quality="S",
        source="自带战法",
        source_general="程昱",
        target="group",
        effect={
            "normal": {
                "probability": 0.35,
                "coefficient": 74,
                "release_range": "2",
                # 禁疗状态和叛逃状态
                "status": ["no_healing", "defection"],
                "status_duration": 2,
                "attack_coefficient": 96,
            }
        },
        activation_type="prepare",
    )

    skill_wudangfeijun = Skill(
        name="无当飞军",
        skill_type="troop",
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
                "attack_coefficient": 880
            }
        },
    )
