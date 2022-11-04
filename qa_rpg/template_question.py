from enum import Enum

BLANK = "___"


class TemplateCatalog(Enum):

    TEMPLATES = [["Which of ", "the following ", "is ", "correct"],
                 ["Which of ", "the following ", "is ", "incorrect"],
                 ["How many ", BLANK, " in ", BLANK], ["When ", "did ", BLANK, " happen"],
                 ["Which ", BLANK, " has ", BLANK], ["What is the ", BLANK, " for ", BLANK]]

    def get_template(self, index: int):
        return self.value[index]

    def get_price(self, index: int):
        return 100 + (self.value[index].count("") * 50)

    def get_all_available_templates(self, index_list: list):
        available = []
        for index in index_list:
            available.append(self.value[index])
        return available
