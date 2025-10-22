import chess

class Interface:
    def __init__(self):
        pass

    def input():
        pass

    def output():
        pass

class CompetitionInterface(Interface):
    def __init__(self):
        super().__init__()

    def input(self):
        return input("Test input: ")

    def output(self, gamestate):
        print(gamestate)

class TestInterface(Interface):
    def __init__(self):
        super().__init__()

    def input(self):
        return input("Test input: ")

    def output(self, gamestate):
        print(gamestate)