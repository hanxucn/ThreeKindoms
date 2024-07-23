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
    """
    def __init__(self, own_team, enemy_team):
        # each team has three generals
        self.team1 = own_team
        self.team2 = enemy_team
        self.round = 0

    def prepare_battle(self):
        # 准备阶段：计算每个将领的属性值
        for team in [self.team1, self.team2]:
            for general in team.generals:
                ready_value = general.ready_fight_general_property()
                general.general_info.update(ready_value)

    def start_battle(self):
        while self.round < 8 and self.team1.is_alive() and self.team2.is_alive():
            self.round += 1
            self.execute_round()
        self.determine_winner()

    def execute_round(self):
        actions = []
        for general in self.team1.get_generals() + self.team2.get_generals():
            if "先攻" in general.statuses:
                actions.append((general, "先攻", general.get_general_property(general.general_info, 45)["speed"]))
        actions.sort(key=lambda x: x[2], reverse=True)

        for action in actions:
            general, status, speed = action
            if general.is_alive():
                self.execute_action(general)

    def execute_action(self, general):
        # 根据当前状态执行行动
        if "震慑" in general.statuses:
            return  # 震慑状态下不能行动
        if "缴械" in general.statuses:
            general.execute_skills(self.team2.get_generals(), self)  # 不能普通攻击，但可以释放技能
            return
        if "伪报" in general.statuses:
            general.execute_skills(self.team2.get_generals(), self)  # 指挥战法和被动战法失效，但可以释放技能
            return
        if "嘲讽" in general.statuses:
            target = [g for g in self.team2.get_generals() if "嘲讽" in g.statuses]
            if target:
                self.normal_attack(general, target[0])
            return
        general.execute_skills(self.team2.get_generals(), self)  # 正常释放技能
        self.normal_attack(general, self.team2.get_generals()[0])  # 普通攻击主将

    def normal_attack(self, attacker, defender):
        damage = self.calculate_damage(attacker, defender)
        defender.take_damage(damage)

    def calculate_damage(self, attacker, defender):
        # 这里可以调用之前的 DamageService 来计算伤害
        damage_service = DamageService()
        attacker_attr = attacker.get_general_property(attacker.general_info, 45)["power"]
        defender_attr = defender.get_general_property(defender.general_info, 45)["defense"]
        return damage_service.calculate_damage(
            45, 45, attacker_attr, defender_attr,
            attacker.general_info["take_troops"], defender.general_info["take_troops"],
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

    # def simulate_battle(self):
    #     # 战斗阶段：模拟8个回合的战斗
    #     for round_cnt in range(1, 9):
    #         if not self.own_team.is_alive() or not self.enemy_team.is_alive():
    #             break
    #         self.simulate_round()
    #
    # def simulate_round(self):
    #     # 根据速度和先攻状态决定行动顺序
    #     all_generals = self.own_team.get_generals() + self.enemy_team.get_generals()
    #     all_generals.sort(key=lambda x: (-x.speed, -x.attr))  # 先按速度排序，再按属性值排序
    #
    #     for general in all_generals:
    #         if not general.is_alive():
    #             continue
    #         # 执行将领的技能
    #         if general in self.own_team.generals:
    #             general.execute_skills(self.enemy_team.get_generals(), self)
    #         else:
    #             general.execute_skills(self.own_team.get_generals(), self)
