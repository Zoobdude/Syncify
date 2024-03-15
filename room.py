import uuid6

class Room:
    def __init__(self, owner: str) -> None:
        self.owner = owner
        self.members = set()
        self.status = "Active"
        
class RoomManager:
    def __init__(self) -> None:
        self.rooms = {}
    
    def create_room(self, owner: str) -> str:
        room_id = f"RID{uuid6.uuid6()}"
        self.rooms[room_id] = Room(owner)
        return room_id

    def get_room_owner(self, room_id: str) -> str:
        if room_id in self.rooms:
            return self.rooms[room_id].owner
        return "Room not found"
    
    def close_room(self, room_id: str):
        if room_id in self.rooms:
            self.rooms[room_id].status = "Closed"
            return "Room closed"
        return "Room not found"
    
    def delete_room(self, room_id: str):
        if room_id in self.rooms:
            del self.rooms[room_id]
            return "Room deleted"
        return "Room not found"

    def list_rooms(self) -> list:
        return list(self.rooms.keys())

    def list_members_in_room(self, room_id: str) -> list:
        if room_id not in self.rooms:
            return "Room not found"
        
        return list(self.rooms[room_id].members)

    def join_room(self, room_id: str, usr_id: str) -> str:
        if room_id not in self.rooms:
            return "Room not found"
        
        self.rooms[room_id].members.add(usr_id)
        return "Joined room"

    def leave_room(self, room_id: str, usr_id: str):
        if room_id not in self.rooms:
            return "Room not found"
        
        if usr_id not in self.rooms[room_id].members:
            return "User not in room"

        self.rooms[room_id].members.remove(usr_id)
        return "Left room"