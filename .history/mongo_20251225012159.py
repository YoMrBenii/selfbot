import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import discord
from discord.ext import commands
import asyncio

uri = os.getenv("mongodb")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["pvp"]

try:
    client.admin.command("ping")
    print("[Mongo] ping OK")
except Exception as e:
    print(f"[Mongo] ping FAILED: {e!r}")

def setuservar(var: str, userid: str, amt: int):
    userid = str(userid)
    amt = int(amt)
    db.users.update_one(
        {"_id": userid},
        {"$inc": {var: amt}},
        upsert=True
    )
def changeuservar(var: str, userid: str, amt):
    userid = str(userid)
    if isinstance(amt, str) and amt.isdigit():
        amt = int(amt)
    db.users.update_one(
        {"_id": userid},
        {"$set": {var: amt}},
        upsert=True
    )

def getuservar(var: str, userid: str):
    users = db["users"]
    userid = str(userid)
    user = users.find_one({"_id": userid})
    if not user:
        return 0
    val = user.get(var, 0)
    return 0 if val is None else val
def resetuservar(var: str, userid: str):
    userid = str(userid)
    db.users.update_one(
        {"_id": userid},
        {"$set": {var: 0}},
        upsert=True
    )
def ccreateclan(clanname: str, userid: str):
    clanfind = db.clans.find_one({"_id": clanname})
    if clanfind is not None:
        return "Clan already exists"
    if userinclan(userid) is not None:
        return "User is already in a clan"
    db.clans.update_one(
        {"_id": clanname},
        {"$push": {"members": {"userid": userid, "rank": "Owner", "points": 0}}},
        upsert=True
    )
    return f"You created the clan {clanname}, to view your clan use -clan"
def userinclan(userid: str) -> str | None:
    clanfind = db.clans.find_one({
        "members.userid": userid},
        {"_id": 1})
    
    if clanfind:
        return clanfind["_id"]
    else:
        return None  
def clanexists(clanname: str):
    clanfind = db.clans.find_one(
        {"_id": clanname}
    )
    if clanfind:
        return True
    else:
        return False   
def setuserclan(clan: str, userid: str) -> str:
    if not clanexists(clan):
        return "Clan does not exist"
    if not userinclan(userid):
        return "You are already in a clan, leave your old one if you want to join a new one"
    db.clans.update_one(
        {"_id": clan},
        {"$push": {"members": {"userid": userid, "rank": "Member", "points": 0}}},
        upsert=True
    )
    return f"<@{userid}> joined {clan}"
def mlb(var: str, amt: int):
    a = "**Weekly rankings\n**"
    top = db.users.find().sort(var, -1).limit(amt)
    for rank, user in enumerate(top, start=1):
        username = user.get("username", "Unknown")
        value = user.get(var, 0)
        format = f"{value:,}"

        a += f"#{rank} - {username} - {format}\n"
    return a
def lb(bot, var: str, amt: int):
    a = ""
    top = db.users.find().sort(var, -1).limit(amt)
    for rank, user in enumerate(top, start=1):
        user_id = int(user["_id"])
        username = user.get("username")

        if not username:
            member = bot.get_user(user_id)
            if not member:
                try:
                    member = asyncio.run_coroutine_threadsafe(
                        bot.fetch_user(user_id),
                        bot.loop
                    ).result(timeout=3)
                except Exception:
                    member = None
            if member:
                username = member.name
                db.users.update_one({"_id": user_id}, {"$set": {"username": username}})
            else:
                username = "Unknown"

        value = user.get(var, 0)
        a += f"#{rank} - {username} - {value:,}\n"

    return a
def getlbspot(var: str, userid: str):
    userid = str(userid)
    cursor = db.users.find({}, {"_id": 1, var: 1})
    scores = [(d["_id"], (d.get(var) or 0)) for d in cursor]
    scores.sort(key=lambda t: t[1], reverse=True)
    for idx, (uid, _) in enumerate(scores, start=1):
        if uid == userid:
            return idx
    return 0
def jobupdate(job: str, userid: str, amt: str):
    userid = str(userid)
    db.jobs.update_one(
        {"_id": job},
        {"$push": {"member": {"userid": userid, "salary": amt}}},
        upsert=True
    )
def ping_db() -> bool:
    client.admin.command("ping")
    return True
def resetallusers(var: str):
    db.users.update_many(
        {},
        {"$set": {var: 0}}
    )
def top1lb(var: str):
    top = db.users.find().sort(var, -1).limit(1)
    for user in top:
        return user.get("_id", "Unknown")
    return "Unknown"
def top1lbvalue(var: str):
    top = db.users.find().sort(var, -1).limit(1)
    for user in top:
        return user.get(var, "Unknown")
    return "Unknown"
def setservervar(var: str, amt: int):
    amt = int(amt)
    db.server.update_one(
        {"_id": "pvp"},
        {"$inc": {var: amt}},
        upsert=True
    )
def changeservervar(var: str, amt):
    db.server.update_one(
        {"_id": "pvp"},
        {"$set": {var: amt}},
        upsert=True
    )
def getservervar(var: str):
    a = db.server.find_one(
        {"_id": "pvp"}
    )
    if a is None:
        return 0
    b = a.get(var, 0)
    return b
def setusername(id: str, username: str):
    id = str(id)
    db.users.update_one(
        {"_id": id},
        {"$set": {"username": username}},
        upsert=True
    )

def changerank(rankname: str, user_id: str):
    userid = str(user_id)
    db.ranks.update_one(
        {"_id": "ranks"},
        {"$addToSet": {rankname: userid}},
        upsert=True
    )

def findusers(var: str, value, operator: str = "=="):
    query = {}
    if isinstance(value, (int, float)):
        if operator == "==":
            query = {var: value}
        elif operator == "!=":
            query = {var: {"$ne": value}}
        elif operator == "<":
            query = {var: {"$lt": value}}
        elif operator == "<=":
            query = {var: {"$lte": value}}
        elif operator == ">":
            query = {var: {"$gt": value}}
        elif operator == ">=":
            query = {var: {"$gte": value}}

    elif isinstance(value, str):
        if operator == "==":
            query = {var: value}
        elif operator == "!=":
            query = {var: {"$ne": value}}
        elif operator == "contains":
            query = {var: {"$regex": value, "$options": "i"}}

    else:
        raise TypeError("Value must be a string or number.")
    cursor = db.users.find(query, {"_id": 1})

    ids = [doc["_id"] for doc in cursor]
    return ids

def auctionlb(bot, var: str):

    a = ""
    top = db.users.find(
        {"staffrank": {"$in": ["executive", "lead executive", "director", "coo", "c-suite"]},
         var: {"$gte": 1}}
        ).sort(var, -1)
    for rank, user in enumerate(top, start=1):
        user_id = int(user["_id"])
        username = user.get("username")

        if not username:
            member = bot.get_user(user_id)
            if not member:
                try:
                    member = asyncio.run_coroutine_threadsafe(
                        bot.fetch_user(user_id),
                        bot.loop
                    ).result(timeout=3)
                except Exception:
                    member = None
            if member:
                username = member.name
                db.users.update_one({"_id": user_id}, {"$set": {"username": username}})
            else:
                username = "Unknown"

        value = user.get(var, 0)
        a += f"#{rank} - {username} - {value:,}\n"
    return a

def add_to_serverlist(list_name, new_values):
    if not isinstance(new_values, list):
        return
    db.server_lists.update_one(
        {"server_id": 1, "list_name": list_name},
        {"$push": {"values": {"$each": new_values}}},
        upsert=True 
    )

