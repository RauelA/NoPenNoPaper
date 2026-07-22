from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

load_dotenv()


#***          ***#
#***   LLMs   ***#
#***          ***#

creative_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.25
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

    def run(self, world_details: str, language: str):

        prompt = f"""
            You are an experienced screenwriter.
            
            Create a game world. 
            
            Requirements:
            {world_details}
            Language: {language}
            
            Return ONLY:
            
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

    def run(self, player_details: str, language: str):

        prompt = f"""
        
            Create a player character based on following details:
            {player_details}
                        
            Return ONLY:
            
            Name:
            Race:
            Class:
            Skills:
            Details:
            
            IMPORTANT:
            - Write in {language}.
            - Write the Name pure as Name without its Race or Class.
            - Write Race in singular.
            - Write Class as whats fits most to the genre.
            - Write the Details in 3 bullet points, each with up to 3 words.
            """

        return self.invoke(prompt)


#***                         ***#
#***   Environment Builder   ***#
#***                         ***#

class EnvironmentBuilder(BaseAgent):

    def run(self, world: str, language: str):

        prompt = f"""
            Generate the current environment.
            
            Requirements:
            World: {world}
            Language: {language}
            
            Return ONLY:
            
            Time:
            Weather:
            """

        return self.invoke(prompt)


#***                  ***#
#***   Scene Writer   ***#
#***                  ***#

class SceneWriter(BaseAgent):

    def create_start_scene(self, world: str, player: str, language: str):

        prompt = f"""
        
            Create the first playable location in two sentences.
            
            Requirements:
            World: {world}
            Player: {player}
            Language: {language}
            
            Return ONLY:
            
            Name:
            Details:
            """

        return self.invoke(prompt)


    def create_next_scene(self, world, player, previous_scene, action, language: str):
        prompt = f"""
        
            World: {world}
            
            Player: {player}

            Previous Scene: {previous_scene}

            Player Action: {action}
            
            Language: {language}


            Create the next scene based on the player's action.

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

    def create(self, world: str, scene: str, language: str):

        prompt = f"""
        
            World: {world}

            Scene: {scene}
            
            Language: {language}
            
            Create one memorable NPC.
            
            Return ONLY:
            
            Name:
            Personality:
            Knows:
            """

        return self.invoke(prompt)


#***              ***#
#***   Narrator   ***#
#***              ***#

class Narrator(BaseAgent):

    def describe(
        self,
        world: str,
        player: str,
        environment: str,
        scene: str,
        action: str,
        language: str
    ):

        prompt = f"""
        You are a storyteller.

        World: {world}
        
        Player: {player}

        Environment: {environment}

        Current Scene: {scene}

        Player Action: {action}

        Describe what happens using an immersive narrative.

        IMPORTANT:
        - Write the scene in {language}.
        - Speak about the player in the second person singular.
        - Include the player's action naturally.
        - Describe consequences of the action.
        - Do not mention game mechanics.
        - Write only 1-2 sentences.
        """

        return self.invoke(prompt)


    def describe_impossible_action(
            self,
            world: str,
            environment: str,
            scene: str,
            action: str,
            reason: str,
            language: str = "English"
    ):
        prompt = f"""
        You are a storyteller.

        World:
        {world}

        Environment:
        {environment}

        Current Scene:
        {scene}

        Player Action:
        {action}

        Reason the action is impossible:
        {reason}

        Describe why the action cannot be performed.

        IMPORTANT:
        - Write in {language}.
        - Speak about the player in the second person singular.
        - Write only 1 sentence with less than 15 words.
        - Do not progress the scene.
        - Do not invent alternative outcomes.
        - Do not mention game mechanics.
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
        action: str,
        language: str
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
            <reason in {language}>
            """

        return self.invoke(prompt)


#***                ***#
#***   Game Ender   ***#
#***                ***#

class GameEnder(BaseAgent):

    def check(self, player: str, world: str, quest_state: str, language: str):

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
            <ending text in {language}>
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