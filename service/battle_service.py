import random

from damage_service import DamageService
from skill_service import QianlizoudanqiSkill


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
        # 记录了被攻击的记录 {"被攻击将领": [("普通攻击来源将领", 记录的回合)]}
        self.normal_attack_records = {general.name: [] for general in self.team1.get_generals() + self.team2.get_generals()}

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
            self.execute_round()
            self.round += 1
        self.determine_winner()

    def execute_round(self):
        actions = []
        for general in self.team1.get_generals() + self.team2.get_generals():
            actions.append((general, general.get_general_property(general.general_info, 50)["speed"]))
        actions.sort(key=lambda x: x[1], reverse=True)

        for action in actions:
            general, speed = action
            if general.is_alive():
                self.execute_action(general, self.round)

        for general in self.team1.get_generals() + self.team2.get_generals():
            general.update_statuses()

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
        debuff = general.debuff
        is_stunned = "is_stunned" in debuff
        is_silenced = "is_silenced" in debuff
        is_disarmed = "is_disarmed" in debuff
        is_discommand = "is_discommand" in debuff
        is_taunted = "is_taunted" in debuff

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

    def select_targets(self, defenders, release_range=1):
        """
        选择攻击目标
        :param defenders: 所有存活的敌方将领
        :param release_range: 攻击范围，1 表示单个目标，2 表示两个目标，3 表示所有目标
        :return: 选择的目标列表
        """
        if release_range == 1:
            return [random.choice(defenders)]
        elif release_range == 2:
            return random.sample(defenders, min(2, len(defenders)))
        elif release_range == 3:
            return defenders
        else:
            raise ValueError("Invalid release_range value")

    def execute_action(self, general, turn):
        # 根据当前状态执行行动
        survive_defenders = [g for g in self.team2.get_generals() if g.is_alive()]
        if not survive_defenders:
            return

        normal_attack_target = self.select_targets(survive_defenders)
        action = self.get_action_based_on_debuffs(general)

        if action == "taunted":
            taunt_targets = [g for g in self.team2.get_generals() if "is_taunted" in g.buff]
            normal_attack_target = taunt_targets[0] if taunt_targets else None

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
            self.normal_attack(general, normal_attack_target)
            return

        # 正常情况下
        general.execute_skills(self.team2.get_generals(), self, turn)
        self.normal_attack(general, normal_attack_target)  # 普通攻击主将

    def record_normal_attack(self, attacker, defender, turn):
        if defender.name not in self.normal_attack_records:
            self.normal_attack_records[defender.name] = []
        self.normal_attack_records[defender.name].append((attacker.name, turn))

    def was_attacked_in_current_round(self, general):
        if general.name in self.normal_attack_records:
            for record in self.normal_attack_records[general.name]:
                if record[1] == self.round:
                    return record[0]
        return None

    def normal_attack(self, attacker, defender, attack_type="physical", skill_coefficient=100):
        damage = self.calculate_damage(attacker, defender, attack_type, skill_coefficient)
        defender.take_damage(damage)
        self.record_normal_attack(attacker, defender, self.round)

    def skill_attack(self, attacker, defenders, skill, targets=None, attacker_attr=None, defender_attr=None):
        """
        处理技能攻击，计算并应用伤害和效果
        :param attacker: 攻击者
        :param defenders: 防御者列表
        :param skill: 技能实例
        :param targets: 目标对象，如果为空则随机选择
        :param attacker_attr: 攻击者属性，如果为空则使用普通的攻击者属性
        :param defender_attr: 防御者属性，如果为空则使用普通的防御者属性
        """

        # 直接技能计算伤害
        if attacker.is_leader:
            skill_effect = attacker.effect.get("leader") if attacker.effect.get("leader") else attacker.effect.get("normal")
        else:
            skill_effect = attacker.effect.get("normal")
        skill_coefficient = skill_effect.get("attack_coefficient", 100)
        release_range = skill_effect.get("release_range", 1)
        if not targets:
            targets = self.select_targets(defenders, release_range)
        for defender in targets:
            damage = self.calculate_damage(attacker, defender, skill.skill_type, skill_coefficient)
            defender.take_damage(damage)

    def calculate_damage(
            self, attacker, defender, attack_type, skill_coefficient=100, attacker_attr=None, defender_attr=None
    ):
        """
        计算伤害
        :param attacker: 攻击者
        :param defender: 被攻击者
        :param attack_type: 攻击类型：physical or intelligent
        :param skill_coefficient: 技能伤害系数，默认 100%
        :param attacker_attr: 攻击者属性，如果为空则使用普通的攻击者属性
        :param defender_attr: 防御者属性，如果为空则使用普通的防御者属性
        :return:
        """
        damage_service = DamageService()
        if attack_type == "physical":
            attacker_key = "power"
            defender_key = "defense"
        elif attack_type == "intelligent":
            attacker_key = defender_key = "intelligence"
        else:
            raise ValueError("Invalid attack type")

        if not attacker_attr:
            attacker_attr = attacker.get_general_property(attacker.general_info)[attacker_key]
        if not defender_attr:
            defender_attr = defender.get_general_property(defender.general_info)[defender_key]

        attacker_basic_bonus = 0
        # 考虑攻击者的增益效果
        for buff_name in attacker.buff:
            if buff_name.startswith("damage_bonus_"):
                attacker_basic_bonus += int(buff_name.split("_")[-1])

        defender_basic_bonus = 0
        # 考虑防御者的增益效果
        for buff_name in defender.buff:
            if buff_name.startswith("damage_reduction_"):
                defender_basic_bonus += int(buff_name.split("_")[-1])

        troop_restriction = damage_service._is_troop_restriction(attacker, defender)

        damage = damage_service.calculate_damage(
            attacker.user_level, defender.user_level, attacker_attr, defender_attr,
            attacker.default_take_troops, defender.default_take_troops,
            attacker.fusion_count, defender.fusion_count, attacker_basic_bonus,
            defender_basic_bonus, 100, troop_restriction, skill_coefficient
        )
        return damage

    def determine_winner(self):
        if not self.team1.is_alive():
            print("Team 2 wins!")
        elif not self.team2.is_alive():
            print("Team 1 wins!")
        else:
            print("It's a draw!")
