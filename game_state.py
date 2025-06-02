# game_state.py

class GameState:
    """
    Gerencia dinheiro e vidas do jogador.
    """
    def __init__(self):
        self.money = 0
        self.lives = 10

    def can_afford(self, amount: int) -> bool:
        return self.money >= amount

    def spend(self, amount: int):
        self.money -= amount

    def earn(self, amount: int):
        self.money += amount

    def lose_life(self):
        self.lives -= 1

game_state = GameState()
