import importlib

from core.base_skill import Skill


"""
buff: 增加伤害的数量 -> damage_bonus_<增伤百分数> 
"""


class SkillService:
    """
    战法服务类，用于管理和提供技能的相关操作。
    """
    def __init__(self):
        self.skills = {}
        self._load_skills()

    def _load_skills(self):
        """
        初始化并加载所有可用的技能实例。
        """
        # 手动指定需要加载的技能模块
        skill_modules = [
            "core.active_skill",
            "core.command_skill",
            "core.formation_skill",
            "core.passive_skill",
            "core.troop_skill"
        ]

        for module_path in skill_modules:
            module = importlib.import_module(module_path)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, Skill) and attr is not Skill:
                    self._add_skill_instance(attr)

    def _add_skill_instance(self, skill_class):
        """
        创建技能实例并添加到技能字典中。
        :param skill_class: 技能类
        """
        skill_instance = skill_class()
        if hasattr(skill_instance, 'name'):
            self.skills[skill_instance.name] = skill_instance

    def get_skill(self, skill_name):
        """
        根据技能名称获取技能实例。
        :param skill_name: 技能名称
        :return: 技能实例
        """
        return self.skills.get(skill_name)

    def load_skill(self, skill_name, skill_instance):
        """
        根据技能名称和实例更新或添加技能。
        :param skill_name: 技能名称
        :param skill_instance: 技能实例
        """
        self.skills[skill_name] = skill_instance

    def list_skills(self):
        """
        返回所有已加载的技能名称。
        :return: 技能名称列表
        """
        return list(self.skills.keys())
