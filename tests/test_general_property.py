from cgi import test
from config.generals import guanyu, zhangfei, guanyinping, caocao, manchong, simayi, zhangcunhua
from service.general_service import GeneralService

def test_guanyu_property():
    # 创建关羽实例，设置为50级
    guanyu_service = GeneralService(
        general_info=guanyu,
        is_dynamic=True,  # 动态人物
        is_classic=True,  # 典藏
        fusion_count=5,   # 满红
        take_troops_type="pike",  # 使用枪兵
        is_leader=True,   # 作为主将
        user_level=50,    # 50级
        equipped_skill_names=[{"name": "qianlizoudanqi", "type": "passive"}, {"name": "weimoumikang", "type": "active"}],
        user_add_property={"power": 50, "intelligence": 0, "speed": 0, "defense": 0}  # 加点全加武力
    )
    
    # 获取并打印属性
    properties = guanyu_service.get_general_property(guanyu)
    
    print("\n关羽属性测试结果:")
    print("-" * 30)
    for prop, value in properties.items():
        print(f"{prop}: {value}")
    print("-" * 30)


def test_zhangfei_property():
    # 创建张飞实例，设置为50级
    zhangfei_service = GeneralService(
        general_info=zhangfei,
        is_dynamic=True,  # 动态人物
        is_classic=True,  # 典藏
        fusion_count=5,   # 满红
        take_troops_type="pike",  # 使用枪兵
        is_leader=False,   # 作为主将
        user_level=50,    # 50级
        equipped_skill_names=[{"name": "hengsaoqianjun", "type": "active"}, {"name": "jixingzhen", "type": "formation"}],
        user_add_property={"power": 50, "intelligence": 0, "speed": 0, "defense": 0}  # 加点全加武力
    )
    
    # 获取并打印属性
    properties = zhangfei_service.get_general_property(zhangfei)
    
    print("\n张飞属性测试结果:")
    print("-" * 30)
    for prop, value in properties.items():
        print(f"{prop}: {value}")
    print("-" * 30)


def test_guanyinping_property():
    # 创建关银屏实例，设置为50级
    guanyinping_service = GeneralService(
        general_info=guanyinping,
        is_dynamic=True,  # 动态人物
        is_classic=True,  # 典藏
        fusion_count=5,   # 满红
        take_troops_type="pike",  # 使用枪兵
        is_leader=False,   # 作为主将
        user_level=50,    # 50级
        equipped_skill_names=[{"name": "jifengzhouyu", "type": "active"}, {"name": "shengqilindi", "type": "command"}],
        user_add_property={"power": 30, "intelligence": 0, "speed": 20, "defense": 0}  # 部分武力部分速度加点
    )
    
    # 获取并打印属性
    properties = guanyinping_service.get_general_property(guanyinping)
    
    print("\n关银屏属性测试结果:")
    print("-" * 30)
    for prop, value in properties.items():
        print(f"{prop}: {value}")
    print("-" * 30)


def test_caocao_property():
    # 创建曹操实例，设置为50级
    caocao_service = GeneralService(
        general_info=caocao,
        is_dynamic=True,  # 动态人物
        is_classic=True,  # 典藏
        fusion_count=5,   # 满红
        take_troops_type="shield",  # 使用枪兵
        is_leader=False,   # 作为主将
        user_level=50,    # 50级
        equipped_skill_names=[{"name": "meihuo", "type": "passive"}, {"name": "tengjiabing", "type": "troop"}],
        user_add_property={"power": 0, "intelligence": 0, "speed": 0, "defense": 50}  # 加点全加统帅
    )
    
    # 获取并打印属性
    properties = caocao_service.get_general_property(caocao)
    can_alloc_property = caocao_service.overall_can_allocation_property()

    print("\n曹操可分配属性测试结果:")
    print("-" * 30)
    print(f"can_alloc_property: {can_alloc_property}")
    print("-" * 30) 
    
    print("\n曹操属性测试结果:")
    print("-" * 30)
    for prop, value in properties.items():
        print(f"{prop}: {value}")
    print("-" * 30)


def test_manchong_property():
    # 创建满宠实例，设置为50级
    manchong_service = GeneralService(
        general_info=manchong,
        is_dynamic=True,  # 动态人物
        is_classic=True,  # 典藏
        fusion_count=5,   # 满红
        take_troops_type="shield",  # 使用枪兵
        is_leader=False,   # 作为主将
        user_level=50,    # 50级
        equipped_skill_names=[{"name": "guaguliaodu", "type": "active"}, {"name": "fengshizhen", "type": "formation"}],
        user_add_property=None,
    )
    
    # 获取并打印属性
    can_alloc_property = manchong_service.overall_can_allocation_property()

    print("\n满宠可分配属性测试结果:")
    print("-" * 30)
    print(f"can_alloc_property: {can_alloc_property}")
    print("-" * 30)

    properties = manchong_service.get_general_property(manchong, user_add_property={"power": 0, "intelligence": can_alloc_property, "speed": 0, "defense": 0})
    
    print("\n满宠属性测试结果:")
    print("-" * 30)
    for prop, value in properties.items():
        print(f"{prop}: {value}")
    print("-" * 30) 


def test_simayi_property():
    # 创建司马懿实例，设置为50级
    simayi_service = GeneralService(
        general_info=simayi,
        is_dynamic=True,  # 动态人物
        is_classic=True,  # 典藏
        fusion_count=5,   # 满红
        take_troops_type="shield",  # 使用枪兵
        is_leader=True,   # 作为主将
        user_level=50,    # 50级
        equipped_skill_names=[{"name": "yongwutongshen", "type": "command"}, {"name": "shibiesanri", "type": "passive"}],
        user_add_property=None
    )
    
    # 获取并打印属性
    can_alloc_property = simayi_service.overall_can_allocation_property()

    print("\n司马懿可分配属性测试结果:")
    print("-" * 30)
    print(f"can_alloc_property: {can_alloc_property}")
    print("-" * 30)
    properties = simayi_service.get_general_property(simayi, user_add_property={"power": 0, "intelligence": can_alloc_property, "speed": 0, "defense": 0})
    
    print("\n司马懿属性测试结果:")
    print("-" * 30)
    for prop, value in properties.items():
        print(f"{prop}: {value}")
    print("-" * 30)


if __name__ == "__main__":
    #test_guanyu_property()
    #test_zhangfei_property()
    #test_guanyinping_property()
    #test_caocao_property()
    test_manchong_property()
    test_simayi_property()
