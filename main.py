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

class OpenLinguApp(MDApp):
    #Hallo Jonas
    def build(self, **kwargs):
        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(name="main"))
        self.sm.add_widget(SettingsScreen(name="settings"))
        return self.sm
    
    def open_settings_menu(self, **kwargs):
        self.sm.transition.direction = "left"
        self.sm.current = "settings"
    def backto_main_menu(self, **kwargs):
        self.sm.transition.direction = "right"
        self.sm.current = "main"

if __name__ == "__main__":
    
    OpenLinguApp().run()