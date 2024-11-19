
import random

from base_skill import Skill


class FormationSkill(Skill):
    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect, duration):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect)
        self.duration = duration  # 阵法的持续回合数，箕形阵持续 3 回合，锋矢阵持续 8 回合

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        # 阵法在战斗前指定回合触发
        if current_turn <= self.duration:
            self.effect.apply(battle_service, attackers, defenders, current_turn)


class JixingzhenSkill(FormationSkill):
    """
    战斗前3回合，使敌军主将造成伤害降低40%（受武力影响），并使我军随机副将受到兵刃伤害降低18%，另一名副将受到谋略伤害降低18%
    """
    name = "jixingzhen"

    def __init__(
        self,
        name="jixingzhen",
        skill_type="formation",
        attack_type="",
        quality="S",
        source="inherited",
        source_general="guanyinping,sp-yuansao",
        target=None,
        effect=None,
        duration=3,
    ):
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


class FengshizhenSkill(FormationSkill):
    """
    战斗中，使我军主将造成的伤害提升30%，受到的伤害提升20%；我军副将造成的伤害降低15%，受到的伤害降低25%
    """
    name = "fengshizhen"

    def __init__(
        self,
        name="fengshizhen",
        skill_type="formation",
        attack_type="",
        quality="S",
        source="inherited",
        source_general="huangyueying,yuejin",
        target="self_group",
        effect=None,
        duration=8,
    ):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect, duration)

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        for general in attackers:
            if general.is_leader:
                general.add_buff("intelligence_damage_increase", 30, duration=7)
                general.add_buff("physical_damage_increase", 30, duration=7)
                general.add_debuff("damage_taken_increase", 20, duration=7)
            else:
                # 副将伤害降低和受到伤害降低
                general.add_debuff("physical_damage_reduction", 15, duration=7)
                general.add_debuff("intelligence_damage_reduction", 15, duration=7)
                general.add_buff("damage_taken_reduction", 25, duration=0)
