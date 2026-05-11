class StreakEngine:

    def calculate_streak_bonus(self, streak_days):

        if streak_days >= 30:
            return 100

        if streak_days >= 7:
            return 30

        if streak_days >= 3:
            return 10

        return 0