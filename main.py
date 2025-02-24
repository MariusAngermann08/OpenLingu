import kivy
from kivymd.app import MDApp
from kivy.lang import Builder

#Importing custom modules
from module import HelloWorld

Builder.load_file("kivy/main_ui.kv")

class OpenLinguApp(MDApp):
    #Hallo Jonas
    def build(self, **kwargs):
        return None

if __name__ == "__main__":
    HelloWorld()
    OpenLinguApp().run()