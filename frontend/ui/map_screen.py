import os
import webbrowser

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy_garden.mapview import MapView, MapMarker


def asset_path(filename):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "assets", filename)


class PlaceMarker(MapMarker):
    def __init__(self, place=None, manager=None, map_screen=None, **kwargs):
        super().__init__(**kwargs)
        self.place = place
        self.manager = manager
        self.map_screen = map_screen

    def on_release(self):
        if self.map_screen and self.place:
            self.map_screen.selected_place = self.place
            self.map_screen.route_button.disabled = False
            self.map_screen.route_button.opacity = 1
            self.map_screen.subheader.text = f"Selected: {self.place.name}"

        if self.manager and self.manager.has_screen("details") and self.place:
            details_screen = self.manager.get_screen("details")
            details_screen.set_place(self.place)
            self.manager.current = "details"


class UserMarker(MapMarker):
    pass


class MapScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.places = []
        self.current_lat = 59.9139
        self.current_lon = 10.7522
        self.selected_place = None

        self.user_icon = asset_path("user_marker.png")
        self.place_icon = asset_path("place_marker.png")

        root = BoxLayout(orientation="vertical", padding=10, spacing=8)

        self.header = Label(
            text="Map View",
            size_hint=(1, None),
            height=36,
            font_size=22,
            bold=True,
            color=(1, 1, 1, 1),
        )

        self.subheader = Label(
            text="Blue marker = you • Red marker = place",
            size_hint=(1, None),
            height=24,
            font_size=13,
            color=(0.85, 0.85, 0.9, 1),
        )

        self.map_view = MapView(
            zoom=16,
            lat=self.current_lat,
            lon=self.current_lon,
        )

        controls = BoxLayout(size_hint=(1, None), height=48, spacing=8)

        self.route_button = Button(
            text="Open Route",
            background_normal="",
            background_down="",
            background_color=(0.20, 0.56, 0.86, 1),
            color=(1, 1, 1, 1),
            disabled=True,
            opacity=0.6,
        )
        self.route_button.bind(on_press=self.open_route)

        back_button = Button(
            text="Back",
            background_normal="",
            background_down="",
            background_color=(0.22, 0.22, 0.26, 1),
            color=(1, 1, 1, 1),
        )
        back_button.bind(on_press=self.go_back)

        controls.add_widget(self.route_button)
        controls.add_widget(back_button)

        root.add_widget(self.header)
        root.add_widget(self.subheader)
        root.add_widget(self.map_view)
        root.add_widget(controls)

        self.add_widget(root)

    def set_places(self, places, current_lat, current_lon):
        self.places = places or []
        self.current_lat = current_lat
        self.current_lon = current_lon
        self.selected_place = None
        self.route_button.disabled = True
        self.route_button.opacity = 0.6
        self.refresh_map()

    def refresh_map(self):
        parent = self.map_view.parent
        if parent:
            parent.remove_widget(self.map_view)

        self.map_view = MapView(
            zoom=16,
            lat=self.current_lat,
            lon=self.current_lon,
        )

        if parent:
            parent.add_widget(self.map_view, index=0)

        user_icon_exists = os.path.exists(self.user_icon)
        place_icon_exists = os.path.exists(self.place_icon)

        self.subheader.text = f"Blue marker = you • Red markers = places ({len(self.places)})"

        # exact current location marker
        user_kwargs = {
            "lat": self.current_lat,
            "lon": self.current_lon,
        }
        if user_icon_exists:
            user_kwargs["source"] = self.user_icon

        self.map_view.add_marker(UserMarker(**user_kwargs))

        for place in self.places:
            if not place.lat or not place.lon:
                continue

            marker_lat = float(place.lat)
            marker_lon = float(place.lon)

            # only offset if almost identical to your location (about a few meters)
            if abs(marker_lat - self.current_lat) < 0.0001 and abs(marker_lon - self.current_lon) < 0.0001:
                marker_lat += 0.00025
                marker_lon += 0.00025

            marker_kwargs = {
                "place": place,
                "manager": self.manager,
                "map_screen": self,
                "lat": marker_lat,
                "lon": marker_lon,
            }
            if place_icon_exists:
                marker_kwargs["source"] = self.place_icon

            self.map_view.add_marker(PlaceMarker(**marker_kwargs))

    def open_route(self, instance):
        if not self.selected_place:
            return

        origin = f"{self.current_lat},{self.current_lon}"
        destination = f"{self.selected_place.lat},{self.selected_place.lon}"

        url = (
            "https://www.google.com/maps/dir/?api=1"
            f"&origin={origin}"
            f"&destination={destination}"
            "&travelmode=driving"
        )
        webbrowser.open(url)

    def go_back(self, instance):
        if self.manager.has_screen("results"):
            self.manager.current = "results"