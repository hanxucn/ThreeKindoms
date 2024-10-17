import random

from damage_service import DamageService


"""
buff: 增加伤害的数量 -> damage_bonus_<增伤百分数> 
"""


class Skill:
    name = None

    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect):
        self.name = name
        self.skill_type = skill_type
        self.attack_type = attack_type
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

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        raise NotImplementedError("Subclasses should implement this method")


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


class PassiveSkill(Skill):
    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect)
        self.skill_type = "passive"
        self.attack_type = attack_type


class FormationSkill(Skill):
    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect, duration):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect)
        self.duration = duration  # 阵法的持续回合数，箕形阵持续 3 回合，锋矢阵持续 8 回合

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        # 阵法在战斗前指定回合触发
        if current_turn <= self.duration:
            self.effect.apply(battle_service, attackers, defenders, current_turn)


class CommandSkill(Skill):
    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect)

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        return super().apply_effect(skill_own_attacker, attackers, defenders, battle_service, current_turn)


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
    

class ShengqilindiSkill(CommandSkill):
    """
    战斗开始后前2回合，使敌军群体随机（2人）每回合都有90%的几率陷入缴械状态，无法进行普通攻击
    """
    name = "shengqilindi"

    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect, duration):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect)
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
    name = "shengqilindi"

    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect)
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

    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect, self_groups):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect)
        self._init_commander_buff(self_groups)

    def _init_commander_buff(self, self_groups):
        for general_obj in self_groups:
            if not general_obj.is_leader():
                general_obj.add_buff("luanshijianxiong", 10, duration=7)

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        # 友军群体（2人）造成的兵刃伤害和谋略伤害提高16%
        intelligence_factor = 1 + skill_own_attacker.intelligence / 2000  # 假设智力影响比例为每100点智力增加5%
        damage_increase = 16 * intelligence_factor
        allies = battle_service.select_targets(attackers, 2)
        for ally in allies:
            ally.add_buff("physical_damage_increase", damage_increase, duration=7)
            ally.add_buff("intelligent_damage_increase", damage_increase, duration=7)

        # 自己受到的兵刃伤害和谋略伤害降低18%
        damage_reduction = 18 * intelligence_factor
        skill_own_attacker.add_buff("physical_damage_reduction", damage_reduction, duration=7)
        skill_own_attacker.add_buff("intelligent_damage_reduction", damage_reduction, duration=7)


class YingshilangguSkill(CommandSkill):
    """
    指挥技能：鹰视狼顾
    - 战斗前4回合，每回合有80%概率使自身获得7%攻心或奇谋几率（每种效果最多叠加2次）；
    - 第5回合起，每回合对1-2个敌军单体造成谋略伤害（伤害率154%，受智力影响）；
    - 自身为主将时，获得16%奇谋几率。
    """
    name = "yingshilanggu"

    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect)
        self.attack_chance_buff_count = 0  # 记录攻心和奇谋的叠加次数

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        # 如果自身为主将，获得16%奇谋几率
        if skill_own_attacker.is_leader:
            skill_own_attacker.add_buff("intelligent_attack_double", 0.16, duration=7)
        if current_turn <= 4:
            # 战斗前4回合，有80%的概率获得7%攻心或奇谋几率，每种效果最多叠加2次
            if self.is_triggered(0.8):
                buff_type = "intelligent_attack_double" if random.random() < 0.5 else "intelligent_health_double"
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

    # def on_turn_start(self):
    #     # 每回合开始，增加当前回合数
    #     self.current_turn += 1


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


class QianlizoudanqiSkill(PassiveSkill):
    """
    战斗中，自身准备发动自带准备战法时，有70%几率（受武力影响）获得洞察状态（免疫所有控制效果）并提高 50 武力，持续2回合，
    在此期间，自身受到普通攻击时，对攻击者进行一次反击（伤害率238%），每回合最多触发1次
    """
    name = "qianlizoudanqi"

    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect)
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
    name = "qianlizoudanqi"

    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect)

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

    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect)

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        if current_turn == 0:
            skill_own_attacker.add_buff("is_evasion", 0, 3)
        elif current_turn == 3:
            skill_own_attacker.add_buff("intelligence_up", 64, 1)
            battle_service.skill_attack(skill_own_attacker, defenders, self, targets=defenders)


class TroopSkill(Skill):
    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect)

    def apply_effect(self):
        pass


class TengjiabingSkill(TroopSkill):
    """
    我军全体受到兵刃伤害降低24%（受统率影响），但处于灼烧状态时每回合额外损失兵力（伤害率300%）
    """
    def __init__(
            self, name, skill_type, attack_type, quality, source, source_general, target, effect, owner, self_group
    ):
        super().__init__(
            name, skill_type, attack_type, quality, source, source_general, target, effect
        )
        self._init_pre_effect(owner, self_group)

    def _init_pre_effect(self, owner, self_group):
        if owner.take_troops_type == "shield":
            owner_attr = owner.get_general_property(owner.general_info)
            owner_defense = owner_attr["defense"]
            defense_up_factor = round((owner_defense - 100) * 20 / 7000, 2)
            physical_damage_reduction = 24 * (1 + defense_up_factor)  # 如果携带者统帅为350，那么 24* (1+ 500 /700)= 24*1.71=41.04
            for general_obj in self_group:
                general_obj.add_buff("physical_damage_reduction", physical_damage_reduction, duration=7)

class JixingzhenSkill(FormationSkill):
    """
    战斗前3回合，使敌军主将造成伤害降低40%（受武力影响），并使我军随机副将受到兵刃伤害降低18%，另一名副将受到谋略伤害降低18%
    """
    name = "jixingzhen"

    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect, duration):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect, duration)

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        if current_turn <= 3:
            reduction_factor = skill_own_attacker.get_general_property(skill_own_attacker.general_info, 45)["power"] * 0.1
            for defender in defenders:
                if defender.is_leader:
                    value = 40 + reduction_factor
                    defender.add_debuff(f"attack_reduction", value, 3)

            if len(attackers) > 1:
                random_attacker = random.choice(attackers[1:])
                random_attacker.add_buff("physical_damage_reduction", 18, 3)
                index_defender = attackers.index(random_attacker)
                if len(attackers) > 2:
                    attackers[3 - index_defender].add_buff("intelligence_damage_reduction", 18, 3)
            battle_service.skill_attack(battle_service, attackers, defenders, current_turn)
        else:
            reduction_factor = skill_own_attacker.get_general_property(attackers[0].general_info, 45)["power"] * 0.1
            for defender in defenders:
                if defender.is_leader:
                    value = 40 + reduction_factor
                    defender.remove_debuff(f"attack_reduction_{value}")
            for attacker in attackers:
                attacker.remove_buff("physical_damage_reduction_18")
                attacker.remove_buff("intelligence_damage_reduction_18")


if __name__ == "__main__":
    # 创建技能
    skill_weizhenhuaxia = ActiveSkill(
        name="weizhenhuaxia",
        skill_type="prepare_active",
        attack_type="physical",
        quality="S",
        source="self_implemented",
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
                    "status": ["is_disarmed", "is_silenced"],
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
                    "status": ["is_disarmed", "is_silenced"],
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

    skill_yongwutongshen = YongwutongshenSkill(
        name="yongwutongshen",
        skill_type="command",
        attack_type="intelligent",
        quality="S",
        source="inherited",
        source_general="simayi",
        target="enemy_group",
        effect={
            "normal": {
                "probability": 1,
                "release_range": 2
            },
        }
    )

    skill_luanshijianxiong = LuanshijianxiongSkill(
        name="luanshijianxiong",
        skill_type="command",
        attack_type="",
        quality="S",
        source="self_implemented",
        source_general="caocao",
        target="self_group",
        effect={},
        self_groups=[],
    )

    skill_yingshilanggu = YingshilangguSkill(
        name="yingshilanggu",
        skill_type="command",
        attack_type="intelligent",
        quality="S",
        source="self_implemented",
        source_general="simayi",
        target="enemy_group",
        effect={
            "normal": {
                "probability": 1,
                "self_buff": [
                    {
                        "name": "intelligent_attack_double",
                        "duration": 7,
                        "damage_bonus": 200,
                        "release_probability": 7,
                        "probability": 0.8
                    },
                    {
                        "name": "intelligent_health_double",
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
                        "name": "intelligent_attack_double",
                        "duration": 7,
                        "damage_bonus": 200,
                        "release_probability": 0.16,
                        "probability": 1
                    },
                    {
                        "name": "intelligent_attack_double",
                        "duration": 7,
                        "damage_bonus": 200,
                        "release_probability": 7,
                        "probability": 0.8
                    },
                    {
                        "name": "intelligent_health_double",
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
    )

    skill_weimoumikang = ActiveSkill(
        name="weimoumikang",
        skill_type="prepare_active",
        attack_type="physical",
        quality="S",
        source="inherited",
        source_general=None,
        target="enemy_group",
        effect={
            # normal 表示正常情况下的技能描述； leader 表示如果装备此战法的为主将有不同的技能描述
            "normal": {
                "probability": 0.4,
                "attack_coefficient": 158,  # 此为 DamageService 里的 skill_coefficient
                "release_range": 2,
                "target": "enemy",
                "to_enemy_buff": {
                    "status": ["is_weakness"],
                    "release_range": 2,
                    "duration": 2,
                },
                "status_probability": 1,
            }
        },
        activation_type="prepare",
    )

    skill_hengsaoqianjun = ActiveSkill(
        name="hengsaoqianjun",
        skill_type="instant_active",
        attack_type="physical",
        quality="S",
        source="inherited",
        source_general=None,
        target="enemy_group",
        effect={
            "normal": {
                "probability": 0.4,
                "attack_coefficient": 100,  # 此为 DamageService 里的 skill_coefficient
                "release_range": 3,
                "target": "enemy",
                "to_enemy_buff": {
                    "prerequisite ": ["is_disarmed", "is_silenced"],
                    "status": ["is_taunted"],
                    "release_range": 3,
                    "duration": 1,
                },
                "status_probability": 0.3,
            }
        },
        activation_type="instant",
    )

    skill_jiangmenhunv = ActiveSkill(
        name="jiangmenhunv",
        skill_type="instant_active",
        attack_type="physical",
        quality="S",
        source="self_implemented",
        source_general="guanyinping",
        target="enemy_group",
        effect={
            "normal": {
                "probability": 0.6,
                "release_range": 2,
                "target": "enemy",
                "attack_coefficient": 128,
                "to_enemy_buff": {
                    "prerequisite ": {"target_attack_count": 3},
                    "status": ["is_taunted"],
                    "release_range": 2,
                    "duration": 1,
                    "additional_damage_coefficient": 20,  # 拥有虎嗔状态时，收到伤害时额外增加20%伤害，最多叠加三次
                },
                "status_probability": 1,
            },
        },
        activation_type="instant",
    )

    skill_jiangdongmenghu = ActiveSkill(
        name="jiangdongmenghu",
        skill_type="instant_active",
        attack_type="physical",
        quality="S",
        source="self_implemented",
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
                "release_range": 2,
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

    skill_jifengzhouyu = JifengzhouyuSkill(
        name="jifengzhouyu",
        skill_type="instant_active",
        attack_type="physical",
        quality="S",
        source="inherited",
        source_general="sp-zhangliang,sp-zhangbao",
        target="enemy_single",
        effect={
            "normal": {
                "probability": 0.4,
                "release_range": 1,
                "target": "enemy",
                "attack_coefficient": 78,
                "status": ["is_nohealing"],
                "status_duration": 1,
            }
        },
        activation_type="instant",
    )

    skill_qianlizoudanqi = PassiveSkill(
        name="qianlizoudanqi",
        skill_type="passive",
        attack_type="physical",
        quality="S",
        source="events",
        source_general=None,
        target="self",
        effect={
            "normal": {
                "attack_coefficient": 238
            }
        }

    )

    skill_yanrenpaoxiao = PassiveSkill(
        name="yanrenpaoxiao",
        skill_type="passive",
        attack_type="physical",
        quality="S",
        source="self_implemented",
        source_general="zhangfei",
        target="enemy_group",
        effect={
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
        },
    )

    skill_shibiesanri = PassiveSkill(
        name="shibiesanri",
        skill_type="passive",
        attack_type="intelligent",
        quality="S",
        source="inherited",
        source_general="lvmeng",
        target="enemy_group",
        effect={
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
        },
    )

    skill_shimianmaifu = ActiveSkill(
        name="十面埋伏",
        skill_type="prepare_active",
        attack_type="intelligence",
        quality="S",
        source="自带战法",
        source_general="程昱",
        target="enemy_group",
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
        attack_type="intelligence",
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
                "attack_coefficient": 88
            }
        },
    )
