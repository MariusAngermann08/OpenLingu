import kivy
from kivymd.app import MDApp # type: ignore
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty, DictProperty, NumericProperty, ObjectProperty
import json
import requests
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivy.factory import Factory
from kivy.metrics import dp
from kivymd.uix.expansionpanel import MDExpansionPanel


#AtomTest

#Import Database Module
from database import Database

#Importing custom modules
Builder.load_file('kivy/main_ui.kv')
Builder.load_file('kivy/auth_pages.kv')
Builder.load_file('kivy/new_user.kv')
Builder.load_file('kivy/custom_widgets.kv')

#Read firebase data from file

APIKEY = ""
URL = ""

with open("server/firebase_data.json", "r") as data:
    temp = json.load(data)
    APIKEY = temp["APIKEY"]
    URL = temp["URL"]


class ChooseFieldItem(BoxLayout):
    def __init__(self,**kwargs):
        super(ChooseFieldItem,self).__init__(**kwargs)

class ChooseField(MDExpansionPanel):
    def __init__(self,**kwargs):
        super(ChooseField,self).__init__(**kwargs)
    
    def addItems(self,items=[]):
        pass
        #[["Deutsch","icon.png"]]

    def getSelected(self,**kwargs):
        return None
    


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
    app_link = None

    def __init__(self, **kwargs):
        super(SignUpScreen,self).__init__(**kwargs)

    def get_data(self):
        data = [self.username.text,self.email.text,self.password1.register_password.text,self.password2.confirm_password.text]
        return data
    
    def passwordsDontMatch(self):
        self.test_label.text = "The passwords dont match!"

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

#NickName *optional Profile Picture
class NewUserPage1(Screen):
    pass

#Age
class NewUserPage2(Screen):
    pass

#First Language to learn
class NewUserPage3(Screen):
    pass




class OpenLinguApp(MDApp):
    #Hallo Jonas
    transition_type = "settings"
    db = None
    user_token = None
    user_data = []

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
        self.signup_screen.app_link = self
        self.welcome_screen = WelcomeScreen(name="welcome")

        #New User Pages
        self.newuserpage1 = NewUserPage1(name="newuser1")
        self.newuserpage2 = NewUserPage2(name="newuser2")
        self.newuserpage3 = NewUserPage3(name="newuser3") 

        self.sm = ScreenManager()
        self.sm.add_widget(self.newuserpage1)
        self.sm.add_widget(self.newuserpage2)
        self.sm.add_widget(self.newuserpage3)


        self.sm.add_widget(self.main_screen)
        self.sm.add_widget(self.settings_screen)
        self.sm.add_widget(self.language_screen)
        self.sm.add_widget(self.signin_screen)
        self.sm.add_widget(self.signup_screen)
        self.sm.add_widget(self.welcome_screen)
        self.sm.current = "newuser2"
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
        if data[2] == data[3]:
            self.db.sign_up(data[1],data[2])
            self.user_data = [data[1],data[2]] 
            self.sm.transition.direction = "right"
            self.sm.current = "newuser1"          
        else:
            self.signup_screen.passwordsDontMatch()
    
    def sign_in(self, **kwargs):
        pass



if __name__ == "__main__":

    OpenLinguApp().run()
