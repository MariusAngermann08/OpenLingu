import kivy
from kivymd.app import MDApp # type: ignore
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

#Importing custom modules
Builder.load_file('kivy\main_ui.kv')
class MainScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class LanguageScreen(Screen):
    pass

class OpenLinguApp(MDApp):
    #Hallo Jonas
    transition_type = "settings"
    def build(self, **kwargs):
        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(name="main"))
        self.sm.add_widget(SettingsScreen(name="settings"))
        self.sm.add_widget(LanguageScreen(name="language"))
        return self.sm
    
    def open_settings_menu(self, **kwargs):
        self.transition_type = "settings"
        self.sm.transition.direction = "left"
        self.sm.current = "settings"
    def main_menu(self, **kwargs):
        if self.transition_type == "settings": self.sm.transition.direction = "right"
        elif self.transition_type == "language": self.sm.transition.direction = "up"
        self.sm.current = "main"
    def language_menu(self, **kwargs):
        self.transition_type = "language"
        self.sm.transition.direction = "down"
        self.sm.current = "language"
if __name__ == "__main__":
    
    OpenLinguApp().run()