# ------------- Decision Making (Nathan) -------------
class Task:
    """Mock task class"""
    def init__(self,name,description,progress=False):
        self.name=name
        self.description=description
        self.progress=progress

class NPC:
    """Mock NPC class"""
    def __init__(self,name,dialogue_options):
        self.name=name
        self.dialouge_option=dialogue_options

class Player:
    """Mock player class"""
    def __init__ (self, stats, items):
        self.stats=stats
        self.items=items
    
def dialogue_and_choice(dialogue_options,choice,player):
    """
    Decision making and processing for players interaction and conversation
    
    Parameters:
        dialouge_options (dict): Every choice must contain all values
        dict in dict, key number optons and inside key for content response
            "text" (str) Players options
            "response" (str) NPC response to a player choice
            "available (bool) if available true or false
            "requires" (dict) Requirements needed like {"itms": item_name,
            "min_stats: from player} 
            "locked_message" (str) reply is requirements are not met
            "task" (Task) returns task or no task
            "unlocks" (list) number of options to make task or response 
            available
            "removes" (list) options to remove responses or tasks
        choice (int): player choice to respond
        player (class) holds info of player maybe in a dict or attributes 
        to make decisions based on player 
    
    Returns:
        tuple(str, Task): gives response to player and a task if they get one
    Side effects:
        Options can be altered and av can be available changed in dialouge 
        options for an NPC
    """
    
    #Valid
    if not isinstance(choice, int) or choice not in dialogue_options:
        return "Invalid response."
    
    option=dialogue_options[choice]
    if not option.get("available",True):
        return "Invalid choice"
    
    #Requirements
    requirements=option["requires"]
    for item in requirements["items"]: 
        if item not in player["items"]:
            return option["locked_message"]
        
    for stat, minimum in requirements["min_stats"].items():
        if player["stats"].get(stat,0)<minimum:
            return option["locked_message"]
    #Availability
    for key in option["unlocks"]:
        if key in dialogue_options:
            dialogue_options[key]["avaliable"]=True
    
    for key in option["removes"]:
        if key in dialogue_options:
            dialogue_options[key]["avaiable"]=False
    #NPC response
    return option["response"], option["task"]

# ------------- Task Completion (Justin) -------------

class TaskCompletion:
    """
    Handle task and mission completion.

    Checks player requirements, tracks completed missions,
    removes required items, and distributes rewards.
    """

    def __init__(self):
        """Initializes the task completion system."""
        self.completed_tasks = set()

    def complete_task(self, task_name, character, task_requirements, task_rewards):
        """
        Will attempt to complete a task based on player requirements.

        Args:
            task_name (str): Name of the task or mission.
            character (dict): Dictionary containing player
                level, skills, and inventory.
            task_requirements (dict): Requirements needed to
                complete the task.
            task_rewards (dict): Rewards received after
                successfully completing the task.

        Returns:
            bool: True if the task is completed.
                  False if requirements are not met.

        Side Effects:
            Updates player progression, awards rewards,
            and removes required items when necessary.
        """

        # Check if the task was already completed.
        if task_name in self.completed_tasks:
            return False

        # Get player information.
        level = character.get("level", 0)
        skills = character.get("skills", {})
        inventory = character.get("inventory", {})

        # Check required player level.
        required_level = task_requirements.get("level", 0)

        if level < required_level:
            return False

        # Check required skills.
        required_skills = task_requirements.get("skills", {})

        for skill, amount in required_skills.items():
            if skills.get(skill, 0) < amount:
                return False

        # Check required inventory items.
        required_items = task_requirements.get("items", {})

        for item, amount in required_items.items():
            if inventory.get(item, 0) < amount:
                return False

        # Check prerequisite missions.
        prerequisites = task_requirements.get(
            "prerequisite_tasks", []
        )

        for task in prerequisites:
            if task not in self.completed_tasks:
                return False

        # Remove required items if necessary.
        if task_requirements.get("consume_items", False):
            for item, amount in required_items.items():
                inventory[item] -= amount

                if inventory[item] == 0:
                    del inventory[item]

        # Mark the task as completed.
        self.completed_tasks.add(task_name)

        # Award experience points and gold.
        character["xp"] = (
            character.get("xp", 0) + task_rewards.get("xp", 0)
        )

        character["gold"] = (
            character.get("gold", 0) + task_rewards.get("gold", 0)
        )

        # Add reward items to the player's inventory.
        reward_items = task_rewards.get("items", {})

        for item, amount in reward_items.items():
            inventory[item] = inventory.get(item, 0) + amount

        return True

