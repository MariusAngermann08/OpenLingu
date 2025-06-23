import flet as ft
import json

class LectionParser:
    def __init__(self, lection_json: str):
        self.lection_json = lection_json
        self.lection = json.loads(lection_json)