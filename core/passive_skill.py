import random

from core.base_skill import Skill


class PassiveSkill(Skill):
    name = None
    effect = {}

    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target)
        self.skill_type = "passive"
        self.attack_type = attack_type


class QianlizoudanqiSkill(PassiveSkill):
    """
    战斗中，自身准备发动自带准备战法时，有70%几率（受武力影响）获得洞察状态（免疫所有控制效果）并提高 50 武力，持续2回合，
    在此期间，自身受到普通攻击时，对攻击者进行一次反击（伤害率238%），每回合最多触发1次
    """
    name = "qianlizoudanqi"
    effect = {"normal": {"attack_coefficient": 238}}

    def __init__(
        self,
        name="qianlizoudanqi",
        skill_type="passive",
        attack_type="passive",
        quality="S",
        source="events",
        source_general=None,
        target="self",
    ):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target)
        self.counter_triggered = False

    def check_and_apply_effect(self, battle_service, attacker, current_turn):
        if attacker.is_self_preparing_skill() and self.is_triggered_by_power(attacker):
            attacker.add_buff("insight", 0, 2)
            attacker.add_buff("power_up", 50, 2)
            print(f"获得洞察状态并提高50武力，持续2回合。")

    def is_triggered_by_power(self, attacker):
        power = attacker.get_general_property(attacker.general_info, 45)["power"]
        probability = min(1, 0.7 + power / 1000)  # 受武力影响的触发概率
        return random.random() < probability

    def counter_attack(self, defender, attacker):
        attack_attr = None
        defend_attr = None
        if not self.counter_triggered:
            power_up = 50 if attacker.buff.get("power_up_50") else 0
            attack_attr = attacker.get_general_property(defender.general_info)["power"] + power_up
            defend_attr = defender.get_general_property(attacker.general_info)["defense"]
            # damage = damage_service.calculate_damage(
            #     attacker.user_level, defender.user_level, attack_attr, defend_attr,
            #     attacker.default_take_troops, defender.default_take_troops,
            #     attacker.fusion_count, defender.fusion_count, 10, 10, 100, False, self.effect["counter_damage_rate"]
            # )
            # attacker.take_damage(damage)
            self.counter_triggered = True
            print(f"触发反击效果。")
        return attack_attr, defend_attr

    def is_get_normal_attack(self, attacker, battle_service, current_turn):
        normal_attack_records = battle_service.normal_attack_records.get(attacker.name)
        if normal_attack_records and current_turn in normal_attack_records:
            return True
        return False

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        if skill_own_attacker.counter_status_list and current_turn < len(skill_own_attacker.counter_status_list):
            if (
                skill_own_attacker.counter_status_list[current_turn] and
                self.is_get_normal_attack(skill_own_attacker, battle_service, current_turn)
            ):
                self.check_and_apply_effect(battle_service, skill_own_attacker, current_turn)
                attack_source = battle_service.was_attacked_in_current_round(skill_own_attacker)
                if attack_source:
                    attack_attr, defend_attr = self.counter_attack(skill_own_attacker, attack_source)
                    battle_service.skill_attack(
                        skill_own_attacker,
                        attack_source,
                        self,
                        targets=attack_source,
                        attacker_attr=attack_attr,
                        defender_attr=defend_attr,
                    )
                    self.reset_counter()

    def reset_counter(self):
        self.counter_triggered = False


class YanrenpaoxiaoSkill(PassiveSkill):
    """
    战斗第2、4回合，对敌军全体造成兵刃攻击（伤害率104%）；若目标处于缴械状态或计穷状态，则额外使目标统率降低50%，持续2回合，
    自身为主将时，第6回合对敌军全体发动兵刃攻击（伤害率88%）
    """
    name = "yanrenpaoxiao"
    effect = {
        "normal": {
            "attack_coefficient": 104,
            "release_range": 3,
            "target": "enemy",
            "release_turn_with_attack_coefficient": {2: 104, 4: 104},
            "to_enemy_buff": {
                "status": ["defense_reduction"],
                "duration": 2,
                "value": -50,
                "prerequisite": ["is_disarmed", "is_silenced"],
            },
        },
        "leader": {
            "attack_coefficient": 104,
            "release_range": 3,
            "target": "enemy",
            "release_turn_with_attack_coefficient": {2: 104, 4: 104, 6: 88},
            "to_enemy_buff": {
                "status": ["defense_reduction"],
                "duration": 2,
                "value": -50,
                "prerequisite": ["is_disarmed", "is_silenced"],
            },
        },
    }

    def __init__(
        self,
        name="yanrenpaoxiao",
        skill_type="passive",
        attack_type="physical",
        quality="S",
        source="self_implemented",
        source_general="zhangfei",
        target="enemy_group",
    ):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target)

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        trigger_list = [False] * 8
        trigger_list[1] = trigger_list[3] = True
        if skill_own_attacker.is_leader:
            trigger_list[5] = True
        if trigger_list[current_turn]:
            if current_turn == 5:
                self.effect["leader"]["attack_coefficient"] = 88
            battle_service.skill_attack(skill_own_attacker, defenders, self, targets=defenders)


class ShibiesanriSkill(PassiveSkill):
    """
    战斗前3回合，无法进行普通攻击但获得30%概率规避效果，第4回合提高自己64点智力并对敌军全体造成谋略伤害（伤害率180%，受智力影响）
    """
    name = "shibiesanri"
    effect = {
        "normal": {
            "probability": 1,
            "attack_coefficient": 180,
            "release_range": 3,
            "target": "enemy",
            "self_buff": {
                "status": ["is_evasion"],  # 规避状态
                "duration": 3,
                "buff_probability": 0.3,
            },
        },
    }

    def __init__(
        self,
        name="shibiesanri",
        skill_type="passvie",
        attack_type="intelligence",
        quality="S",
        source="inherited",
        source_general="lvmeng",
        target="enemy_group",
    ):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target)

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        if current_turn == 0:
            skill_own_attacker.add_buff("is_evasion", 0, 3)
        elif current_turn == 3:
            skill_own_attacker.add_buff("intelligence_up", 64, 1)
            battle_service.skill_attack(skill_own_attacker, defenders, self, targets=defenders)


class MeihuoSkill(PassiveSkill):
    """
    自己受到普通攻击时，有45%几率使攻击者进入混乱（攻击和战法无差别选择目标）、计穷（无法发动主动战法）、虚弱（无法造成伤害）状态的一种，持续1回合，
    自身为女性时，触发几率额外受智力影响
    """
    name = "meihuo"
    effect = {
        "normal": {
            "probability": 1,
            "attack_coefficient": 0,
            "release_range": 1,
            "target": "enemy",
            "to_enemy_buff": {
                "status": ["is_confusion", "is_silenced", "is_weakness"],  # 混乱 技穷 虚弱
                "duration": 1,
                "buff_probability": 0.45,
            },
        },
    }

    def __init__(
        self,
        name="meihuo",
        skill_type="passive",
        attack_type="",
        quality="S",
        source="inherited",
        source_general="zhenji",
        target="enemy_single",
    ):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target)

    def on_receive_attack(self, attacker, skill_own_attacker):
        # 基础触发概率为45%
        trigger_probability = 0.45

        # 如果持有技能的人物是女性，则概率额外受到智力的加成
        if skill_own_attacker.gender == "female":
            skill_own_attr = skill_own_attacker.get_general_property(skill_own_attacker.general_info)
            intelligence_factor = round((skill_own_attr["intelligence"] - 100) * 20 / 7000, 2)
            trigger_probability = 0.45 + (1 + intelligence_factor)

        # 检查是否触发技能效果
        if random.random() < trigger_probability:
            # 随机选择一种负面状态
            negative_effects = ["is_confusion", "is_silenced", "is_weakness"]
            chosen_effect = random.choice(negative_effects)

            # 对攻击者施加负面状态，持续1回合
            attacker.add_debuff(chosen_effect, 0, duration=1)
