from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from ui.home_screen import HomeScreen
from ui.filters_screen import FiltersScreen
from ui.results_screen import ResultsScreen


class HiddenGemsApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(FiltersScreen(name="filters"))
        sm.add_widget(ResultsScreen(name="results"))
        return sm


if __name__ == "__main__":
    HiddenGemsApp().run()