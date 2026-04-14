from models.place import Place


class PlacesService:
    def get_nearby_places(self, lat, lng):
        """
        Simple mock data so the app works right now.
        Later replace with Google Places or another API.
        """
        return [
            Place("Mama Lina", 4.7, 48, 0.8, "Italian"),
            Place("Sushi Corner", 4.6, 22, 1.2, "Sushi"),
            Place("Burger Nest", 4.3, 180, 2.1, "Burgers"),
            Place("Hidden Bowl", 4.8, 35, 1.6, "Ramen"),
            Place("Cafe Bloom", 4.5, 65, 0.5, "Cafe"),
            Place("Golden Spice", 4.4, 90, 3.4, "Indian"),
        ]