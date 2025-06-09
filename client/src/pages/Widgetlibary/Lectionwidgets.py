import flet as ft


# Unterstrichener Text, Underlined Text("Dies ist ein Beispieltext mit einigen unterstrichenen Wörtern",{3 : "red", 5: "blue"}, 32, "green")
class UnderlinedText:
    def __init__(
        self,
        text: str,
        underlined: dict[int, str],
        font_size: float = 14,
        bgcolor: str = None
    ):
        self.text = text
        self.underlined = underlined
        self.font_size = font_size
        self.bgcolor = bgcolor

    def render(self) -> ft.Container:
        words = self.text.split(" ")
        spans = []

        for i, word in enumerate(words):
            if i in self.underlined:
                spans.append(
                    ft.TextSpan(
                        text=word + " ",
                        style=ft.TextStyle(
                            decoration=ft.TextDecoration.UNDERLINE,
                            decoration_color=self.underlined[i],
                            size=self.font_size  # <-- Set font size here!
                        )
                    )
                )
            else:
                spans.append(
                    ft.TextSpan(
                        text=word + " ",
                        style=ft.TextStyle(
                            size=self.font_size  # <-- Set font size here!
                        )
                    )
                )

        return ft.Container(
            bgcolor=self.bgcolor,
            padding=10,
            border_radius=5,
            content=ft.Text(
                spans=spans,
                selectable=True
            )
        )

class Dragables:
    def __init__(self, amount: int, text: dict[int, str], font_size: float):
        self.amount = amount
        self.text = text
        self.font_size = font_size
    