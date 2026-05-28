from kivy.uix.screenmanager import Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle

from logic.recommendation_engine import RecommendationEngine
from ui.components.place_card import PlaceCard


class ResultsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.engine = RecommendationEngine()
        self.user_query = ""
        self.current_results = []

        root = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            padding=18,
        )

        self.card = BoxLayout(
            orientation="vertical",
            padding=[18, 20, 18, 20],
            spacing=10,
            size_hint=(1, 1),
        )

        with self.card.canvas.before:
            Color(0.10, 0.10, 0.13, 1)
            self.card_bg = RoundedRectangle(radius=[18])

        self.card.bind(pos=self._update_card_bg, size=self._update_card_bg)

        top_bar = Label(
            text="RESULTS",
            font_size=12,
            bold=True,
            color=(0.75, 0.75, 0.82, 1),
            size_hint=(1, None),
            height=22,
        )

        self.header_label = Label(
            text="Hidden Gem Matches",
            font_size=28,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=40,
        )

        self.summary_label = Label(
            text="",
            font_size=13,
            color=(0.75, 0.83, 0.95, 1),
            size_hint=(1, None),
            height=22,
        )

        self.subheader_label = Label(
            text="",
            font_size=13,
            color=(0.85, 0.85, 0.9, 1),
            size_hint=(1, None),
            height=36,
        )

        top_actions = BoxLayout(size_hint=(1, None), height=44, spacing=8)

        self.map_button = Button(
            text="Map View",
            background_normal="",
            background_down="",
            background_color=(0.28, 0.31, 0.42, 1),
            color=(1, 1, 1, 1),
        )
        self.map_button.bind(on_press=self.open_map_view)

        self.back_button = Button(
            text="Back",
            background_normal="",
            background_down="",
            background_color=(0.20, 0.56, 0.86, 1),
            color=(1, 1, 1, 1),
        )
        self.back_button.bind(on_press=self.go_back)

        top_actions.add_widget(self.map_button)
        top_actions.add_widget(self.back_button)

        self.results_container = BoxLayout(
            orientation="vertical",
            spacing=12,
            padding=[0, 4, 0, 8],
            size_hint_y=None,
        )
        self.results_container.bind(minimum_height=self.results_container.setter("height"))

        scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            bar_width=6,
        )
        scroll.add_widget(self.results_container)

        self.card.add_widget(top_bar)
        self.card.add_widget(self.header_label)
        self.card.add_widget(self.summary_label)
        self.card.add_widget(self.subheader_label)
        self.card.add_widget(top_actions)
        self.card.add_widget(scroll)

        root.add_widget(self.card)
        self.add_widget(root)

    def _update_card_bg(self, *args):
        self.card_bg.pos = self.card.pos
        self.card_bg.size = self.card.size

    def get_sort_mode_label(self, mode):
        labels = {
            "hidden_gem": "Hidden Gem",
            "closest": "Closest",
            "highest_rated": "Highest Rated",
        }
        return labels.get(mode, "Hidden Gem")

    def load_results(self):
        self.results_container.clear_widgets()

        filters_screen = self.manager.get_screen("filters")
        ui_prefs = dict(filters_screen.filters_data)

        results, final_prefs = self.engine.get_recommendations(
            ui_prefs=ui_prefs,
            user_query=self.user_query,
        )

        self.current_results = results

        preferred_categories = final_prefs.get("preferred_categories", [])
        preferred_prices = final_prefs.get("preferred_price_levels", [])
        sort_mode = final_prefs.get("sort_mode", "hidden_gem")
        location_name = self.engine.get_current_location_name()

        preferred_text = ", ".join(preferred_categories) if preferred_categories else "Any"
        price_text = ", ".join(preferred_prices) if preferred_prices else "Any"
        sort_text = self.get_sort_mode_label(sort_mode)

        self.summary_label.text = f"{len(results)} matches • Sorted by {sort_text}"
        self.subheader_label.text = (
            f"{location_name} • Type: {preferred_text} • Price: {price_text} • Radius: {final_prefs['radius_km']} km"
        )

        if not results:
            self.map_button.disabled = True
            self.map_button.opacity = 0.6

            self.results_container.add_widget(
                Label(
                    text="No places matched your search. Try relaxing your filters.",
                    size_hint_y=None,
                    height=60,
                    font_size=15,
                    color=(1, 1, 1, 1),
                )
            )
            return

        self.map_button.disabled = False
        self.map_button.opacity = 1

        for place in results:
            self.results_container.add_widget(PlaceCard(place, manager=self.manager))

    def open_map_view(self, instance):
        if not self.current_results:
            return

        location = self.engine.gps_service.get_location()

        if self.manager.has_screen("map"):
            map_screen = self.manager.get_screen("map")
            map_screen.set_places(
                self.current_results,
                location["lat"],
                location["lng"],
            )
            self.manager.current = "map"

    def go_back(self, instance):
        self.manager.current = "home"