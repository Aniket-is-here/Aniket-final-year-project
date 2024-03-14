class GameStateManager:
    def __init__(self, currentState):
        self.state = currentState

    def getstate(self):
        return self.state

    def changestate(self, newstate):
        self.state = newstate

