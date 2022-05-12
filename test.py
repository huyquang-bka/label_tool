class State:
    def __init__(self):
        self.b = False

    def setB(self, setTo):
        self.b = setTo


state = State()

SystemHotkey().register(('control', 'e'), callback=lambda: state.setB(True))
