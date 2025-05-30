import flet as ft
import requests

try:
    #Try relative import
    from setuppages.profile import ProfileSetupPage
    from setuppages.nativelanguage import NativeLanguageSetupPage
    from setuppages.studylanguage import StudyLanguageSetupPage
    from setuppages.goal import GoalSetupPage
except ImportError:
    #Do absolute import instead
    from pages.setuppages.profile import ProfileSetupPage
    from pages.setuppages.nativelanguage import NativeLanguageSetupPage
    from pages.setuppages.studylanguage import StudyLanguageSetupPage
    from pages.setuppages.goal import GoalSetupPage
   

class SetupPage(ft.Container):
    def __init__(self, page, route):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        self.route = route
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.current_step = 0
        self.total_steps = 4
        
        # Create step labels
        self.step_labels = ["Profile", "Native Language", "Study Language", "Goal"]
        
        # Create step indicators
        self.steps_row = ft.Row(
            controls=[],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=0,
            width=400,
        )
        
        # Create progress bar
        self.progress_bar = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        expand=True,
                        height=4,
                        bgcolor="#e0e0e0",  # Light gray track
                        border_radius=2,
                        content=ft.Container(
                            bgcolor="#1a73e8",  # Blue progress
                            border_radius=2,
                            width=0  # Will be updated based on progress
                        )
                    )
                ]
            ),
            margin=ft.margin.only(top=10, bottom=20),
            width=400
        )
        
        # Add step indicators
        for i, label in enumerate(self.step_labels):
            self.steps_row.controls.append(
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=24,
                            height=24,
                            border_radius=12,
                            bgcolor="#e0e0e0",
                            content=ft.Text(
                                str(i + 1),
                                color="#757575",
                                weight=ft.FontWeight.BOLD,
                                size=12
                            ),
                            alignment=ft.alignment.center
                        ),
                        ft.Text(
                            label,
                            size=12,
                            color="#757575",
                            weight=ft.FontWeight.W_500
                        )
                    ],
                    spacing=4
                )
            )

        #Define Pages
        self.profile_page = ProfileSetupPage(self)
        self.native_language_page = NativeLanguageSetupPage(self)
        self.study_language_page = StudyLanguageSetupPage(self)
        self.goal_page = GoalSetupPage(self)

        # Update progress bar initially
        self._update_progress()
        
        # Create a fixed header with progress
        self.header = ft.Container(
            content=ft.Column(
                controls=[
                    self.steps_row,
                    self.progress_bar
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                tight=True
            ),
            padding=20,
            alignment=ft.alignment.center,
            bgcolor="white",
            border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color="#e0e0e0",  # Light gray shadow
                offset=ft.Offset(0, 2)
            )
        )
        
        # Main content with header and current page
        self.content = ft.Column(
            controls=[
                self.header,
                self.profile_page
            ],
            expand=True,
            spacing=0
        )
         
    def _update_progress(self):
        # Update progress bar width
        progress = (self.current_step + 1) / self.total_steps
        self.progress_bar.content.controls[0].content.width = f"{progress * 100}%"
        
        # Update step indicators
        for i, step in enumerate(self.steps_row.controls):
            # Update circle color and number
            circle = step.controls[0]
            if i < self.current_step:
                # Completed step
                circle.bgcolor = "#e0e0e0"
                circle.content.value = "✓"
                circle.content.color = "#9e9e9e"
                circle.border = ft.border.all(1, "#bdbdbd")
            elif i == self.current_step:
                # Current step
                circle.bgcolor = "#1a73e8"
                circle.content.value = str(i + 1)
                circle.content.color = "white"
                circle.border = None
            else:
                # Upcoming step
                circle.bgcolor = "white"
                circle.content.value = str(i + 1)
                circle.content.color = "#bdbdbd"
                circle.border = ft.border.all(1, "#e0e0e0")
            
            # Update text color
            text = step.controls[1]
            if i < self.current_step:
                text.color = "#9e9e9e"  # Gray out completed steps
            elif i == self.current_step:
                text.color = "#1a73e8"  # Highlight current step
            else:
                text.color = "#bdbdbd"  # Light gray for upcoming steps
            
            text.weight = ft.FontWeight.BOLD if i <= self.current_step else ft.FontWeight.W_400
        
        self.page.update()
    
    def next_page(self, e):
        if self.current_step < self.total_steps - 1:
            self.current_step += 1
            
            # Update content based on current step
            if self.current_step == 1:
                self.content.controls[1] = self.native_language_page
            elif self.current_step == 2:
                self.content.controls[1] = self.study_language_page
            elif self.current_step == 3:
                self.content.controls[1] = self.goal_page
                
            # Update the header to stay on top
            self.content.controls[0] = self.header
                
            self._update_progress()
        else:
            self.page.finish_setup()

    def finish_setup(self, e):
        # This is called when the drawer is dismissed (e.g., by tapping outside)
        self.page.go("/main")