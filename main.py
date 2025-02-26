import kivy
from kivymd.app import MDApp # type: ignore
from kivy.lang import Builder
#Importing custom modules

class OpenLinguApp(MDApp):
    #Hallo Jonas
    def build(self, **kwargs):
        return Builder.load_file('kivy\main_ui.kv')
    def open_settings_menu(self, **kwargs):
        pass

if __name__ == "__main__":
    
    OpenLinguApp().run()