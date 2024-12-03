import random


class Skill:
    name = None

    def __init__(self, name=None, skill_type="", attack_type="", quality="", source="", source_general="", target="", effect=None):
        self.name = name or self.name  # Use class-level name if not provided
        self.skill_type = skill_type
        self.attack_type = attack_type
        self.quality = quality
        self.source = source
        self.source_general = source_general
        self.target = target
        self.effect = effect or {}

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
