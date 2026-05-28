from kivy.uix.screenmanager import Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle

from services.storage_service import StorageService
from ui.components.favorite_card import FavoriteCard


class FavoritesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.storage = StorageService()

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
            text="FAVORITES",
            font_size=12,
            bold=True,
            color=(0.75, 0.75, 0.82, 1),
            size_hint=(1, None),
            height=22,
        )

        self.header_label = Label(
            text="Saved Places",
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
            height=24,
        )

        self.favorites_container = BoxLayout(
            orientation="vertical",
            spacing=12,
            padding=[0, 4, 0, 8],
            size_hint_y=None,
        )
        self.favorites_container.bind(minimum_height=self.favorites_container.setter("height"))

        scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            bar_width=6,
        )
        scroll.add_widget(self.favorites_container)

        refresh_button = Button(
            text="Refresh Favorites",
            size_hint=(1, None),
            height=46,
            background_normal="",
            background_down="",
            background_color=(0.28, 0.31, 0.42, 1),
            color=(1, 1, 1, 1),
        )
        refresh_button.bind(on_press=lambda *_: self.load_favorites())

        back_button = Button(
            text="Back",
            size_hint=(1, None),
            height=52,
            background_normal="",
            background_down="",
            background_color=(0.20, 0.56, 0.86, 1),
            color=(1, 1, 1, 1),
        )
        back_button.bind(on_press=self.go_back)

        self.card.add_widget(top_bar)
        self.card.add_widget(self.header_label)
        self.card.add_widget(self.summary_label)
        self.card.add_widget(scroll)
        self.card.add_widget(refresh_button)
        self.card.add_widget(back_button)

        root.add_widget(self.card)
        self.add_widget(root)

    def _update_card_bg(self, *args):
        self.card_bg.pos = self.card.pos
        self.card_bg.size = self.card.size

    def on_pre_enter(self, *args):
        self.load_favorites()

    def load_favorites(self):
        self.favorites_container.clear_widgets()
        favorites = self.storage.get_favorites()

        self.summary_label.text = f"{len(favorites)} saved places"

        if not favorites:
            self.favorites_container.add_widget(
                Label(
                    text="You have no saved places yet.",
                    size_hint_y=None,
                    height=60,
                    font_size=15,
                    color=(1, 1, 1, 1),
                )
            )
            return

        for place in favorites:
            self.favorites_container.add_widget(
                FavoriteCard(
                    place=place,
                    refresh_callback=self.load_favorites,
                    manager=self.manager,
                )
            )

    def go_back(self, instance):
        self.manager.current = "home"