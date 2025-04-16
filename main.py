import kivy
from kivymd.app import MDApp # type: ignore
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
import json
import requests
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.core.window import Window

#AtomTest

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
    username = ObjectProperty(None)
    email = ObjectProperty(None)
    password1 = ObjectProperty(None)
    password2 = ObjectProperty(None)
    test_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SignUpScreen,self).__init__(**kwargs)

    def get_data(self):
        data = [self.username.text,self.email.text,self.password1.register_password.text,self.password2.confirm_password.text]
        self.test_label.text = f"Click Sign Up to display data from input fields\n{str(data)}"
        return data

class MainScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class LanguageScreen(Screen):
    pass
class Passwordloginfield(MDRelativeLayout):
    pass
class Passwordregisterfield(MDRelativeLayout):
    pass

class Passwordconfirmfield(MDRelativeLayout):
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
        Window.size = (412,600)
        self.main_screen = MainScreen(name="main")
        self.settings_screen = SettingsScreen(name="settings")
        self.language_screen = LanguageScreen(name="language")
        self.signin_screen = SignInScreen(name="signin")
        self.signup_screen = SignUpScreen(name="signup")
        self.welcome_screen = WelcomeScreen(name="welcome")

        self.sm = ScreenManager()
        self.sm.add_widget(self.main_screen)
        self.sm.add_widget(self.settings_screen)
        self.sm.add_widget(self.language_screen)
        self.sm.add_widget(self.signin_screen)
        self.sm.add_widget(self.signup_screen)
        self.sm.add_widget(self.welcome_screen)
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
        self.sm.current = "welcome"


    def sign_up(self, **kwargs):
        data = self.signup_screen.get_data()
        print(data)


if __name__ == "__main__":

    OpenLinguApp().run()
