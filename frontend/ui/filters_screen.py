from kivy.uix.screenmanager import Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.graphics import Color, RoundedRectangle

from config import DEFAULT_PREFS


class FiltersScreen(Screen):
    SORT_OPTIONS = ["hidden_gem", "closest", "highest_rated"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.filters_data = dict(DEFAULT_PREFS)

        root = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            padding=18,
        )

        self.card = BoxLayout(
            orientation="vertical",
            padding=[20, 22, 20, 22],
            spacing=12,
            size_hint=(1, 1),
        )

        with self.card.canvas.before:
            Color(0.10, 0.10, 0.13, 1)
            self.card_bg = RoundedRectangle(radius=[18])

        self.card.bind(pos=self._update_card_bg, size=self._update_card_bg)

        top_bar = Label(
            text="FILTERS",
            font_size=12,
            bold=True,
            color=(0.75, 0.75, 0.82, 1),
            size_hint=(1, None),
            height=22,
        )

        title = Label(
            text="Tune Your Search",
            font_size=30,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=42,
        )

        subtitle = Label(
            text="Control how strict Hidden Gems should be.",
            font_size=14,
            color=(0.85, 0.85, 0.9, 1),
            size_hint=(1, None),
            height=24,
        )

        self.sort_label = Label(
            text=f"Sort Mode: {self.get_sort_mode_label()}",
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=24,
        )

        self.sort_button = Button(
            text="Change Sort Mode",
            size_hint=(1, None),
            height=46,
            background_normal="",
            background_down="",
            background_color=(0.28, 0.31, 0.42, 1),
            color=(1, 1, 1, 1),
        )
        self.sort_button.bind(on_press=self.cycle_sort_mode)

        self.rating_label = Label(
            text=f"Minimum Rating: {self.filters_data['min_rating']}",
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=24,
        )
        self.rating_slider = Slider(min=1, max=5, value=self.filters_data["min_rating"])
        self.rating_slider.bind(value=self.on_rating_change)

        self.min_reviews_label = Label(
            text=f"Minimum Reviews: {self.filters_data['min_reviews']}",
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=24,
        )
        self.min_reviews_slider = Slider(min=0, max=200, value=self.filters_data["min_reviews"])
        self.min_reviews_slider.bind(value=self.on_min_reviews_change)

        self.max_reviews_label = Label(
            text=f"Maximum Reviews: {self.filters_data['max_reviews']}",
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=24,
        )
        self.max_reviews_slider = Slider(min=20, max=500, value=self.filters_data["max_reviews"])
        self.max_reviews_slider.bind(value=self.on_max_reviews_change)

        self.radius_label = Label(
            text=f"Radius: {self.filters_data['radius_km']} km",
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=24,
        )
        self.radius_slider = Slider(min=1, max=20, value=self.filters_data["radius_km"])
        self.radius_slider.bind(value=self.on_radius_change)

        reset_button = Button(
            text="Reset to Defaults",
            size_hint=(1, None),
            height=50,
            background_normal="",
            background_down="",
            background_color=(0.34, 0.34, 0.38, 1),
            color=(1, 1, 1, 1),
        )
        reset_button.bind(on_press=self.reset_filters)

        back_button = Button(
            text="Back",
            size_hint=(1, None),
            height=54,
            background_normal="",
            background_down="",
            background_color=(0.20, 0.56, 0.86, 1),
            color=(1, 1, 1, 1),
        )
        back_button.bind(on_press=self.go_back)

        self.card.add_widget(top_bar)
        self.card.add_widget(title)
        self.card.add_widget(subtitle)
        self.card.add_widget(Label(size_hint=(1, None), height=10))

        self.card.add_widget(self.sort_label)
        self.card.add_widget(self.sort_button)
        self.card.add_widget(Label(size_hint=(1, None), height=6))

        self.card.add_widget(self.rating_label)
        self.card.add_widget(self.rating_slider)

        self.card.add_widget(self.min_reviews_label)
        self.card.add_widget(self.min_reviews_slider)

        self.card.add_widget(self.max_reviews_label)
        self.card.add_widget(self.max_reviews_slider)

        self.card.add_widget(self.radius_label)
        self.card.add_widget(self.radius_slider)

        self.card.add_widget(Label(size_hint=(1, 1)))
        self.card.add_widget(reset_button)
        self.card.add_widget(back_button)

        root.add_widget(self.card)
        self.add_widget(root)

    def _update_card_bg(self, *args):
        self.card_bg.pos = self.card.pos
        self.card_bg.size = self.card.size

    def get_sort_mode_label(self):
        mode = self.filters_data.get("sort_mode", "hidden_gem")
        labels = {
            "hidden_gem": "Hidden Gem",
            "closest": "Closest",
            "highest_rated": "Highest Rated",
        }
        return labels.get(mode, "Hidden Gem")

    def cycle_sort_mode(self, instance):
        current = self.filters_data.get("sort_mode", "hidden_gem")
        index = self.SORT_OPTIONS.index(current)
        next_index = (index + 1) % len(self.SORT_OPTIONS)
        self.filters_data["sort_mode"] = self.SORT_OPTIONS[next_index]
        self.sort_label.text = f"Sort Mode: {self.get_sort_mode_label()}"

    def on_rating_change(self, instance, value):
        value = round(value, 1)
        self.filters_data["min_rating"] = value
        self.rating_label.text = f"Minimum Rating: {value}"

    def on_min_reviews_change(self, instance, value):
        value = int(value)
        self.filters_data["min_reviews"] = value
        self.min_reviews_label.text = f"Minimum Reviews: {value}"

    def on_max_reviews_change(self, instance, value):
        value = int(value)
        self.filters_data["max_reviews"] = value
        self.max_reviews_label.text = f"Maximum Reviews: {value}"

    def on_radius_change(self, instance, value):
        value = int(value)
        self.filters_data["radius_km"] = value
        self.radius_label.text = f"Radius: {value} km"

    def reset_filters(self, instance):
        self.filters_data = dict(DEFAULT_PREFS)
        self.rating_slider.value = self.filters_data["min_rating"]
        self.min_reviews_slider.value = self.filters_data["min_reviews"]
        self.max_reviews_slider.value = self.filters_data["max_reviews"]
        self.radius_slider.value = self.filters_data["radius_km"]

        self.sort_label.text = f"Sort Mode: {self.get_sort_mode_label()}"
        self.rating_label.text = f"Minimum Rating: {self.filters_data['min_rating']}"
        self.min_reviews_label.text = f"Minimum Reviews: {self.filters_data['min_reviews']}"
        self.max_reviews_label.text = f"Maximum Reviews: {self.filters_data['max_reviews']}"
        self.radius_label.text = f"Radius: {self.filters_data['radius_km']} km"

    def go_back(self, instance):
        self.manager.current = "home"