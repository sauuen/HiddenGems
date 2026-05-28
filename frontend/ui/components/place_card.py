from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle

from services.storage_service import StorageService


class PlaceCard(BoxLayout):
    def __init__(self, place, manager=None, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=285,
            padding=[14, 14, 14, 14],
            spacing=8,
            **kwargs
        )

        self.place = place
        self.manager = manager
        self.storage = StorageService()

        with self.canvas.before:
            Color(0.14, 0.14, 0.18, 1)
            self.bg = RoundedRectangle(radius=[16])

        self.bind(pos=self._update_bg, size=self._update_bg)

        title = Label(
            text=f"[b]{place.name}[/b]",
            markup=True,
            size_hint_y=None,
            height=28,
            halign="left",
            valign="middle",
            font_size=18,
            color=(1, 1, 1, 1),
        )
        title.bind(size=lambda instance, value: setattr(instance, "text_size", value))

        badge_text = "Chain" if place.is_chain else "Independent"
        badge_color = (0.86, 0.62, 0.32, 1) if place.is_chain else (0.45, 0.84, 0.62, 1)

        badge = Label(
            text=f"Badge: {badge_text}",
            size_hint_y=None,
            height=22,
            halign="left",
            valign="middle",
            font_size=12,
            color=badge_color,
        )
        badge.bind(size=lambda instance, value: setattr(instance, "text_size", value))

        meta = Label(
            text=f"⭐ {place.rating}   Reviews: {place.reviews}   Distance: {place.distance_km} km",
            size_hint_y=None,
            height=24,
            halign="left",
            valign="middle",
            font_size=14,
            color=(0.88, 0.88, 0.92, 1),
        )
        meta.bind(size=lambda instance, value: setattr(instance, "text_size", value))

        details = Label(
            text=f"{place.category}   {place.price_level}   Score: {place.score}",
            size_hint_y=None,
            height=24,
            halign="left",
            valign="middle",
            font_size=14,
            color=(0.74, 0.82, 0.96, 1),
        )
        details.bind(size=lambda instance, value: setattr(instance, "text_size", value))

        reason = Label(
            text=f"Why: {place.reason}",
            halign="left",
            valign="top",
            font_size=13,
            color=(0.85, 0.85, 0.9, 1),
        )
        reason.bind(size=lambda instance, value: setattr(instance, "text_size", value))

        self.status_label = Label(
            text="",
            size_hint_y=None,
            height=18,
            font_size=12,
            color=(0.64, 0.9, 0.72, 1),
        )

        details_button = Button(
            text="View Details",
            size_hint=(1, None),
            height=42,
            background_normal="",
            background_down="",
            background_color=(0.28, 0.31, 0.42, 1),
            color=(1, 1, 1, 1),
        )
        details_button.bind(on_press=self.open_details)

        save_button = Button(
            text="Save to Favorites",
            size_hint=(1, None),
            height=42,
            background_normal="",
            background_down="",
            background_color=(0.20, 0.56, 0.86, 1),
            color=(1, 1, 1, 1),
        )
        save_button.bind(on_press=self.save_favorite)

        self.add_widget(title)
        self.add_widget(badge)
        self.add_widget(meta)
        self.add_widget(details)
        self.add_widget(reason)
        self.add_widget(self.status_label)
        self.add_widget(details_button)
        self.add_widget(save_button)

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def save_favorite(self, instance):
        saved = self.storage.save_favorite(self.place)
        if saved:
            self.status_label.text = "Saved"
        else:
            self.status_label.text = "Already in favorites"

    def open_details(self, instance):
        if self.manager and self.manager.has_screen("details"):
            details_screen = self.manager.get_screen("details")
            details_screen.set_place(self.place)
            self.manager.current = "details"