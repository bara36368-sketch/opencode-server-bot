import math
import json
import os
import time

DATA_FILE = os.path.join(os.path.dirname(__file__), "location_data.json")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

class LocationDistance:
    def __init__(self):
        self.data = self._load()

    def _load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"home": {}, "users": {}, "settings": {}}

    def _save(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    def set_home(self, chat_id, lat, lon, name="Home"):
        chat = str(chat_id)
        self.data.setdefault("home", {})[chat] = {"lat": lat, "lon": lon, "name": name, "set_at": time.time()}
        self._save()

    def get_home(self, chat_id):
        return self.data.get("home", {}).get(str(chat_id))

    def record_user_location(self, chat_id, user_id, lat, lon):
        chat, uid = str(chat_id), str(user_id)
        self.data.setdefault("users", {}).setdefault(chat, {})[uid] = {
            "lat": lat, "lon": lon, "updated": time.time()
        }
        self._save()

    def get_distance(self, chat_id, user_id):
        home = self.get_home(chat_id)
        if not home:
            return None
        user_loc = self.data.get("users", {}).get(str(chat_id), {}).get(str(user_id))
        if not user_loc:
            return None
        return haversine(home["lat"], home["lon"], user_loc["lat"], user_loc["lon"])

    def set_max_distance(self, chat_id, km):
        self.data.setdefault("settings", {})[str(chat_id)] = {"max_distance_km": km}
        self._save()

    def get_max_distance(self, chat_id):
        return self.data.get("settings", {}).get(str(chat_id), {}).get("max_distance_km")

    def is_within_range(self, chat_id, user_id):
        maxd = self.get_max_distance(chat_id)
        if not maxd:
            return True
        dist = self.get_distance(chat_id, user_id)
        if dist is None:
            return True
        return dist <= maxd

    def get_user_history(self, chat_id, user_id):
        return self.data.get("users", {}).get(str(chat_id), {}).get(str(user_id))

    def get_all_users_in_range(self, chat_id):
        home = self.get_home(chat_id)
        if not home:
            return []
        maxd = self.get_max_distance(chat_id) or 999999
        results = []
        for uid, loc in self.data.get("users", {}).get(str(chat_id), {}).items():
            dist = haversine(home["lat"], home["lon"], loc["lat"], loc["lon"])
            if dist <= maxd:
                results.append({"user_id": uid, "distance_km": round(dist, 2)})
        results.sort(key=lambda x: x["distance_km"])
        return results

    def format_config(self, chat_id):
        home = self.get_home(chat_id)
        maxd = self.get_max_distance(chat_id)
        users = self.data.get("users", {}).get(str(chat_id), {})
        lines = ["Location & Distance Config:"]
        if home:
            lines.append(f"  Home: {home['name']} ({home['lat']:.4f}, {home['lon']:.4f})")
        else:
            lines.append("  Home: not set (use /loc set <lat> <lon> [name])")
        lines.append(f"  Max distance: {maxd} km" if maxd else "  Max distance: unlimited")
        lines.append(f"  Tracked users: {len(users)}")
        return "\n".join(lines)

_location = None

def get_location():
    global _location
    if _location is None:
        _location = LocationDistance()
    return _location
