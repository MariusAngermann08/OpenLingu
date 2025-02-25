import kivy
from kivymd.app import MDApp
from kivy.lang import Builder
#Importing custom modules

class OpenLinguApp(MDApp):
    #Hallo Jonas
    def build(self, **kwargs):
        return Builder.load_file('kivy\main_ui.kv')

if __name__ == "__main__":
    
    OpenLinguApp().run()