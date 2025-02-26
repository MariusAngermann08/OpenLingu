import kivy
from kivymd.app import MDApp # type: ignore
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import json
import requests

#Import Database Module
from database import Database

#Importing custom modules
Builder.load_file('kivy/main_ui.kv')
Builder.load_file('kivy/auth_pages.kv')

class SignInScreen(Screen):
    pass

class SignUpScreen(Screen):
    pass
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
        self.sm.add_widget(SignInScreen(name="signin"))
        self.sm.add_widget(SignUpScreen(name="signup"))
        self.sm.current = "signin"
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
    def sign_in_menu(self, **kwargs):
        self.sm.transition.direction = "right"
        self.sm.current = "signin"
    def sign_up_menu(self, **kwargs):
        self.sm.transition.direction = "left"
        self.sm.current = "signup"


if __name__ == "__main__":
    
    OpenLinguApp().run()