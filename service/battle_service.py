import random

from damage_service import DamageService


class BattleService:
    """
    战斗系统需要计算一个最多8回合的战斗，包括准备阶段和战斗阶段。敌我双方开始阶段为各3人。且其分为1个主将和2个副将。
    每个人物除了有一个自带的战法外，还需要装备两个其他战法。战法类型分为指挥战法、主动战法、被动战法、兵种战法、阵法和突击战法。
    战斗回合过程中需要根据6个人的速度快慢来决定每回合的行动顺序。如果人物带有先攻状态，则视为可以先行动。
    如果多个人物带有先攻状态，则带有先攻状态的人物按照速度排序。然后是没有先攻状态的人物进行速度排序。
    如果人物带有震慑状态，则当前回合行动时候无法普通攻击和技能释放，但是如果自身带有指挥战法或者被动战法或者兵种战法是可以正常释放的。
    如果人物带有缴械状态，则当前回合行动时候无法普通攻击，但是如果自身带有指挥战法或者被动战法或者兵种战法是可以正常释放的。
    如果人物带有伪报状态，则当前回合人物指挥、被动战法暂时失效，但普通攻击和技能释放仍然有效。
    如果人物带有被嘲讽状态，则在行动回合必须强制性普通攻击释放嘲讽状态的人物。
    在战斗过程中以双方谁的主将首先阵亡，谁为输家。如果战斗的8个回合双方主将仍然存活，即视为平局。
    =====
    战斗服务初始化时需要填入己方三人和对方三人的 general 人物信息，然后传入选择两方使用的兵种
    """
    def __init__(self, own_team, enemy_team, own_team_arm_type, enemy_team_arm_type):
        # each team has three generals
        self.team1 = own_team
        self.team2 = enemy_team
        self.own_team_arm_type = own_team_arm_type
        self.enemy_team_arm_type = enemy_team_arm_type
        self.round = 0

    def prepare_battle(self):
        # 准备阶段：计算每个将领的属性值
        for team in [self.team1, self.team2]:
            for general in team.generals:
                user_add_property = general.get_user_add_property()
                ready_value = general.ready_fight_general_property(user_add_property, self.own_team_arm_type)
                general.general_info.update(ready_value)

    def start_battle(self):
        self.prepare_battle()
        while self.round < 8 and self.team1[0].is_alive() and self.team2[0].is_alive():
            self.execute_round(self.round)
            self.round += 1
        self.determine_winner()

    def execute_round(self):
        actions = []
        for general in self.team1.get_generals() + self.team2.get_generals():
            actions.append((general, general.get_general_property(general.general_info, 45)["speed"]))
        actions.sort(key=lambda x: x[1], reverse=True)

        for action in actions:
            general, speed = action
            if general.is_alive():
                self.execute_action(general, self.round)

        # 重置反击触发状态
        for general in self.team1.get_generals() + self.team2.get_generals():
            for skill in general.skills:
                if skill.name == "qianlizoudanqi":
                    skill.reset_counter()

    def get_debuff_status(self, general):
        debuffs = general.debuff
        is_stunned = "is_stunned" in debuffs
        is_silenced = "is_silenced" in debuffs
        is_disarmed = "is_disarmed" in debuffs
        is_discommand = "is_discommand" in debuffs
        is_taunted = "is_taunted" in debuffs
        return {
            "is_stunned": is_stunned,
            "is_silenced": is_silenced,
            "is_disarmed": is_disarmed,
            "is_discommand": is_discommand,
            "is_taunted": is_taunted,
        }

    def get_action_based_on_debuffs(self, general):
        debuffs = general.debuff
        is_stunned = "is_stunned" in debuffs
        is_silenced = "is_silenced" in debuffs
        is_disarmed = "is_disarmed" in debuffs
        is_discommand = "is_discommand" in debuffs
        is_taunted = "is_taunted" in debuffs

        # 震慑状态（技穷+缴械）：不能普通攻击和释放主动、突击技能；可以发动指挥、兵种和阵法
        if is_stunned or (is_silenced and is_disarmed):
            return "stunned"

        # 缴械状态 + 伪报状态：不能普通攻击和指挥、被动战法，但可以释放主动战法和兵种战法
        if is_disarmed and is_discommand:
            return "disarmed_discommand"

        # 震慑状态 + 伪报状态：不能进行任何行动，但兵种战法可用
        if (is_stunned or (is_silenced and is_disarmed)) and is_discommand:
            return "stunned_discommand"

        # 缴械状态：不能普通攻击，但可以释放技能
        if is_disarmed:
            return "disarmed"

        # 伪报状态：指挥战法和被动战法失效，但可以释放技能和普通攻击
        if is_discommand:
            return "discommand"

        # 嘲讽状态：必须攻击嘲讽状态的人物
        if is_taunted:
            return "taunted"

        # 正常情况下
        return "normal"

    def execute_action(self, general, turn):
        # 根据当前状态执行行动
        survive_defenders = [g for g in self.team2.get_generals() if g.is_alive()]
        if not survive_defenders:
            return
        target = random.choice(survive_defenders)

        action = self.get_action_based_on_debuffs(general)

        if action == "taunted":
            taunt_targets = [g for g in self.team2.get_generals() if "is_taunted" in g.buff]
            target = taunt_targets[0]

        if action == "stunned":
            if general.has_command_or_troop_skill():
                general.execute_skills(self.team2.get_generals(), self, turn)
            return

        if action == "disarmed_discommand":
            if general.has_active_or_troop_skill():
                general.execute_skills(self.team2.get_generals(), self, turn)
            return

        if action == "stunned_discommand":
            if general.has_troop_skill():
                general.execute_skills(self.team2.get_generals(), self, turn)
            return

        if action == "disarmed":
            if general.only_has_assault_skill():
                return
            general.execute_skills(self.team2.get_generals(), self, turn)
            return

        if action == "discommand":
            if general.only_has_passive_skill() or general.only_has_command_skill():
                return
            general.execute_skills(self.team2.get_generals(), self, turn)
            self.normal_attack(general, target)
            return

        for skill in general.skills:
            if skill.name == "qianlizoudanqi":
                skill.check_and_apply_effect(self, general, turn)

        # 正常情况下
        general.execute_skills(self.team2.get_generals(), self, turn)
        self.normal_attack(general, target)  # 普通攻击主将

    def normal_attack(self, attacker, defender):
        damage = self.calculate_damage(attacker, defender, attack_type="physical")
        defender.take_damage(damage)

    def calculate_damage(self, attacker, defender, attack_type):
        # 这里可以调用之前的 DamageService 来计算伤害
        damage_service = DamageService()
        if attack_type == "physical":

            attacker_attr = attacker.get_general_property(attacker.general_info, 45)["power"]
            defender_attr = defender.get_general_property(defender.general_info, 45)["defense"]
            return damage_service.calculate_damage(
                50, 50, attacker_attr, defender_attr,
                attacker.default_take_troops, defender.default_take_troops,
                10, 10, 10,
                10, 100, False, 100
            )
        elif attack_type == "intelligent":
            attacker_attr = attacker.get_general_property(attacker.general_info, 45)["intelligence"]
            defender_attr = defender.get_general_property(defender.general_info, 45)["intelligence"]
            return damage_service.calculate_damage(
                50, 50, attacker_attr, defender_attr,
                attacker.default_take_troops, defender.default_take_troops,
                10, 10, 10,
                10, 100, False, 100
            )

    def determine_winner(self):
        if not self.team1.is_alive():
            print("Team 2 wins!")
        elif not self.team2.is_alive():
            print("Team 1 wins!")
        else:
            print("It's a draw!")
