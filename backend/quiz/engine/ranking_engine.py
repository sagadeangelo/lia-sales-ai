import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
PLAYER_DATA_PATH = BASE_DIR / "storage" / "player_data.json"


class RankingEngine:

    def load_players(self):

        try:
            with open(PLAYER_DATA_PATH, "r", encoding="utf-8") as file:
                return json.load(file)
        except:
            return []

    def get_ranking(self):

        players = self.load_players()

        return sorted(
            players,
            key=lambda x: x.get("total_points", 0),
            reverse=True
        )