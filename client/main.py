import kivy
import kivymd
from kivymd.app import MDApp

class App(MDApp):
    def build(self):
        #Set window title
        self.title = "Open Lingu"

        return None

App().run()