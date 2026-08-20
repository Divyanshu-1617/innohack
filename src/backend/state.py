from datetime import datetime


system_state = {
    "system_status": "ONLINE",
    "cameras": {},
    "zones": {},
    "alerts": [],
    "last_update": None,
}


def update_detection(data):
    camera_id = data["camera_id"]
    zone = data["zone"]

    system_state["cameras"][camera_id] = {
        "zone": zone,
        "people_count": data["people_count"],
        "crowd_level": data["crowd_level"],
        "blocked": data["blocked"],
        "threat": data["threat"],
    }

    system_state["zones"][zone] = {
        "people_count": data["people_count"],
        "crowd_level": data["crowd_level"],
        "blocked": data["blocked"],
        "threat": data["threat"],
    }

    system_state["last_update"] = datetime.now().isoformat()

    return system_state