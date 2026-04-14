from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        title = Label(text="Hidden Gems", font_size=28, size_hint=(1, 0.2))
        subtitle = Label(
            text="Find nearby hidden gem restaurants",
            size_hint=(1, 0.15)
        )

        self.query_input = TextInput(
            hint_text="What are you craving? e.g. cozy sushi",
            multiline=False,
            size_hint=(1, 0.15)
        )

        filters_btn = Button(
            text="Filters",
            size_hint=(1, 0.15)
        )
        filters_btn.bind(on_press=self.go_to_filters)

        find_btn = Button(
            text="Find Hidden Gems",
            size_hint=(1, 0.2)
        )
        find_btn.bind(on_press=self.go_to_results)

        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(self.query_input)
        layout.add_widget(filters_btn)
        layout.add_widget(find_btn)

        self.add_widget(layout)

    def go_to_filters(self, instance):
        self.manager.current = "filters"

    def go_to_results(self, instance):
        results_screen = self.manager.get_screen("results")
        results_screen.user_query = self.query_input.text.strip()
        results_screen.load_results()
        self.manager.current = "results"