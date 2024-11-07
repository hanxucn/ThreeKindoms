

guanyu = {
    "name": "guanyu",
    "country": "shu",
    "basic_power": 97,  # 默认1级初始武力值
    "power_up": 2.68,  # 每升 1 级提升的武力值
    "basic_defense": 97,  # 默认 1 级初始防御值
    "defense_up": 2.04,  # 每升 1 级提升的防御值
    "basic_intelligence": 79,  # 默认 1 级初始智力值
    "intelligence_up": 1.05,  # 每升 1 级提升的智力值
    "basic_speed": 74,  # 默认 1 级初始速度值
    "speed_up": 1.3,  # 每升 1 级提升的速度值
    "self_skill": "weizhenhuaxia",  # 自带战法
    "type": "normal",  # 普通 or sp
    # 部队兵种适应度:pike 枪兵 S，shield 盾兵 A, bow 弓箭 C, cavalry 骑兵 S
    "troop_adaptability": {"pike": "s_level", "shield": "a_level", "bow": "c_level", "cavalry": "s_level"},
    # "level": 50,  # 45 or 50  这个值从前端传入参数
    # "add_property": {"power": 50},  # 默认升级全加力量，这里改用前端传递
    "default_attack_type": "physical",  # 武力 physical  or 谋略 intelligence or 综合 combined
    "has_dynamic": True,  # 是否有动态人物
    "take_troops": 10000,  # 默认初始带满兵1W，如果为 45级 则为 95000
    "gender": "male",  # 性别
}

guanyinping = {
    "name": "guanyinping",
    "country": "shu",
    "basic_power": 78,  # 默认1级初始武力值
    "power_up": 2.09,  # 每升 1 级提升的武力值
    "basic_defense": 73,  # 默认 1 级初始防御值
    "defense_up": 1.97,  # 每升 1 级提升的防御值
    "basic_intelligence": 42,  # 默认 1 级初始智力值
    "intelligence_up": 0.76,  # 每升 1 级提升的智力值
    "basic_speed": 65,  # 默认 1 级初始速度值
    "speed_up": 1.21,  # 每升 1 级提升的速度值
    "self_skill": "jiangmenhunv",  # 自带战法
    "type": "normal",  # 普通 or sp
    # 部队兵种适应度:pike 枪兵 S，shield 盾兵 A, bow 弓箭 C, cavalry 骑兵 S
    "troop_adaptability": {"pike": "s_level", "shield": "b_level", "bow": "c_level", "cavalry": "s_level"},
    "default_attack_type": "physical",  # 武力 physical  or 谋略 intelligence or 综合 combined
    "has_dynamic": True,  # 是否有动态人物
    "take_troops": 10000,  # 默认初始带满兵1W，如果为 45级 则为 95000
    "gender": "female",  # 性别
}

zhangfei = {
    "name": "zhangfei",
    "country": "shu",
    "basic_power": 98,  # 默认1级初始武力值
    "power_up": 2.69,  # 每升 1 级提升的武力值
    "basic_defense": 94,  # 默认 1 级初始防御值
    "defense_up": 1.69,  # 每升 1 级提升的防御值
    "basic_intelligence": 30,  # 默认 1 级初始智力值
    "intelligence_up": 0.22,  # 每升 1 级提升的智力值
    "basic_speed": 70,  # 默认 1 级初始速度值
    "speed_up": 1.26,  # 每升 1 级提升的速度值
    "self_skill": "yanrenpaoxiao",  # 自带战法
    "type": "normal",  # 普通 or sp
    # 部队兵种适应度:pike 枪兵 S，shield 盾兵 A, bow 弓箭 C, cavalry 骑兵 S
    "troop_adaptability": {"pike": "s_level", "shield": "s_level", "bow": "c_level", "cavalry": "a_level"},
    "default_attack_type": "physical",  # 武力 physical  or 谋略 intelligence or 综合 combined
    "has_dynamic": True,  # 是否有动态人物
    "take_troops": 10000,  # 默认初始带满兵1W，如果为 45级 则为 95000
    "gender": "male",  # 性别
}

# wei =============================
simayi = {
    "name": "simayi",
    "country": "wei",
    "basic_power": 63,  # 默认1级初始武力值
    "power_up": 0.42,  # 每升 1 级提升的武力值
    "basic_defense": 98,  # 默认 1 级初始防御值
    "defense_up": 2.06,  # 每升 1 级提升的防御值
    "basic_intelligence": 98,  # 默认 1 级初始智力值
    "intelligence_up": 2.67,  # 每升 1 级提升的智力值
    "basic_speed": 39,  # 默认 1 级初始速度值
    "speed_up": 0.82,  # 每升 1 级提升的速度值
    "self_skill": "yingshilanggu",  # 自带战法
    "type": "normal",  # 普通 or sp
    # 部队兵种适应度:pike 枪兵 S，shield 盾兵 A, bow 弓箭 C, cavalry 骑兵 S
    "troop_adaptability": {"pike": "s_level", "shield": "s_level", "bow": "a_level", "cavalry": "a_level"},
    "default_attack_type": "intelligence",  # 武力 physical  or 谋略 intelligence or 综合 combined
    "has_dynamic": True,  # 是否有动态人物
    "take_troops": 10000,  # 默认初始带满兵1W，如果为 45级 则为 95000
    "gender": "male",  # 性别
}

caocao = {
    "name": "caocao",
    "country": "wei",
    "basic_power": 72,  # 默认1级初始武力值
    "power_up": 1.33,  # 每升 1 级提升的武力值
    "basic_defense": 99,  # 默认 1 级初始防御值
    "defense_up": 2.70,  # 每升 1 级提升的防御值
    "basic_intelligence": 91,  # 默认 1 级初始智力值
    "intelligence_up": 1.94,  # 每升 1 级提升的智力值
    "basic_speed": 64,  # 默认 1 级初始速度值
    "speed_up": 1.18,  # 每升 1 级提升的速度值
    "self_skill": "luanshijianxiong",  # 自带战法
    "type": "normal",  # 普通 or sp
    # 部队兵种适应度:pike 枪兵 S，shield 盾兵 A, bow 弓箭 C, cavalry 骑兵 S
    "troop_adaptability": {"pike": "a_level", "shield": "s_level", "bow": "a_level", "cavalry": "s_level"},
    "default_attack_type": "intelligence",  # 武力 physical  or 谋略 intelligence or 综合 combined
    "has_dynamic": True,  # 是否有动态人物
    "take_troops": 10000,  # 默认初始带满兵1W，如果为 45级 则为 95000
    "gender": "male",  # 性别
}

manchong = {
    "name": "manchong",
    "country": "wei",
    "basic_power": 64,  # 默认1级初始武力值
    "power_up": 0.92,  # 每升 1 级提升的武力值
    "basic_defense": 85,  # 默认 1 级初始防御值
    "defense_up": 1.95,  # 每升 1 级提升的防御值
    "basic_intelligence": 82,  # 默认 1 级初始智力值
    "intelligence_up": 2.08,  # 每升 1 级提升的智力值
    "basic_speed": 61,  # 默认 1 级初始速度值
    "speed_up": 1.08,  # 每升 1 级提升的速度值
    "self_skill": "zhenefangju",  # 自带战法
    "type": "normal",  # 普通 or sp
    # 部队兵种适应度:pike 枪兵 S，shield 盾兵 A, bow 弓箭 C, cavalry 骑兵 S
    "troop_adaptability": {"pike": "b_level", "shield": "s_level", "bow": "a_level", "cavalry": "a_level"},
    "default_attack_type": "intelligence",  # 武力 physical  or 谋略 intelligence or 综合 combined
    "has_dynamic": True,  # 是否有动态人物
    "take_troops": 10000,  # 默认初始带满兵1W，如果为 45级 则为 95000
    "gender": "male",  # 性别
}

zhangcunhua = {
    "name": "zhangcunhua",
    "country": "wei",
    "basic_power": 49,  # 默认1级初始武力值
    "power_up": 0.40,  # 每升 1 级提升的武力值
    "basic_defense": 60,  # 默认 1 级初始防御值
    "defense_up": 1.34,  # 每升 1 级提升的防御值
    "basic_intelligence": 79,  # 默认 1 级初始智力值
    "intelligence_up": 1.98,  # 每升 1 级提升的智力值
    "basic_speed": 48,  # 默认 1 级初始速度值
    "speed_up": 0.63,  # 每升 1 级提升的速度值
    "self_skill": "chenduanjimou",  # 自带战法
    "type": "normal",  # 普通 or sp
    # 部队兵种适应度:pike 枪兵 S，shield 盾兵 A, bow 弓箭 C, cavalry 骑兵 S
    "troop_adaptability": {"pike": "c_level", "shield": "a_level", "bow": "a_level", "cavalry": "a_level"},
    "default_attack_type": "intelligence",  # 武力 physical  or 谋略 intelligence or 综合 combined
    "has_dynamic": True,  # 是否有动态人物
    "take_troops": 10000,  # 默认初始带满兵1W，如果为 45级 则为 95000
    "gender": "female",  # 性别
}
