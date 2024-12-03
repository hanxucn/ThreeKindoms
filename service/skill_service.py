import importlib
from typing import Dict, Type, Optional

from core.base_skill import Skill


class SkillService:
    """
    战法服务类，用于管理和提供技能的相关操作。
    采用按需加载和缓存机制，提高性能和资源利用率。
    """
    # 技能模块映射
    SKILL_MODULES = {
        "active": "core.active_skill",
        "command": "core.command_skill",
        "formation": "core.formation_skill",
        "passive": "core.passive_skill",
        "troop": "core.troop_skill"
    }

    def __init__(self):
        # 用于缓存已加载的技能类
        self._skill_classes: Dict[str, Type[Skill]] = {}
        # 用于缓存已实例化的技能对象
        self._skill_instances: Dict[str, Skill] = {}

    def get_skill(self, skill_name: str, skill_type: Optional[str] = None) -> Optional[Skill]:
        """
        根据技能名称和类型获取技能实例。如果技能未加载，会尝试加载并实例化。
        :param skill_name: 技能名称
        :param skill_type: 技能类型（active/command/formation/passive/troop）
        :return: 技能实例，如果找不到则返回 None
        """
        # 检查是否已有实例
        if skill_name in self._skill_instances:
            return self._skill_instances[skill_name]

        # 尝试加载技能类
        skill_class = self._find_skill_class(skill_name, skill_type)
        if skill_class:
            # 创建实例并缓存
            skill_instance = skill_class()
            self._skill_instances[skill_name] = skill_instance
            return skill_instance

        return None

    def _find_skill_class(self, skill_name: str, skill_type: Optional[str] = None) -> Optional[Type[Skill]]:
        """
        查找指定名称和类型的技能类。
        :param skill_name: 技能名称
        :param skill_type: 技能类型（active/command/formation/passive/troop）
        :return: 技能类，如果找不到则返回 None
        """
        # 检查是否已缓存该技能类
        if skill_name in self._skill_classes:
            return self._skill_classes[skill_name]

        # 如果提供了技能类型，直接查找对应模块
        if skill_type and skill_type in self.SKILL_MODULES:
            module_path = self.SKILL_MODULES[skill_type]
            skill_class = self._find_skill_in_module(module_path, skill_name)
            if skill_class:
                return skill_class

        # 如果没有提供技能类型或在指定模块中未找到，遍历所有模块
        if not skill_type:
            for module_path in self.SKILL_MODULES.values():
                skill_class = self._find_skill_in_module(module_path, skill_name)
                if skill_class:
                    return skill_class

        return None

    def _find_skill_in_module(self, module_path: str, skill_name: str) -> Optional[Type[Skill]]:
        """
        在指定模块中查找技能类。
        :param module_path: 模块路径
        :param skill_name: 技能名称
        :return: 技能类，如果找不到则返回 None
        """
        module = importlib.import_module(module_path)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, Skill) and 
                attr is not Skill and 
                hasattr(attr, 'name') and 
                attr.name == skill_name):
                # 缓存找到的技能类
                self._skill_classes[skill_name] = attr
                return attr
        return None

    def load_skill(self, skill_name: str, skill_instance: Skill) -> None:
        """
        手动加载或更新技能实例。
        :param skill_name: 技能名称
        :param skill_instance: 技能实例
        """
        self._skill_instances[skill_name] = skill_instance

    def clear_cache(self) -> None:
        """
        清除所有缓存的技能类和实例。
        """
        self._skill_classes.clear()
        self._skill_instances.clear()
