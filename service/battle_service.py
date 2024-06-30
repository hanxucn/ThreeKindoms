
class BattleService:
    def __init__(self, own_team, enemy_team):
        self.own_team = own_team
        self.enemy_team = enemy_team

    def prepare_battle(self):
        # 准备阶段：计算每个将领的属性值，检查指挥类型战法和兵种类型战法
        for team in [self.own_team, self.enemy_team]:
            for general in team.generals:
                for skill in general.skills:
                    if skill.skill_type == 'command':
                        skill.apply_effect(general, team.generals, self)
                    elif skill.skill_type == 'troop':
                        skill.apply_effect(general, team.generals, self)

    def simulate_battle(self):
        # 战斗阶段：模拟8个回合的战斗
        for round_cnt in range(1, 9):
            if not self.own_team.is_alive() or not self.enemy_team.is_alive():
                break
            self.simulate_round()

    def simulate_round(self):
        # 根据速度和先攻状态决定行动顺序
        all_generals = self.own_team.get_generals() + self.enemy_team.get_generals()
        all_generals.sort(key=lambda x: (-x.speed, -x.attr))  # 先按速度排序，再按属性值排序

        for general in all_generals:
            if not general.is_alive():
                continue
            # 执行将领的技能
            if general in self.own_team.generals:
                general.execute_skills(self.enemy_team.get_generals(), self)
            else:
                general.execute_skills(self.own_team.get_generals(), self)
