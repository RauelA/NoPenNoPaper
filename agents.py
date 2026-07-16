from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

load_dotenv()


#***          ***#
#***   LLMs   ***#
#***          ***#

creative_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5
)

precise_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


#***                ***#
#***   Base Agent   ***#
#***                ***#

class BaseAgent:

    def __init__(self, llm):
        self.llm = llm

    def invoke(self, prompt: str) -> str:
        return self.llm.invoke(prompt).content


#***                   ***#
#***   World Builder   ***#
#***                   ***#

class WorldBuilder(BaseAgent):

    def run(self, world_details: str):

        prompt = f"""
            You are an experienced fantasy screenwriter.
            
            Create a game world.
            
            Requirements:
            {world_details}
            
            Return ONLY:
            
            Language:
            Genre:
            Universe:
            Quest:
            Physics:
            """

        return self.invoke(prompt)


#***                    ***#
#***   Player Builder   ***#
#***                    ***#

class PlayerBuilder(BaseAgent):

    def run(self, player_details: str):

        prompt = f"""
            Create a player character.
            
            Requirements:
            {player_details}
            
            Return ONLY:
            
            Name:
            Race/Class:
            Skills:
            Details:
            """

        return self.invoke(prompt)


#***                         ***#
#***   Environment Builder   ***#
#***                         ***#

class EnvironmentBuilder(BaseAgent):

    def run(self, world: str):

        prompt = f"""
            World:
            
            {world}
            
            Generate the current environment.
            
            Return ONLY:
            
            Time:
            Weather:
            """

        return self.invoke(prompt)


#***                  ***#
#***   Scene Writer   ***#
#***                  ***#

class SceneWriter(BaseAgent):

    def create_start_scene(self, world: str):

        prompt = f"""
            World:
            
            {world}
            
            Create the first playable location.
            
            Return ONLY:
            
            Name:
            Details:
            Info Source:
            """

        return self.invoke(prompt)

    def create_next_scene(self, world: str, previous_scene: str):

        prompt = f"""
            World:
            
            {world}
            
            Previous Scene:
            
            {previous_scene}
            
            Create the next scene.
            
            Include:
            
            - location
            - obstacle
            - interesting object
            
            Return ONLY:
            
            Name:
            Details:
            Obstacle:
            """

        return self.invoke(prompt)


#***                ***#
#***   NPC Writer   ***#
#***                ***#

class NPCWriter(BaseAgent):

    def create(self, world: str, scene: str):

        prompt = f"""
            World:
            
            {world}
            
            Scene:
            
            {scene}
            
            Create one memorable NPC.
            
            Return ONLY:
            
            Name:
            Occupation:
            Appearance:
            Personality:
            Knows:
            """

        return self.invoke(prompt)


#***              ***#
#***   Narrator   ***#
#***              ***#

class Narrator(BaseAgent):

    def describe(self, world: str, environment: str, scene: str):

        prompt = f"""
            You are a fantasy storyteller.
            
            World:
            {world}
            
            Environment:
            {environment}
            
            Scene:
            {scene}
            
            Describe the location in immersive prose in German.
            
            Do not mention game mechanics.
            """

        return self.invoke(prompt)


#***               ***#
#***   Validator   ***#
#***               ***#

class Validator(BaseAgent):

    def validate(
        self,
        player: str,
        world: str,
        environment: str,
        scene: str,
        action: str
    ):

        prompt = f"""
            You are an experienced Pen & Paper Game Master.
            
            Player:
            {player}
            
            World:
            {world}
            
            Environment:
            {environment}
            
            Scene:
            {scene}
            
            Player Action:
            
            {action}
            
            Determine whether the action is possible.
            
            If possible answer ONLY:
            
            YES
            
            Otherwise answer:
            
            NO:
            <reason>
            """

        return self.invoke(prompt)


#***                ***#
#***   Game Ender   ***#
#***                ***#

class GameEnder(BaseAgent):

    def check(self, player: str, world: str, quest_state: str):

        prompt = f"""
            World:
            {world}
            
            Player:
            {player}
            
            Quest:
            
            {quest_state}
            
            Has the main quest ended?
            
            Answer ONLY:
            
            CONTINUE
            
            or
            
            GAME OVER:
            <ending text>
            """

        return self.invoke(prompt)


#***               ***#
#***   Instances   ***#
#***               ***#

player_builder = PlayerBuilder(creative_llm)

world_builder = WorldBuilder(creative_llm)

environment_builder = EnvironmentBuilder(creative_llm)

scene_writer = SceneWriter(creative_llm)

npc_writer = NPCWriter(creative_llm)

narrator = Narrator(creative_llm)

validator = Validator(precise_llm)

game_ender = GameEnder(precise_llm)