from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from graph import creation_graph
from graph import game_graph

app = FastAPI()

game_state = {}


# =====================================================
# Game Session
# =====================================================

config={
 "configurable":{
    "thread_id":"game_1"
 }
}


class ActionRequest(BaseModel):
    action: str



# =====================================================
# Start Game
# =====================================================

class StartRequest(BaseModel):

    language: str

    universe: str

    player: str

@app.post("/api/start")
def start_game(request: StartRequest):

    initial_state = {

        "player_prompt":
            request.player,

        "world_prompt":
            request.universe,

        "language":
            request.language,

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

    global game_state

    game_state = creation_graph.invoke(
        initial_state,
        config=config
    )

    return {
        "scene": game_state["scene_description"],
        "player": game_state["player"]
    }



# =====================================================
# Player Action
# =====================================================

@app.post("/api/action")
def action(request: ActionRequest):

    global game_state

    result = game_graph.invoke(
        {
            "player_action": request.action
        },
        config=config
    )

    game_state = result

    return {
        "scene": result["scene_description"]
    }



# =====================================================
# Frontend
# =====================================================

app.mount(
    "/",
    StaticFiles(directory="frontend", html=True),
    name="frontend"
)