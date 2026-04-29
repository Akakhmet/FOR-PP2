"""persistence.py — JSON load/save for settings and leaderboard."""



import json
import os

# file names for storing data
SETTINGS_FILE    = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

# default settings used if no file exists
DEFAULT_SETTINGS = {
    "sound":      True,
    "car_color":  "default",
    "difficulty": "normal",
}


def load_settings():
    # check if settings file exists
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            # load saved settings and merge with defaults
            
            return {**DEFAULT_SETTINGS, **json.load(f)}
    
    # if no file return default settings
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    # save settings to file in readable format
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


def load_leaderboard():
    # load leaderboard if file exists
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE) as f:
            return json.load(f)
    
    # if no file return empty list
    return []


def save_score(name, score, distance):
    # load current leaderboard
    lb = load_leaderboard()

    # add new result
    lb.append({
        "name": name,
        "score": score,
        "distance": int(distance)
    })

    # sort by score
    lb.sort(key=lambda x: x["score"], reverse=True)

    # keep only top 10 players
    lb = lb[:10]

    # save updated leaderboard
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(lb, f, indent=2)

    return lb