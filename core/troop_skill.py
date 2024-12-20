from core.base_skill import Skill


class TroopSkill(Skill):
    def __init__(self, name, skill_type, attack_type, quality, source, source_general, target, effect):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect)

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        pass


class TengjiabingSkill(TroopSkill):
    """
    我军全体受到兵刃伤害降低24%（受统率影响），但处于灼烧状态时每回合额外损失兵力（伤害率300%）
    """
    name = "tengjiabing"
    attack_type = "",
    quality = "S",
    source = "self_implemented",
    source_general = "wangping",
    target = "self_team",
    effect = {
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
    }

    def __init__(
        self,
        name="tengjiabing",
        skill_type="troop",
        attack_type="",
        quality="S",
        source="inherited",
        source_general="",
        target="self_group",
        effect=None,
    ):
        super().__init__(name, skill_type, attack_type, quality, source, source_general, target, effect)

    def _init_pre_effect(self, owner, self_group):
        if owner.take_troops_type == "shield":
            buff_name = "physical_damage_reduction"
            debuff_name = "tengjia_burning_up"
            owner_attr = owner.get_general_property(owner.general_info)
            owner_defense = owner_attr["defense"]
            defense_up_factor = round((owner_defense - 100) * 20 / 7000, 2)
            physical_damage_reduction = 24 * (1 + defense_up_factor)  # 如果携带者统帅为350，那么 24* (1+ 500 /700)= 24*1.71=41.04
            for general_obj in self_group:
                buff_value = 0
                if general_obj.get_buff(buff_name):
                    buff_value = general_obj.get_buff(buff_name)["value"] or 0
                general_obj.add_buff(buff_name, buff_value + physical_damage_reduction, duration=7)
                general_obj.add_debuff(debuff_name, 3, duration=7)

    def apply_effect(self, skill_own_attacker, attackers, defenders, battle_service, current_turn):
        if current_turn == 0:
            self._init_pre_effect(skill_own_attacker, attackers)


class WuDangFeiJunSkill(TroopSkill):
    """
    我军全体统率、速度提高22点，首回合对敌军群体（2人）施加中毒状态，每回合持续造成伤害（伤害率80%，受智力影响），持续3回合；若王平统领，对敌军全体施加中毒状态，但伤害率降低（伤害率66%，受智力影响
    """
    name = "wudangfeijun"
