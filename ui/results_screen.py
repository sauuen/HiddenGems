from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

from services.gps_service import GPSService
from services.places_service import PlacesService
from services.scoring_service import passes_filters, calculate_score


class ResultsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_query = ""

        self.gps_service = GPSService()
        self.places_service = PlacesService()

        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        self.title = Label(text="Results", font_size=24, size_hint=(1, 0.12))
        self.layout.add_widget(self.title)

        self.results_container = BoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None
        )
        self.results_container.bind(minimum_height=self.results_container.setter("height"))

        scroll = ScrollView(size_hint=(1, 0.75))
        scroll.add_widget(self.results_container)

        self.layout.add_widget(scroll)

        back_btn = Button(text="Back", size_hint=(1, 0.13))
        back_btn.bind(on_press=self.go_back)
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    def load_results(self):
        self.results_container.clear_widgets()

        location = self.gps_service.get_current_location()
        places = self.places_service.get_nearby_places(location["lat"], location["lng"])

        filters_screen = self.manager.get_screen("filters")
        filters_data = filters_screen.filters_data

        filtered_places = []
        for place in places:
            if passes_filters(place, filters_data):
                place.score = calculate_score(place)
                filtered_places.append(place)

        filtered_places.sort(key=lambda x: x.score, reverse=True)

        if not filtered_places:
            self.results_container.add_widget(
                Label(
                    text="No places matched your filters.",
                    size_hint_y=None,
                    height=40
                )
            )
            return

        for place in filtered_places:
            reason = self.get_simple_reason(place)

            text = (
                f"{place.name}\n"
                f"Category: {place.category}\n"
                f"Rating: {place.rating} | Reviews: {place.reviews}\n"
                f"Distance: {place.distance_km} km | Score: {place.score}\n"
                f"Why: {reason}"
            )

            card = Label(
                text=text,
                size_hint_y=None,
                height=140
            )
            self.results_container.add_widget(card)

    def get_simple_reason(self, place):
        if place.rating >= 4.7 and place.reviews < 60:
            return "Very highly rated and still not overly popular."
        if place.distance_km <= 1.0:
            return "Very close to you and worth checking out."
        if place.reviews < 50:
            return "Good ratings with a lower review count, so it feels like a hidden gem."
        return "Matches your current hidden gem filters."

    def go_back(self, instance):
        self.manager.current = "home"