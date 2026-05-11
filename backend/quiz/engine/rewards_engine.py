class RewardsEngine:

    def calculate_rewards(self, points):

        rewards = {
            "xp": points,
            "coins": points * 2,
            "badge": None
        }

        if points >= 50:
            rewards["badge"] = "Quiz Master"

        return rewards