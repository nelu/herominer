"""AI-based decision making for automation"""

def choose_best_team(available_heroes):
    """Uses AI to select the optimal team for battle"""
    return sorted(available_heroes, key=lambda hero: hero['power'], reverse=True)[:5]
