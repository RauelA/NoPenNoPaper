from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from graph import graph


app = FastAPI()


# =====================================================
# Game Session
# =====================================================

config = {
    "configurable": {
        "thread_id": "game_1"
    }
}


class ActionRequest(BaseModel):
    action: str



# =====================================================
# Start Game
# =====================================================

@app.get("/api/start")
def start_game():

    state = {

        "player_prompt": 
            "Name: Rauel, Dwarven Mage, Fire Magic, Likes carving",

        "world_prompt":
            "Fantasy, Middleearth",

        "player": "",
        "world": "",
        "environment": "",

        "current_scene": "",
        "scene_description": "",

        "current_npc": "",

        "inventory": [],
        "visited_scenes": [],

        "quest_state": "",

        "player_action": "",
        "validation": "",

        "game_status": ""
    }


    result = graph.invoke(
        state,
        config=config
    )


    return {
        "scene": result["scene_description"]
    }



# =====================================================
# Player Action
# =====================================================

@app.post("/api/action")
def action(request: ActionRequest):


    result = graph.invoke(
        {
            "player_action": request.action
        },
        config=config
    )


    return {
        "scene": result["scene_description"],
        "validation": result["validation"]
    }



# =====================================================
# Frontend
# =====================================================

app.mount(
    "/",
    StaticFiles(directory="frontend", html=True),
    name="frontend"
)