import random

from damage_service import DamageService


class Skill:
    def __init__(self, name, skill_type, quality, source, source_general, target, probability, effect):
        self.name = name
        self.skill_type = skill_type
        self.quality = quality
        self.source = source  # 自带战法或传承战法
        self.source_general = source_general  # 来源武将
        self.target = target  # 目标类型（单体或群体）
        self.probability = probability  # 发动概率
        self.effect = effect  # 战法效果描述

    def apply_effect(self, attacker, defenders, battle_service):
        if self.skill_type == 'active':
            return self.apply_active_effect(attacker, defenders, battle_service)
        elif self.skill_type == 'command':
            return self.apply_command_effect(attacker, defenders, battle_service)
        elif self.skill_type == 'troop':
            return self.apply_troop_effect(attacker, defenders, battle_service)
        elif self.skill_type == 'assault':
            return self.apply_assault_effect(attacker, defenders, battle_service)

    def apply_active_effect(self, attacker, defenders, battle_service):
        if random.random() < self.probability:
            print(f"{attacker.name}发动了战法{self.name}")
            if self.target == 'single':
                target = random.choice(defenders)
                self.apply_damage_and_effects(attacker, [target], battle_service)
            elif self.target == 'group':
                targets = random.sample(defenders, min(2, len(defenders)))
                self.apply_damage_and_effects(attacker, targets, battle_service)
                self.apply_follow_up_effects(attacker, defenders, battle_service)

    def apply_damage_and_effects(self, attacker, targets, battle_service):
        for target in targets:
            damage = battle_service.calculate_damage(
                attacker.level, target.level, attacker.attr, target.attr,
                attacker.troops, target.troops, attacker.advanced_bonus,
                target.advanced_bonus, attacker.basic_bonus, target.basic_bonus,
                attacker.speed, self.effect['coefficient'], self.effect.get('special_damage_bonus', 1)
            )
            target.take_damage(damage)
            print(f"{attacker.name}对{target.name}造成了{damage}点伤害，{target.name}剩余兵力{target.troops}")

            # 处理状态效果
            if 'status' in self.effect:
                for status in self.effect['status']:
                    target.add_status(status, self.effect['status_duration'])
                    print(f"{target.name}进入{status}状态，持续{self.effect['status_duration']}回合")

    def apply_follow_up_effects(self, attacker, defenders, battle_service):
        for target in defenders:
            if target.has_negative_status():
                damage = battle_service.calculate_damage(
                    attacker.level, target.level, attacker.attr, target.attr,
                    attacker.troops, target.troops, attacker.advanced_bonus,
                    target.advanced_bonus, attacker.basic_bonus, target.basic_bonus,
                    attacker.speed, self.effect['follow_up_coefficient'], self.effect.get('special_damage_bonus', 1)
                )
                target.take_damage(damage)
                print(f"{attacker.name}对{target.name}进行后续攻击造成了{damage}点伤害，{target.name}剩余兵力{target.troops}")

    def apply_command_effect(self, attacker, defenders, battle_service):
        if self.target == 'self_team':
            for general in battle_service.own_team.get_generals():
                for buff, amount in self.effect.items():
                    general.add_buff(buff, amount)
                    print(f"{general.name}获得了{buff}提升，数量{amount}")
        elif self.target == 'enemy_team':
            for general in battle_service.enemy_team.get_generals():
                for debuff, amount in self.effect.items():
                    general.add_debuff(debuff, amount)
                    print(f"{general.name}受到了{debuff}效果，数量{amount}")

    def apply_troop_effect(self, attacker, defenders, battle_service):
        if self.target == 'self_team':
            for general in battle_service.own_team.get_generals():
                if general.attr['兵种'] == self.effect['required_troop']:
                    for buff, amount in self.effect['buffs'].items():
                        general.add_buff(buff, amount)
                        print(f"{general.name}因兵种战法{self.name}获得了{buff}提升，数量{amount}")
            if 'initial_effect' in self.effect:
                for target in random.sample(defenders, min(2, len(defenders))):
                    target.add_status(self.effect['initial_effect']['status'], self.effect['initial_effect']['duration'])
                    print(f"{target.name}进入{self.effect['initial_effect']['status']}状态，持续{self.effect['initial_effect']['duration']}回合")

    def apply_assault_effect(self, attacker, defender, battle_service):
        if random.random() < self.probability:
            print(f"{attacker.name}发动了突击战法{self.name}")
            damage = battle_service.calculate_damage(
                attacker.level, defender.level, attacker.attr, defender.attr,
                attacker.troops, defender.troops, attacker.advanced_bonus,
                defender.advanced_bonus, attacker.basic_bonus, defender.basic_bonus,
                attacker.speed, self.effect['coefficient'], self.effect.get('special_damage_bonus', 1)
            )
            defender.take_damage(damage)
            print(f"{attacker.name}对{defender.name}造成了{damage}点伤害，{defender.name}剩余兵力{defender.troops}")
            if 'status' in self.effect:
                for status in self.effect['status']:
                    defender.add_status(status, self.effect['status_duration'])
                    print(f"{defender.name}进入{status}状态，持续{self.effect['status_duration']}回合")


if __name__ == "__main__":
    # 创建技能
    skill_weizhenhuaxia = Skill(
        name="威震华夏",
        skill_type="active",
        quality="S",
        source="自带战法",
        source_general="关羽",
        target="group",
        probability=0.35,
        effect={
            "coefficient": 146,
            "special_damage_bonus": 1.36,
            "status": ["缴械", "计穷"],
            "status_probability": 0.5,
            "status_duration": 1,
            "self_buff": {
                "type": "兵刃伤害",
                "amount": 36,
                "duration": 2,
                "main_general_bonus": 0.65
            }
        }
    )

    skill_jiangdongmenghu = Skill(
        name="江东猛虎",
        skill_type="active",
        quality="S",
        source="自带战法",
        source_general="孙坚",
        target="group",
        probability=0.5,
        effect={
            "coefficient": 103,
            "status": ["嘲讽"],
            "status_duration": 2
        }
    )

    skill_shimianmaifu = Skill(
        name="十面埋伏",
        skill_type="active",
        quality="S",
        source="自带战法",
        source_general="程昱",
        target="group",
        probability=0.35,
        effect={
            "coefficient": 74,
            "status": ["禁疗", "叛逃"],
            "status_duration": 2,
            "follow_up_coefficient": 96
        }
    )

    skill_wudangfeijun = Skill(
        name="无当飞军",
        skill_type="troop",
        quality="S",
        source="自带战法",
        source_general="王平",
        target="self_team",
        probability=1.0,
        effect={
            "required_troop": "弓兵",
            "buffs": {
                "统率": 22,
                "速度": 22
            },
            "initial_effect": {
                "status": "中毒",
                "duration": 3,
                "coefficient": 80
            }
        }
    )
