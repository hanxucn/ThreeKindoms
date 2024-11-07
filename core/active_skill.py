import random

from base_skill import Skill


class ActiveSkill(Skill):
    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect, activation_type="prepare"):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect)
        self.activation_type = activation_type
        self.skill_type = "active"
        self.attack_type = attack_type
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

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        if self.trigger_list[current_turn]:
            if self.activation_type == "prepare":
                self.prepare_effect(attackers[0], defenders, battle_service)
            elif self.activation_type == "instant":
                self.instant_effect(attackers[0], defenders, battle_service)

    def prepare_effect(self, attacker, defenders, battle_service):
        pass

    def instant_effect(self, attacker, defenders, battle_service):
        # Implement the instant effect logic for your specific skill here
        pass


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

    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect, activation_type):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect, activation_type)
        self.trigger_list = self.simulate_trigger(self.effect["leader"]["probability"])
        self.counter_status_list = self._counter_status_list()
        source_general.counter_status_list = self.counter_status_list

    def _counter_status_list(self):
        counter_status_list = [False * 8]
        if not self.trigger_list:
            self.trigger_list = self.simulate_trigger(self.effect["leader"]["probability"])
        for turn, trigger_status in enumerate(self.trigger_list):
            if turn == 0:
                continue
            if trigger_status:
                counter_status_list[turn-1] = True
        return counter_status_list

    def prepare_effect(self, attacker, defenders, battle_service):
        if attacker.is_leader:
            skill_effect = self.effect["leader"]
        else:
            skill_effect = self.effect["normal"]
        for defender in defenders:
            if self.is_triggered(skill_effect.get("status_probability", 0)):
                defender.add_debuff("is_disarmed", 0, 1)  # 缴械
            if self.is_triggered(skill_effect.get("status_probability", 0)):
                defender.add_debuff("is_silenced", 0, 1)  # 计穷
        if "damage_bonus" in skill_effect.get("self_buff", {}):
            damage_bonus = skill_effect["self_buff"]["damage_bonus"]
            attacker.add_buff(f"damage_bonus", damage_bonus, 2)

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        if self.trigger_list[current_turn]:
            self.prepare_effect(skill_own_attacker, defenders, battle_service)

            battle_service.skill_attack(skill_own_attacker, defenders, self, targets=defenders)


class WeiMouMiKangSkill(ActiveSkill):
    """
    准备1回合，对敌军群体（2人）施加虚弱（无法造成伤害）状态，持续2回合；
    如果目标已处于虚弱状态则使其陷入叛逃状态，每回合持续造成伤害（伤害率158%，受武力或智力最高一项影响，无视防御），持续2回合
    """
    name = "weimoumikang"

    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect, activation_type):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect, activation_type)
        self.trigger_list = self.simulate_trigger(self.effect["normal"]["probability"])

    def prepare_effect(self, attacker, defenders, battle_service):
        skill_effect = self.effect["normal"]
        for defender in defenders:
            if self.is_triggered(skill_effect.get("probability", 0)):
                if "is_weakness" in defender.debuff:
                    attacker.add_buff("ignore_defense", 0, 1)  # 无视防御
                else:
                    defender.add_debuff("is_weakness", 0, 2)  # 虚弱

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        if self.trigger_list[current_turn]:
            self.prepare_effect(skill_own_attacker, defenders, battle_service)

            battle_service.skill_attack(skill_own_attacker, defenders, self, targets=defenders)
            skill_own_attacker.remove_buff("ignore_defense")


class HengsaoqianjunSkill(ActiveSkill):
    """
    对敌军全体造成100%兵刃伤害，若目标已处于缴械或计穷状态则有30%概率使目标处于震慑状态（无法行动），持续1回合
    """
    name = "hengsaoqianjun"

    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect, activation_type):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect, activation_type)
        self.trigger_list = self.simulate_trigger(self.effect["normal"]["probability"])

    def instant_effect(self, attacker, defenders, battle_service):
        skill_effect = self.effect["normal"]
        for defender in defenders:
            if self.is_triggered(skill_effect.get("probability", 0)):
                if "is_disarmed" in defender.debuff or "is_silenced" in defender.debuff:
                    if self.is_triggered(0.3):
                        defender.add_debuff("is_taunted", 0, 1)  # 震慑

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        if self.trigger_list[current_turn]:
            self.instant_effect(skill_own_attacker, defenders, battle_service)

            battle_service.skill_attack(skill_own_attacker, defenders, self, targets=defenders)


class JifengzhouyuSkill(ActiveSkill):
    """
    随机对敌军武将发动3-4次兵刃攻击（伤害率78%，每次提升6%），第3次和第4次攻击额外附带1回合禁疗状态
    """
    name = "jifengzhouyu"

    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect, activation_type):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect, activation_type)
        self.trigger_list = self.simulate_trigger(self.effect["normal"]["probability"])

    def instant_effect(self, attacker, defenders, battle_service):
        skill_effect = self.effect["normal"]
        for defender in defenders:
            if self.is_triggered(skill_effect.get("probability", 0)):
                defender.add_debuff("is_nohealing", 0, 1)  # 禁疗

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        if self.trigger_list[current_turn]:
            self.instant_effect(skill_own_attacker, defenders, battle_service)

            battle_service.skill_attack(skill_own_attacker, defenders, self, targets=defenders)


class GuaguliaoduSkill(ActiveSkill):
    """
    刮骨疗毒：为损失兵力最高的我军单体清除负面状态并为其恢复兵力（治疗率256%，受智力影响）
    """
    name = "guaguliaodu"

    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect)

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        # 选择损失兵力最多的友军
        target = max(attackers, key=lambda ally: ally.curr_take_troops["wounded_troops"])

        # 清除负面状态
        target.clean_all_debuffs()

        # 使用 battle_service 的 skill_heal 方法进行治疗
        battle_service.skill_heal(
            healer=skill_own_attacker,
            skill=self,
            self_groups=attackers,
            targets=[target],
            heal_extra_amount=target.get_general_property(skill_own_attacker.general_info)["intelligence"],
            custom_coefficient=256,
        )
