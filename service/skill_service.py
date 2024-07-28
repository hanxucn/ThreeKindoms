import random

from damage_service import DamageService


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
    def __init__(self, name, skill_type, quality, source, source_general, target, effect, activation_type, healing_rate):
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
    name = "weizhenhuaxia"

    def __init__(self, name, skill_type, quality, source, source_general, target, effect, activation_type):
        super().__init__(name, skill_type, quality, source, source_general, target, effect, activation_type)
        self.trigger_list = self.simulate_trigger(self.effect['normal']['probability'])

    def prepare_effect(self, attacker, defenders, battle_service):
        for defender in defenders:
            if random.random() < self.effect['normal']['status_probability']:
                defender.add_debuff("no_normal_attack", 1)  # 缴械
            if random.random() < self.effect['normal']['status_probability']:
                defender.add_debuff("no_skill_release", 1)  # 计穷
            damage = battle_service.calculate_damage(
                attacker, defender, "physical", self.effect['normal']['attack_coefficient']
            )
            defender.take_damage(damage)
        attacker.add_buff("damage_bonus", self.effect['normal']['self_buff']['damage_bonus'])

    def apply_effect(self, battle_service, attacker, defenders, current_turn):
        if self.trigger_list[turn]:
            if self.activation_type == "prepare" and turn + 1 < len(self.trigger_list):
                self.trigger_list[turn + 1] = True
            else:
                self.prepare_effect(attacker, defenders, battle_service)


class QianlizoudanqiSkill(PassiveSkill):
    name = "qianlizoudanqi"

    def __init__(self, name, skill_type, quality, source, source_general, target, effect):
        super().__init__(name, skill_type, quality, source, source_general, target, effect)
        self.counter_triggered = False

    def check_and_apply_effect(self, battle_service, attacker, current_turn):
        if attacker.is_self_preparing_skill() and self.is_triggered_by_power(attacker):
            attacker.add_buff("insight", 2)
            attacker.add_buff("power_boost", 2)
            print(f"{attacker.general_info['name']}获得洞察状态并提高50武力，持续2回合。")

    def is_triggered_by_power(self, attacker):
        power = attacker.get_general_property(attacker.general_info, 45)["power"]
        probability = min(1, 0.7 + power / 1000)  # 受武力影响的触发概率
        return random.random() < probability

    def counter_attack(self, defender, attacker, battle_service):
        if not self.counter_triggered:
            damage_service = DamageService()
            attack_attr = defender.get_general_property(defender.general_info, 45)["power"]
            defend_attr = attacker.get_general_property(attacker.general_info, 45)["defense"]
            damage = damage_service.calculate_damage(
                50, 50, attack_attr, defend_attr,
                defender.default_take_troops, attacker.default_take_troops,
                10, 10, 10, 10, 100, False, self.effect['counter_damage_rate']
            )
            attacker.take_damage(damage)
            self.counter_triggered = True
            print(f"{defender.general_info['name']}反击{attacker.general_info['name']}，造成{damage}点伤害。")

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
        target="group",
        effect={
            # normal 表示正常情况下的技能描述； leader 表示如果装备此战法的为主将有不同的技能描述
            "normal": {
                "probability": 0.35,
                "attack_coefficient": 1.46,  # 此为 DamageService 里的 skill_coefficient
                "release_range": "all",
                "target": "enemy",
                "to_enemy_buff": {
                    "status": ["no_normal_attack", "no_skill_release"],
                    "release_range": "all",
                    "duration": 1,
                },
                "status_probability": 0.5,
                "self_buff": {
                    "type": "physical_damage",
                    "damage_bonus": 1.36,
                    "duration": 2,
                }
            },
            "leader": {
                "probability": 0.35,
                "attack_coefficient": 1.46,
                "release_range": "all",
                "target": "enemy",
                "to_enemy_buff": {
                    "status": ["no_normal_attack", "no_skill_release"],
                    "release_range": "all",
                    "duration": 1,
                },
                "status_probability": 0.65,
                "self_buff": {
                    "type": "physical_damage",
                    "damage_bonus": 1.36,
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
        target="group",
        effect={
            "normal": {
                "probability": 0.5,
                "release_range": "2",
                "target": "enemy",
                "attack_coefficient": 1.26,
                "status": ["taunt"],
                "status_duration": 2
            },
            "leader": {
                "probability": 0.5,
                "release_range": "2",
                "target": "enemy",
                "attack_coefficient": 1.26,
                "status": ["taunt"],
                "status_duration": 2,
                "self_buff": {
                    "injury_tolerance": 0.8
                }
            }

        },
        activation_type="instant",
    )

    skill_shimianmaifu = ActiveSkill(
        name="十面埋伏",
        skill_type="prepare_active",
        quality="S",
        source="自带战法",
        source_general="程昱",
        target="group",
        effect={
            "probability": 0.35,
            "coefficient": 74,
            # 禁疗状态和叛逃状态
            "status": ["no_healing", "defection"],
            "status_duration": 2,
            "attack_coefficient": 0.96
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
                "attack_coefficient": 0.8
            }
        },
    )
