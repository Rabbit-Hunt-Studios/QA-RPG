from enum import Enum

BLANK = "___"


class TemplateCatalog(Enum):

    TEMPLATES = {0: ["Which of ", "the following ", "is ", "correct"],
                 1: ["Which of ", "the following ", "is ", "incorrect"],
                 2: ["How many ", BLANK, " in ", BLANK], 3: ["When ", "did ", BLANK, " happen"],
                 4: ["Which ", BLANK, " has ", BLANK], 5: ["What is the ", BLANK, " for ", BLANK],
                 6: ["Who ", BLANK, " in ", BLANK], 7: ["Which feature ", "does ", BLANK, "have"],
                 100: ["How ", BLANK], 101: ["Who ", BLANK], 102: ["What ", BLANK],
                 103: ["Where ", BLANK], 104: ["When ", BLANK], 105: ["Why ", BLANK],
                 106: ["Which ", BLANK]}

    def get_template(self, index: int):
        return self.value[index]

    def get_price(self, index: int):
        if index >= 100:
            return 999
        return 100 + (self.value[index].count(BLANK) * 50)

    def get_all_available_templates(self, index_list: list):
        available = []
        for index in index_list:
            available.append(self.value[index])
        return available
