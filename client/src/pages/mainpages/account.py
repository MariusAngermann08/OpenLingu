import flet as ft
import requests


class AccountPage(ft.Container):
    def __init__(self, page, account_name=None, account_email=None, account_pic=None):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page

        self.account_name = account_name or "Unbekannt"
        self.account_email = account_email or "Keine E-Mail angegeben"
        self.account_pic = account_pic or "https://via.placeholder.com/150"

        self.available_pics = [
            "https://i.pravatar.cc/150?img=1",
            "https://i.pravatar.cc/150?img=2",
            "https://i.pravatar.cc/150?img=3",
            "https://i.pravatar.cc/150?img=4",
            "https://i.pravatar.cc/150?img=5",
            "https://i.pravatar.cc/150?img=6"
        ]

        self.avatar = ft.CircleAvatar(
            foreground_image_src=self.account_pic,
            radius=50
        )

        # Dialog mit Avatar-Auswahl
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Profilbild auswählen"),
            content=self.build_avatar_picker(),
            actions=[
                ft.TextButton("Abbrechen", on_click=self.close_dialog)
            ],
        )
        self.page.dialog = self.dialog  # wichtig: dialog hier schon zuweisen

        self.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Stack([
                                self.avatar,
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_size=18,
                                    tooltip="Profilbild ändern",
                                    on_click=lambda e: page.open(self.dialog),  # ohne Klammern! sonst wird direkt aufgerufen
                                    style=ft.ButtonStyle(
                                        padding=0,
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                        bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.WHITE)
                                    ),
                                    top=0,
                                    right=0,
                                )
                            ], width=100, height=100),

                            ft.Text(self.account_name, size=22, weight="bold", text_align="center"),
                            ft.Text(self.account_email, size=14, color=ft.Colors.GREY_600, text_align="center"),
                            ft.Divider(height=60, thickness=1, color=ft.Colors.GREY_300),
                            ft.Text("Weitere Informationen folgen hier ...", size=16, color=ft.Colors.GREY_500, italic=True),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=24
                    ),
                    width=800,
                    padding=20,
                    margin=ft.margin.all(20),
                    border_radius=ft.border_radius.all(20),
                    bgcolor=ft.Colors.GREY_100,
                    alignment=ft.alignment.center
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )

    def open_dialog(self, e):
        self.dialog.content = self.build_avatar_picker()  # refresh content, falls sich die Liste ändert
        self.dialog.open = True
        self.page.update()  # unbedingt update aufrufen, damit UI neu gerendert wird

    def close_dialog(self, e=None):
        self.dialog.open = False
        self.page.update()

    def select_pic(self, url):
        self.account_pic = url
        self.avatar.foreground_image_src = url
        self.close_dialog()

    def build_avatar_picker(self):
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.GestureDetector(
                            content=ft.Image(
                                src=img,
                                width=60,
                                height=60,
                                border_radius=30,
                                fit=ft.ImageFit.COVER
                            ),
                            on_tap=lambda e, src=img: self.select_pic(src)
                        )
                        for img in self.available_pics[:3]
                    ],
                    spacing=10
                ),
                ft.Row(
                    controls=[
                        ft.GestureDetector(
                            content=ft.Image(
                                src=img,
                                width=60,
                                height=60,
                                border_radius=30,
                                fit=ft.ImageFit.COVER
                            ),
                            on_tap=lambda e, src=img: self.select_pic(src)
                        )
                        for img in self.available_pics[3:]
                    ],
                    spacing=10
                )
            ],
            spacing=10,
            tight=True
        )