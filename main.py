import base64
import time

import room
import sync

import requests
from tinydb import TinyDB, where
import uuid6

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import RedirectResponse

import os
from dotenv import load_dotenv

usr_db = TinyDB('usr_db.json')

app = FastAPI()
room_manager = room.RoomManager()

def query_string(d: dict):
    return "&".join([f"{k}={v}" for k, v in d.items()])

# Load environment variables from .env file
load_dotenv()

# Get the client_id from the environment file
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

redirect_uri = 'http://localhost:8000/callback'

scope = 'user-read-private user-read-email'

def get_user_account(user_id: str, secret: str) -> dict:
    user = usr_db.get((where('SpotifyID') == user_id) & (where('Secret') == secret))
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
    

@app.get("/login")
def login():
    return RedirectResponse(
        "https://accounts.spotify.com/authorize?"+
        query_string(
                    {
                        'response_type': 'code',
                        'client_id': client_id,
                        'scope': scope,
                        'redirect_uri': redirect_uri,
                    }
                            ))

@app.get("/callback")
def login_callback(code: str = None, state: str = None, error: str = None):
    if error:
        print(error)

    # Get the access token
    token_response = requests.post(
        url="https://accounts.spotify.com/api/token",
        headers={
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode() 
        },
        data={
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
    
    )
    
    token_response_json = token_response.json()
    print(token_response_json)
    
    #Fetch the user's information
    user_data = requests.get(
        url="https://api.spotify.com/v1/me",
        headers={
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + token_response_json['access_token']
        }
    )
    
    user_data_json = user_data.json()
    
    #Check if the user is already in the database and remove the old entry
    if usr_db.get(where('SpotifyID') == user_data_json['id']):
        usr_db.remove(where('SpotifyID') == user_data_json['id'])
    
    user_secret = f"US{uuid6.uuid6()}"
    
    usr_db.insert({'Username': user_data_json['display_name'],
                   'Secret': user_secret,
                   'Email': user_data_json['email'],
                   'SpotifyID': user_data_json['id'],
                   'Access Token': token_response_json['access_token'],
                   'Expires in': token_response_json['expires_in'],
                   'Time'
                   'Refresh_token': token_response_json['refresh_token']})
    
    return{"SpotifyID": user_data_json['id'],
           'Secret': user_secret}


def room_background_task(room_id: str):
    current_song = None
    while room_manager.rooms[room_id].status == "Active":
        owner_state = sync.get_state(room_manager.rooms[room_id].owner['Access Token'])
        if owner_state["item"] != current_song:
            current_song = owner_state["item"]
            
            for user in room_manager.rooms[room_id].users:
                if user['SpotifyID'] != room_manager.rooms[room_id].owner['SpotifyID']:
                    sync.set_song(current_song['item'], user['Access Token'])
                    sync.set_progress(current_song['progress_ms'], user['Access Token'])
        
        time.sleep(1)
    
    print(f"Room {room_id} is no longer active")
    room_manager.delete_room(room_id)

@app.get("/create_room")
def create_room(usr_ID: str, secret: str, background_tasks: BackgroundTasks):
    user = get_user_account(usr_ID, secret)

    room_id = room_manager.create_room(user['SpotifyID'])
    room_manager.join_room(room_id, user['SpotifyID'])
    
    #create background task
    background_tasks.add_task(room_background_task, room_id)
    return {"RoomID": room_id}

@app.get("/join_room")
def join_room(usr_ID: str, secret: str, room_id: str):
    user = usr_db.get((where('SpotifyID') == usr_ID) & (where('Secret') == secret))
    
    if room_id not in room_manager.rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room_manager.join_room(room_id, user['SpotifyID'])
    return {"RoomID": room_id}
     
@app.get("/leave_room")
def leave_room(usr_ID: str, secret: str, room_id: str):
    user = usr_db.get((where('SpotifyID') == usr_ID) & (where('Secret') == secret))
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if room_id not in room_manager.rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room_manager.leave_room(room_id, user['SpotifyID'])
    return {"RoomID": room_id}

@app.delete("/close_room")
def close_room(usr_ID: str, Secret: str, room_id: str):
    user = get_user_account(usr_ID, Secret)
    
    if room_id not in room_manager.rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if user['SpotifyID'] != room_manager.get_room_owner(room_id):
        raise HTTPException(status_code=403, detail="User is not the owner of the room")
    
    room_manager.close_room(room_id)
    return {"RoomID": room_id}
    
#https://developer.spotify.com/documentation/web-api/tutorials/code-flow