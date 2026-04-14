from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider


class FiltersScreen(Screen):
    filters_data = {
        "min_rating": 4.0,
        "min_reviews": 10,
        "radius_km": 5,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        title = Label(text="Filters", font_size=24, size_hint=(1, 0.15))

        self.rating_label = Label(text="Minimum Rating: 4.0", size_hint=(1, 0.1))
        rating_slider = Slider(min=1, max=5, value=4.0)
        rating_slider.bind(value=self.on_rating_change)

        self.reviews_label = Label(text="Minimum Reviews: 10", size_hint=(1, 0.1))
        reviews_slider = Slider(min=0, max=200, value=10)
        reviews_slider.bind(value=self.on_reviews_change)

        self.radius_label = Label(text="Radius: 5 km", size_hint=(1, 0.1))
        radius_slider = Slider(min=1, max=20, value=5)
        radius_slider.bind(value=self.on_radius_change)

        back_btn = Button(text="Back", size_hint=(1, 0.15))
        back_btn.bind(on_press=self.go_back)

        layout.add_widget(title)
        layout.add_widget(self.rating_label)
        layout.add_widget(rating_slider)
        layout.add_widget(self.reviews_label)
        layout.add_widget(reviews_slider)
        layout.add_widget(self.radius_label)
        layout.add_widget(radius_slider)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def on_rating_change(self, instance, value):
        value = round(value, 1)
        self.filters_data["min_rating"] = value
        self.rating_label.text = f"Minimum Rating: {value}"

    def on_reviews_change(self, instance, value):
        value = int(value)
        self.filters_data["min_reviews"] = value
        self.reviews_label.text = f"Minimum Reviews: {value}"

    def on_radius_change(self, instance, value):
        value = int(value)
        self.filters_data["radius_km"] = value
        self.radius_label.text = f"Radius: {value} km"

    def go_back(self, instance):
        self.manager.current = "home"