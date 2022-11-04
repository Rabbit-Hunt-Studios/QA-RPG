from enum import Enum

BLANK = "___"


class TemplateCatalog(Enum):

    TEMPLATES = [["Which of ", "the following ", "is ", "correct"],
                 ["Which of ", "the following ", "is ", "incorrect"],
                 ["How many ", BLANK, " in ", BLANK], ["When ", "did ", BLANK, " happen"],
                 ["Which ", BLANK, " has ", BLANK], ["What is the ", BLANK, " for ", BLANK],
                 ["Who ", BLANK, " in ", BLANK], ["Which feature ", "does ", BLANK, "have"],
                 ["*", "How", BLANK], ["*", "Who", BLANK], ["*", "What", BLANK], ["*", "Where", BLANK],
                 ["*", "When", BLANK], ["*", "Why", BLANK]]

    def get_template(self, index: int):
        if self.value[index][0] == "*":
            return self.value[index][0:]
        return self.value[index]

    def get_price(self, index: int):
        if self.value[index].count("*") > 0:
            return 999
        return 100 + (self.value[index].count(BLANK) * 50)

    def get_all_available_templates(self, index_list: list):
        available = []
        for index in index_list:
            available.append(self.value[index])
        return available
