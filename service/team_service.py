
from general_service import GeneralService


class Team:
    def __init__(self, generals):
        self.generals = generals

    def is_alive(self):
        return any(general.is_alive() for general in self.generals)

    def get_main_general(self):
        return self.generals[0]  # 主将是第一个将领

    def get_generals(self):
        return [general for general in self.generals if general.is_alive()]

