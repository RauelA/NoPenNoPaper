from graph import graph


def init():

    print("MAIN START")

    config = {
        "configurable": {
            "thread_id": "game_1"
        }
    }

    state = {
        "player_prompt": "Name: Rauel, Dwarven Mage, Fire Magic, Likes carving",
        "world_prompt": "Fantasy, Middleearth",

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

        "game_status": "",
    }


    print("CALLING GRAPH")

    result = graph.invoke(
        state,
        config=config
    )

    print("\n=== PLAYER ===")
    print(result["player"])

    print("\n=== WORLD ===")
    print(result["world"])

    print("\n=== ENVIRONMENT ===")
    print(result["environment"])

    print("\n=== SCENE ===")
    print(result["current_scene"])

    print("\n=== NPC ===")
    print(result["current_npc"])

    print("\n=== DESCRIPTION ===")
    print(result["scene_description"])


if __name__ == "__main__":
    init()


"""
    while True:

        action = input("\n> ")

        result["player_action"] = action

        result = graph.invoke(result)

        print(result["validation"])

        print(result["scene_description"])

        if result["game_status"].startswith("GAME OVER"):
            print(result["game_status"])
            break
"""