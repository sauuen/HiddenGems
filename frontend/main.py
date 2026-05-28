from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window

from ui.home_screen import HomeScreen
from ui.filters_screen import FiltersScreen
from ui.results_screen import ResultsScreen
from ui.favorites_screen import FavoritesScreen
from ui.place_details_screen import PlaceDetailsScreen
from ui.map_screen import MapScreen


Window.size = (390, 780)
Window.minimum_width = 360
Window.minimum_height = 640
Window.clearcolor = (0.06, 0.06, 0.08, 1)


class HiddenGemsApp(App):
    def build(self):
        self.title = "Hidden Gems"

        screen_manager = ScreenManager(transition=SlideTransition())
        screen_manager.add_widget(HomeScreen(name="home"))
        screen_manager.add_widget(FiltersScreen(name="filters"))
        screen_manager.add_widget(ResultsScreen(name="results"))
        screen_manager.add_widget(FavoritesScreen(name="favorites"))
        screen_manager.add_widget(PlaceDetailsScreen(name="details"))
        screen_manager.add_widget(MapScreen(name="map"))
        return screen_manager


if __name__ == "__main__":
    HiddenGemsApp().run()