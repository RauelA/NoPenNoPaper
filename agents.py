# Install:
#   pip install langchain "langchain[openai]" langchain-tavily langgraph python-dotenv




from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv(".env")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

tavily = TavilySearch(max_results=5, api_key=TAVILY_API_KEY)
tools = [tavily]







# Screenwriter: World
# Screenwriter: Player
# Screenwriter: Story
# Screenwriter: Scenes List
# Screenwriter: NPCs List

# Narrator

# Validator

# GameEnder



# Truncator (?)
# => Oder lieber bei Agents direkt integrieren?


# world_prompt = ""
# player_prompt = ""
# story_prompt = ""
# scene_prompt = [""]
# npc_prompt = [""]


# def add_to_world(content: str):
#    world_prompt = world_prompt + ", " + content

# ...






player_prompt = "Name: Rauel, Race/Class: Dwarven-Mage, Skills: Fire magic, Alchemy, Details: Likes carving, Hates spiders"
world_prompt = "Language: English, Universe: Middleearth, Genre: Middleearth, Physics: Earth"
environment_prompt = "Time: Day, Weather: Sunny"
scene_prompt = ["Name: Tavern 'Golden Boar', Details: Owned by Hergion Thunderwall"]


#***                  ***#
#***   Screenwriter   ***#
#***                  ***#

screenwriter = ChatOpenAI(model="gpt-4o-mini", temperature=0.25)

#***   Tools   ***#

@tool
def setPlayerInfo(player_details: str) -> str:
    """
    Creates a fictional world and story and returns a string.
    """

    prompt = f"""
        You are an experienced screenwriter.
        Set the player characteristics based on {player_details}.

        Answer as string in the following format:
        "
        Name: ... (eg. Talos),
        Race/Class: ... (eg. Dwarven-Mage),
        Skills: ... (eg. Fire magic, Alchemy),
        Details: ... (eg. Likes carving, Hates spiders)
        "
        """

    return screenwriter.invoke(prompt).content


@tool
def createWorld(world_details: str) -> str:
    """
    Creates a fictional world and story and returns a string.
    """

    prompt = f"""
        You are an experienced screenwriter.
        Create a world about {world_details}.

        Answer as string in the following format:
        "
        Language: ... (eg. English),
        Genre: ... (eg. Fantasy),
        Universe: ... (eg. Middleearth),
        Quest: ... (eg. Find Frodo in the Dead Marshes),
        Physics: ... (eg. Earth physics with Middleearth magic)
        "
        """

    return screenwriter.invoke(prompt).content


@tool
def createEnvironment() -> str:
    """
    Creates time and weather in the given world and returns a string.
    """

    prompt = f"""
        You are an experienced screenwriter.
        Define time and weather in {world_prompt}.

        Answer as string in the following format:
        "
        Time: ... (eg. Day),
        Weather: ... (eg. Sunny)
        "
        """

    return screenwriter.invoke(prompt).content


@tool
def createStartScene() -> str:
    """
    Creates a scenery in the given world and returns a string.
    """

    prompt = f"""
        You are an experienced screenwriter.
        Create a start scene in {world_prompt}.
        Also create a character, that the player has to talk to the get quest information.

        Answer as string in the following format:
        "
        Name: ... (eg. Tavern 'Golden Boar'),
        Details: ... (eg. Owned by Hergion Thunderwall),
        Info-Source: ... (eg. Hergion Thunderwall)
        "
        """

    return screenwriter.invoke(prompt).content


@tool
def createNextScene() -> str:
    """
    Creates a scenery in the given world and the last scenery and returns a string.
    """

    prompt = f"""
        You are an experienced screenwriter.
        Create a new scene in {world_prompt}. The last scene was {scene_prompt[-1]}.
        Create a small obstacle for the player to overcome.

        Answer as string in the following format:
        "
        Name: ... (eg. Marketplace),
        Details: ... (eg. Fountain in the center),
        Obstacle: ... (eg. Fountain in the center)
        "
        """
    
    return screenwriter.invoke(prompt).content



screenwriter_player = screenwriter.bind_tools(setPlayerInfo)
screenwriter_world  = screenwriter.bind_tools(createWorld)
screenwriter_story  = screenwriter.bind_tools(createEnvironment)
screenwriter_scene  = screenwriter.bind_tools(createStartScene)
screenwriter_npc    = screenwriter.bind_tools(createNextScene)



#***              ***#
#***   Narrator   ***#
#***              ***#

narrator = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

#***   Tools   ***#

@tool
def describeScene() -> str:
    """
    Describes a scenery and returns a string.
    """

    prompt = f"""
        You are a storyteller.
        Describe the scene {scene_prompt[-1]} with flowery words.
        """

    return narrator.invoke(prompt).content


narrator_scene = narrator.bind_tools(describeScene)






#***               ***#
#***   Validator   ***#
#***               ***#

validator = ChatOpenAI(model="gpt-4o-mini", temperature=0)

#***   Tools   ***#

@tool
def validateAction(action) -> str:
    """
    Validates weather an action of a player is possible or not
    """

    prompt = f"""
        You are an experienced Pen&Paper game master.
        The player is {player_prompt} and in the world {world_prompt}.
        The scenery is {scene_prompt[-1]} with {environment_prompt}.
        Is the action {action} possible/doable?

        If yes, simply answer "Yes". 
        If not, answer as string in the following format: "You cannot do that, because ..." (and describe the reason for the impossibility)        
        """

    return validator.invoke(prompt).content


validator_action = validator.bind_tools(validateAction)








model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
model_with_tools = model.bind_tools(tools)


# A "node" is just a function: state in, state-update out.
def call_model(state: MessagesState):
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}


workflow = StateGraph(MessagesState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END, 
    },
)

workflow.add_edge("tools", "agent")

app = workflow.compile()

if __name__ == "__main__":
    user_prompt = input("What is your question: ")
    inputs = {"messages": [{"role": "user", "content": user_prompt}]}

    for chunk in app.stream(inputs, stream_mode="updates"):
        for node, update in chunk.items():
            print(f"Output from node '{node}':")
            print("---")
            for message in update["messages"]:
                message.pretty_print()
            print("\n---\n")