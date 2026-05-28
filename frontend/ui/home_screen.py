from kivy.uix.screenmanager import Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle

from logic.recommendation_engine import RecommendationEngine


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.engine = RecommendationEngine()

        root = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            padding=18,
        )

        self.card = BoxLayout(
            orientation="vertical",
            spacing=12,
            padding=[20, 22, 20, 22],
            size_hint=(1, 1),
        )

        with self.card.canvas.before:
            Color(0.10, 0.10, 0.13, 1)
            self.card_bg = RoundedRectangle(radius=[18])

        self.card.bind(pos=self._update_card_bg, size=self._update_card_bg)

        top_bar = Label(
            text="DISCOVER",
            font_size=12,
            bold=True,
            color=(0.75, 0.75, 0.82, 1),
            size_hint=(1, None),
            height=22,
        )

        title = Label(
            text="Hidden Gems",
            font_size=34,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=52,
        )

        subtitle = Label(
            text="Find nearby hidden gem restaurants",
            font_size=16,
            color=(0.85, 0.85, 0.9, 1),
            size_hint=(1, None),
            height=28,
        )

        backend_status = self.engine.backend_status()
        backend_online = backend_status.get("backend") == "online"
        llm_status = "Backend: connected" if backend_online else "Backend: offline"

        status_label = Label(
            text=llm_status,
            font_size=12,
            color=(0.65, 0.82, 0.72, 1) if backend_online else (0.86, 0.72, 0.45, 1),
            size_hint=(1, None),
            height=20,
        )

        self.location_label = Label(
            text=f"Location: {self.engine.get_current_location_name()}",
            font_size=13,
            color=(0.75, 0.83, 0.95, 1),
            size_hint=(1, None),
            height=22,
        )

        self.taste_label = Label(
            text="Taste: " + self.engine.get_taste_profile()["summary"],
            font_size=12,
            color=(0.72, 0.82, 0.72, 1),
            size_hint=(1, None),
            height=22,
        )

        self.location_input = TextInput(
            hint_text="Enter city or lat,lng",
            multiline=False,
            size_hint=(1, None),
            height=46,
            padding=[12, 12, 12, 12],
            background_normal="",
            background_active="",
            background_color=(0.94, 0.94, 0.96, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            cursor_color=(0.1, 0.1, 0.1, 1),
        )

        self.location_status = Label(
            text="Try: Hamar, Oslo, New York, or 59.9139,10.7522",
            font_size=11,
            color=(0.72, 0.72, 0.78, 1),
            size_hint=(1, None),
            height=18,
        )

        location_buttons = BoxLayout(
            size_hint=(1, None),
            height=44,
            spacing=8,
        )

        self.set_location_button = Button(
            text="Set Location",
            background_normal="",
            background_down="",
            background_color=(0.28, 0.31, 0.42, 1),
            color=(1, 1, 1, 1),
        )
        self.set_location_button.bind(on_press=self.set_manual_location)

        self.cycle_location_button = Button(
            text="Cycle Test Cities",
            background_normal="",
            background_down="",
            background_color=(0.32, 0.35, 0.48, 1),
            color=(1, 1, 1, 1),
        )
        self.cycle_location_button.bind(on_press=self.change_location)

        location_buttons.add_widget(self.set_location_button)
        location_buttons.add_widget(self.cycle_location_button)

        self.query_input = TextInput(
            hint_text="Try: cheap sushi nearby with good reviews",
            multiline=False,
            size_hint=(1, None),
            height=52,
            padding=[14, 14, 14, 14],
            background_normal="",
            background_active="",
            background_color=(0.94, 0.94, 0.96, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            cursor_color=(0.1, 0.1, 0.1, 1),
        )

        tip_label = Label(
            text="Search by vibe, food type, price, or sort intent.",
            font_size=13,
            color=(0.72, 0.72, 0.78, 1),
            size_hint=(1, None),
            height=22,
        )

        filters_button = Button(
            text="Open Filters",
            size_hint=(1, None),
            height=52,
            background_normal="",
            background_down="",
            background_color=(0.32, 0.35, 0.48, 1),
            color=(1, 1, 1, 1),
        )
        filters_button.bind(on_press=self.go_to_filters)

        find_button = Button(
            text="Find Hidden Gems",
            size_hint=(1, None),
            height=56,
            background_normal="",
            background_down="",
            background_color=(0.20, 0.56, 0.86, 1),
            color=(1, 1, 1, 1),
        )
        find_button.bind(on_press=self.go_to_results)

        favorites_button = Button(
            text="View Favorites",
            size_hint=(1, None),
            height=52,
            background_normal="",
            background_down="",
            background_color=(0.22, 0.22, 0.26, 1),
            color=(1, 1, 1, 1),
        )
        favorites_button.bind(on_press=self.go_to_favorites)

        self.card.add_widget(top_bar)
        self.card.add_widget(Label(size_hint=(1, None), height=6))
        self.card.add_widget(title)
        self.card.add_widget(subtitle)
        self.card.add_widget(status_label)
        self.card.add_widget(self.location_label)
        self.card.add_widget(self.taste_label)
        self.card.add_widget(self.location_input)
        self.card.add_widget(self.location_status)
        self.card.add_widget(location_buttons)
        self.card.add_widget(Label(size_hint=(1, None), height=6))
        self.card.add_widget(self.query_input)
        self.card.add_widget(tip_label)
        self.card.add_widget(Label(size_hint=(1, None), height=12))
        self.card.add_widget(find_button)
        self.card.add_widget(filters_button)
        self.card.add_widget(favorites_button)
        self.card.add_widget(Label(size_hint=(1, 1)))

        root.add_widget(self.card)
        self.add_widget(root)

    def on_pre_enter(self, *args):
        self.location_label.text = f"Location: {self.engine.get_current_location_name()}"
        self.taste_label.text = "Taste: " + self.engine.get_taste_profile()["summary"]

    def _update_card_bg(self, *args):
        self.card_bg.pos = self.card.pos
        self.card_bg.size = self.card.size

    def set_manual_location(self, instance):
        success, message = self.engine.set_location_from_input(self.location_input.text)

        if success:
            self.location_label.text = f"Location: {self.engine.get_current_location_name()}"
            self.location_status.text = message
            self.location_status.color = (0.64, 0.9, 0.72, 1)
        else:
            self.location_status.text = message
            self.location_status.color = (0.9, 0.55, 0.55, 1)

    def change_location(self, instance):
        names = self.engine.get_available_location_names()
        current = self.engine.get_current_location_name()

        if current in names:
            index = names.index(current)
            next_index = (index + 1) % len(names)
            self.engine.set_named_location(names[next_index])
        else:
            self.engine.set_named_location(names[0])

        self.location_label.text = f"Location: {self.engine.get_current_location_name()}"
        self.location_status.text = f"Location set to {self.engine.get_current_location_name()}"
        self.location_status.color = (0.64, 0.9, 0.72, 1)

    def go_to_filters(self, instance):
        self.manager.current = "filters"

    def go_to_results(self, instance):
        results_screen = self.manager.get_screen("results")
        results_screen.user_query = self.query_input.text.strip()
        results_screen.load_results()
        self.manager.current = "results"

    def go_to_favorites(self, instance):
        self.manager.current = "favorites"