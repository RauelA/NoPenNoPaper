from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from langgraph.checkpoint.memory import MemorySaver

from agents import (
    player_builder,
    world_builder,
    environment_builder,
    scene_writer,
    npc_writer,
    narrator,
    validator,
    game_ender,
)


#***                ***#
#***   Game State   ***#
#***                ***#

class GameState(TypedDict):

    # initial input
    player_prompt: str
    world_prompt: str
    language: str

    # generated
    player: str
    world: str
    environment: str

    current_scene: str
    scene_description: str

    current_npc: str

    # gameplay
    inventory: list[str]
    visited_scenes: list[str]
    quest_state: str

    player_action: str
    validation: str

    game_status: str


#***           ***#
#***   Nodes   ***#
#***           ***#

def create_player(state: GameState):

    player = player_builder.run(
        state["player_prompt"],
        state["language"]
    )
    print(player)

    return {
        "player": player
    }


def create_world(state: GameState):

    world = world_builder.run(
        state["world_prompt"],
        state["language"]
    )
    print(world)

    return {
        "world": world
    }


def create_environment(state: GameState):

    environment = environment_builder.run(
        state["world"],
        state["language"]
    )
    print(environment)

    return {
        "environment": environment
    }


def create_start_scene(state: GameState):

    scene = scene_writer.create_start_scene(
        state["world"],
        state["player"],
        state["language"]
    )
    print(scene)

    return {
        "current_scene": scene,
        "visited_scenes": [scene]
    }


def narrate_scene(state):

    description = narrator.describe(
        state["world"],
        state["player"],
        state["environment"],
        state["current_scene"],
        state["player_action"],
        state["language"]
    )

    return {
        "scene_description": description
    }



#***              ***#
#***   Gameplay   ***#
#***              ***#

def validate_player_action(state: GameState):

    result = validator.validate(
        state["player"],
        state["world"],
        state["environment"],
        state["current_scene"],
        state["player_action"],
        state["language"]
    )
    print(result)

    return {
        "validation": result
    }


def next_scene(state: GameState):

    print("PLAYER ACTION:")
    print(state["player_action"])

    print("OLD SCENE:")
    print(state["current_scene"])

    scene = scene_writer.create_next_scene(
        state["world"],
        state["player"],
        state["current_scene"],
        state["player_action"],
        state["language"]
    )

    print("NEW SCENE:")
    print(scene)

    return {
        "current_scene": scene,
        "visited_scenes": state["visited_scenes"] + [scene]
    }


def narrate_next_scene(state):

    description = narrator.describe(
        state["world"],
        state["player"],
        state["environment"],
        state["current_scene"],
        state["player_action"],
        state["language"]
    )

    return {
        "scene_description": description
    }


def narrate_invalid_action(state):

    description = narrator.describe_impossible_action(
        state["world"],
        state["environment"],
        state["current_scene"],
        state["player_action"],
        state["validation"],
        state["language"]
    )

    return {
        "scene_description": description
    }


def check_game_end(state: GameState):

    result = game_ender.check(
        state["player"],
        state["world"],
        state["quest_state"],
        state["language"]
    )
    print(result)

    return {
        "game_status": result
    }


#***             ***#
#***   Routing   ***#
#***             ***#

def action_router(state: GameState):

    validation = state["validation"]

    if validation.startswith("YES"):
        return "next_scene"

    return "invalid_action"


def ending_router(state: GameState):

    if state["game_status"].startswith("GAME OVER"):
        return END

    return "wait_for_player"


#***                 ***#
#***   Placeholder   ***#
#***                 ***#

def invalid_action(state: GameState):
    return {}


def wait_for_player(state: GameState):

    action = interrupt(
        {
            "message": "What do you want to do?"
        }
    )

    return {
        "player_action": action
    }



#***                 ***#
#***   Build Graph   ***#
#***                 ***#

creation_builder = StateGraph(GameState)

creation_builder.add_node("create_player", create_player)
creation_builder.add_node("create_world", create_world)
creation_builder.add_node("create_environment", create_environment)
creation_builder.add_node("create_start_scene", create_start_scene)
creation_builder.add_node("narrate_scene", narrate_scene)
creation_builder.add_node("next_scene", next_scene)
creation_builder.add_node("narrate_next_scene", narrate_next_scene)
creation_builder.add_node("check_game_end", check_game_end)
creation_builder.add_node("invalid_action", invalid_action)
creation_builder.add_node("wait_for_player", wait_for_player)


#***                              ***#
#***   Initial Story Generation   ***#
#***                              ***#

creation_builder.add_edge(START, "create_player")
creation_builder.add_edge("create_player", "create_world")
creation_builder.add_edge("create_world", "create_environment")
creation_builder.add_edge("create_environment", "create_start_scene")
creation_builder.add_edge("create_start_scene", "narrate_scene")
creation_builder.add_edge("narrate_scene", END)


#***                   ***#
#***   Gameplay Loop   ***#
#***                   ***#

"""
         validate_action
                │
        YES ────┴──── NO
         │             │
         ▼             ▼
        next_scene  invalid_action
         │             │
         ▼             ▼
 narrate_next_scene
                       │
                       ▼
           narrate_invalid_action
                       │
                       ▼
                 wait_for_player
"""

game_builder = StateGraph(GameState)

game_builder.add_node("validate_action", validate_player_action)
game_builder.add_node("next_scene", next_scene)
game_builder.add_node("narrate_next_scene", narrate_next_scene)
game_builder.add_node("narrate_invalid_action", narrate_invalid_action)
game_builder.add_node("check_game_end", check_game_end)
game_builder.add_node("invalid_action", invalid_action)
game_builder.add_node("wait_for_player", wait_for_player)

game_builder.add_edge(START, "validate_action")
game_builder.add_edge("invalid_action", "narrate_invalid_action")
game_builder.add_edge("narrate_invalid_action", "wait_for_player")
game_builder.add_edge("next_scene", "narrate_next_scene")
game_builder.add_edge("narrate_next_scene", "check_game_end")

game_builder.add_conditional_edges(
    "validate_action",
    action_router,
    {
        "next_scene": "next_scene",
        "invalid_action": "invalid_action",
    },
)


game_builder.add_conditional_edges(
    "check_game_end",
    ending_router,
    {
        "wait_for_player": "wait_for_player",
        END: END,
    },
)


#***            ***#
#***   Memory   ***#
#***            ***#

memory = MemorySaver()

creation_graph = creation_builder.compile(
    checkpointer=memory
)

game_graph = game_builder.compile(
    checkpointer=memory
)

