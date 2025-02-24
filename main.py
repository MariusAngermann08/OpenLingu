import kivy
from kivymd.app import MDApp

#Importing custom modules
from module import HelloWorld

class OpenLinguApp(MDApp):
    #Hallo Jonas
    def build(self, **kwargs):
        return None

if __name__ == "__main__":
    HelloWorld()
    OpenLinguApp().run()