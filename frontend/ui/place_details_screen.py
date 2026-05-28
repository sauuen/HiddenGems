import webbrowser

from kivy.uix.screenmanager import Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle

from services.storage_service import StorageService
from logic.recommendation_engine import RecommendationEngine


class PlaceDetailsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.place = None
        self.storage = StorageService()
        self.engine = RecommendationEngine()

        root = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            padding=18,
        )

        self.card = BoxLayout(
            orientation="vertical",
            padding=[20, 20, 20, 20],
            spacing=12,
            size_hint=(1, 1),
        )

        with self.card.canvas.before:
            Color(0.10, 0.10, 0.13, 1)
            self.card_bg = RoundedRectangle(radius=[18])

        self.card.bind(pos=self._update_card_bg, size=self._update_card_bg)

        self.top_bar = Label(
            text="DETAILS",
            font_size=12,
            bold=True,
            color=(0.75, 0.75, 0.82, 1),
            size_hint=(1, None),
            height=22,
        )

        self.name_label = Label(
            text="",
            font_size=28,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=44,
        )

        self.badge_label = Label(
            text="",
            font_size=13,
            size_hint=(1, None),
            height=24,
        )

        self.meta_label = Label(
            text="",
            font_size=15,
            color=(0.88, 0.88, 0.92, 1),
            size_hint=(1, None),
            height=30,
        )

        self.details_label = Label(
            text="",
            font_size=15,
            color=(0.74, 0.82, 0.96, 1),
            size_hint=(1, None),
            height=30,
        )

        self.reason_label = Label(
            text="",
            font_size=14,
            color=(0.85, 0.85, 0.9, 1),
            halign="left",
            valign="top",
        )
        self.reason_label.bind(size=lambda instance, value: setattr(instance, "text_size", value))

        self.status_label = Label(
            text="",
            font_size=12,
            color=(0.64, 0.9, 0.72, 1),
            size_hint=(1, None),
            height=20,
        )

        self.save_button = Button(
            text="Save to Favorites",
            size_hint=(1, None),
            height=46,
            background_normal="",
            background_down="",
            background_color=(0.20, 0.56, 0.86, 1),
            color=(1, 1, 1, 1),
        )
        self.save_button.bind(on_press=self.save_favorite)

        self.map_view_button = Button(
            text="Open Map View",
            size_hint=(1, None),
            height=46,
            background_normal="",
            background_down="",
            background_color=(0.28, 0.31, 0.42, 1),
            color=(1, 1, 1, 1),
        )
        self.map_view_button.bind(on_press=self.open_map_view)

        self.maps_button = Button(
            text="Open in Maps",
            size_hint=(1, None),
            height=46,
            background_normal="",
            background_down="",
            background_color=(0.25, 0.35, 0.55, 1),
            color=(1, 1, 1, 1),
        )
        self.maps_button.bind(on_press=self.open_maps)

        self.back_button = Button(
            text="Back",
            size_hint=(1, None),
            height=52,
            background_normal="",
            background_down="",
            background_color=(0.22, 0.22, 0.26, 1),
            color=(1, 1, 1, 1),
        )
        self.back_button.bind(on_press=self.go_back)

        self.card.add_widget(self.top_bar)
        self.card.add_widget(self.name_label)
        self.card.add_widget(self.badge_label)
        self.card.add_widget(self.meta_label)
        self.card.add_widget(self.details_label)
        self.card.add_widget(self.reason_label)
        self.card.add_widget(Label(size_hint=(1, 1)))
        self.card.add_widget(self.status_label)
        self.card.add_widget(self.save_button)
        self.card.add_widget(self.map_view_button)
        self.card.add_widget(self.maps_button)
        self.card.add_widget(self.back_button)

        root.add_widget(self.card)
        self.add_widget(root)

    def _update_card_bg(self, *args):
        self.card_bg.pos = self.card.pos
        self.card_bg.size = self.card.size

    def set_place(self, place):
        self.place = place

        self.name_label.text = place.name
        self.meta_label.text = (
            f"⭐ {place.rating}   Reviews: {place.reviews}   Distance: {place.distance_km} km"
        )
        self.details_label.text = (
            f"{place.category}   {place.price_level}   Score: {place.score}"
        )
        self.reason_label.text = f"Why: {place.reason}"
        self.status_label.text = ""

        if place.is_chain:
            self.badge_label.text = "Badge: Chain"
            self.badge_label.color = (0.86, 0.62, 0.32, 1)
        else:
            self.badge_label.text = "Badge: Independent"
            self.badge_label.color = (0.45, 0.84, 0.62, 1)

        if place.maps_url:
            self.maps_button.disabled = False
            self.maps_button.opacity = 1
        else:
            self.maps_button.disabled = True
            self.maps_button.opacity = 0.6

    def save_favorite(self, instance):
        if not self.place:
            return

        saved = self.storage.save_favorite(self.place)
        if saved:
            self.status_label.text = "Saved"
        else:
            self.status_label.text = "Already in favorites"

    def open_map_view(self, instance):
        if self.place and self.manager and self.manager.has_screen("map"):
            current_location = self.engine.gps_service.get_location()

            map_screen = self.manager.get_screen("map")
            map_screen.set_places(
                [self.place],
                current_location["lat"],
                current_location["lng"],
            )
            self.manager.current = "map"

    def open_maps(self, instance):
        if self.place and self.place.maps_url:
            webbrowser.open(self.place.maps_url)

    def go_back(self, instance):
        if self.manager.has_screen("results"):
            self.manager.current = "results"