
from core import troop_skill

skill_wudangfeijun = troop_skill.TroopSkill(
    name="无当飞军",
    skill_type="troop",
    attack_type="intelligence",
    quality="S",
    source="自带战法",
    source_general="王平",
    target="self_team",
    effect={
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
    },
)
