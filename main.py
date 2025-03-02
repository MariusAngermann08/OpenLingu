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

#Read firebase data from file

APIKEY = ""
URL = ""

with open("server/firebase_data.json", "r") as data:
    temp = json.load(data)
    APIKEY = temp["APIKEY"]
    URL = temp["URL"]


class WelcomeScreen(Screen):
    pass
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
    db = None

    def __init__(self, **kwargs):
        super(OpenLinguApp,self).__init__(**kwargs)
        global APIKEY
        global URL
        self.db = Database(apikey=APIKEY,database_url=URL)

    def build(self, **kwargs):
        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(name="main"))
        self.sm.add_widget(SettingsScreen(name="settings"))
        self.sm.add_widget(LanguageScreen(name="language"))
        self.sm.add_widget(SignInScreen(name="signin"))
        self.sm.add_widget(SignUpScreen(name="signup"))
        self.sm.add_widget(WelcomeScreen(name="welcome"))
        self.sm.current = "welcome"
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
        self.sm.transition.direction = "right"
        self.sm.current = "signup"
    def welcome_menu(self, **kwargs):
        self.sm.transition.direction = "left"
class OpenLinguApp(MDApp):
    # Hallo Jonas
    transition_type = "settings"
    db = None

    def __init__(self, **kwargs):
        super(OpenLinguApp, self).__init__(**kwargs)
        global APIKEY
        global URL
        self.db = Database(apikey=APIKEY, database_url=URL)

    def build(self, **kwargs):
        self.sm = ScreenManager()
        self.sm.add_widget(WelcomeScreen(name="welcome"))
        self.sm.add_widget(SignInScreen(name="signin"))
        self.sm.add_widget(SignUpScreen(name="signup"))
        self.sm.add_widget(MainScreen(name="main"))
        self.sm.add_widget(SettingsScreen(name="settings"))
        self.sm.add_widget(LanguageScreen(name="language"))
        self.sm.current = "welcome"
        return self.sm

    def navigate_to(self, screen_name, transition_direction):
        self.sm.transition.direction = transition_direction
        self.sm.current = screen_name

    def open_settings_menu(self, **kwargs):
        self.navigate_to("settings", "left")

    def main_menu(self, **kwargs):
        if self.transition_type == "settings":
            self.navigate_to("main", "right")
        elif self.transition_type == "language":
            self.navigate_to("main", "up")

    def language_menu(self, **kwargs):
        self.transition_type = "language"
        self.navigate_to("language", "down")

    def sign_in_menu(self, **kwargs):
        self.navigate_to("signin", "right")

    def sign_up_menu(self, **kwargs):
        self.navigate_to("signup", "right")

    def welcome_menu(self, **kwargs):
        self.navigate_to("welcome", "left")        
        self.sm.current = "welcome"


if __name__ == "__main__":
    
    OpenLinguApp().run()