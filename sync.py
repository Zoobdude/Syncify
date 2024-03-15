import requests

def set_song(songID: str, user_token: str) -> bool:
    r = requests.put(
        url="https://api.spotify.com/v1/me/player/play",
        headers={
            'Authorization': 'Bearer ' + user_token,
            'Content-Type': 'application/json'
        },
        data={
            'uris': [f"spotify:track:{songID}"]
        }
    )
    
    if r.status_code != 204:
        print(r.text)
        return False
    
    return True

def set_progress(progress_ms: int, user_token: str) -> bool:
    r = requests.put(
        url="https://api.spotify.com/v1/me/player/seek",
        headers={
            'Authorization': 'Bearer ' + user_token,
            'Content-Type': 'application/json'
        },
        params={
            'position_ms': progress_ms
        }
    )
    
    if r.status_code == 204:
        return True
    
    return False

def get_state(user_token: str) -> dict:
    r = requests.get(
        url="https://api.spotify.com/v1/me/player",
        headers={
            'Authorization': 'Bearer ' + user_token,
            'Content-Type': 'application/json'
        }
    )
    
    if r.status_code == 204:
        return {}
    
    response_json = r.json()
    
    return{"item": response_json["item"]["id"],
           "progress_ms": response_json["progress_ms"],
           "is_playing": response_json["is_playing"]}

    
