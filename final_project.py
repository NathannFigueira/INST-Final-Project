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
        
# ------------------ Crafting (Akhila) ------------------

# ------------- Player status and health (Bohan) -------------
import json;
def load_player(path):
    """
    Load effect and state rules from the data file.

    Args:
        path (str): path to a JSON file with an "effects" dict and a
            "states" dict.

    Returns:
        dict: the parsed rules.
    """
    with open (path ,"r", encoding="UTF-8" ) as f:
        return json.load(f)

class Health:
    """
    Stores the player's health and stamina and their maximums.
    Values are always kept between 0 and the maximum. Only this class
    changes the numbers; everything else goes through apply_changes().
    """

    def __init__(self, max_health=100, max_stamina=100):
        self.max_health = max_health
        self.max_stamina = max_stamina
        self.health = max_health
        self.stamina = max_stamina

    def current(self, value, maximum):
        return max(0, min(value, maximum))

    def change_health(self, health_change = 0, stamina_change = 0):
        old_health = self.health
        old_stamina = self.stamina
        self.health = self.current(self.health + health_change, self.max_health)
        self.stamina = self.current(self.stamina + stamina_change, self.max_stamina)
        return self.health - old_health, self.stamina - old_stamina

    def _is_dead(self):
        return self.health ==0

    def __str__(self):
        return (f"HP {self.health}/{self.max_health} | "
                f"Stamina {self.stamina}/{self.max_stamina}")




class Status:
    """
    Tracks every buff/debuff and state on the player (poisoned, exhausted...).
    Holds a Health object and changes it only through Health's methods.
    All effects and thresholds come from the data file.
    """

    def __init__ (self, health_obj, data):
        self.health_obj = health_obj
        self.effect_rules = data["effects"]
        self.state_rules = data["states"]
        self.effects = {}     # name -> {"turns": turns left, "stacks": stacks}
        self.states = set()

    def take_turn(self, new_effects):
        """
        Run one turn of effects.

        Args:
            new_effects (list of str): names of the effects caused by this
                turn's action, e.g. ["poisoned", "crafting_cost"].

        Returns:
            dict: how much health and stamina changed, which effects
                started and ended, and whether health reached 0.

        Side effects:
            Updates this Status's effects and states, and changes health
            and stamina through Health.apply_changes().
        """
        # 1. Save current health, stamina, and effect names
        start_names = set(self.effects) | self.states
        start_health = self.health_obj.health
        start_stamina = self.health_obj.stamina

        # 2. Add new effects
        for name in new_effects:
            rule = self.effect_rules[name]
            for other in rule["cancels"]:
                self.effects.pop(other, None)
            if name not in self.effects:
                self.effects[name] = {"turns": rule["duration"], "stacks": 1}
            elif rule["on_repeat"] == "reset":
                self.effects[name]["turns"] = rule["duration"]
            elif rule["on_repeat"] == "stack":
                self.effects[name]["stacks"] += 1
            # "nothing": leave it as it is
        middle_names = set(self.effects) | self.states

        # 3. Add up all changes, then send the totals to Health in one call
        health_total = 0
        stamina_total = 0
        for name, info in self.effects.items():
            health_total += self.effect_rules[name]["health"] * info["stacks"]
            stamina_total += self.effect_rules[name]["stamina"] * info["stacks"]
        for state in self.states:
            health_total += self.state_rules[state]["health"]
            stamina_total += self.state_rules[state]["stamina"]
        self.health_obj.apply_changes(health_total, stamina_total)

        # 4. Check thresholds (new states only start working next turn)
        for state, rule in self.state_rules.items():
            value = (self.health_obj.health if rule["stat"] == "health"
                     else self.health_obj.stamina)
            if value < rule["below"]:
                self.states.add(state)
            else:
                self.states.discard(state)

        # 5. Count down every effect and remove the ones that ran out
        for name in list(self.effects):
            self.effects[name]["turns"] -= 1
            if self.effects[name]["turns"] == 0:
                del self.effects[name]
        end_names = set(self.effects) | self.states

        # 6. Set operations: which effects started and which ended
        started = (middle_names | end_names) - start_names
        ended = (start_names | middle_names) - end_names

        return {
            "health_change": self.health_obj.health - start_health,
            "stamina_change": self.health_obj.stamina - start_stamina,
            "started": started,
            "ended": ended,
            "health_zero": self.health_obj.is_dead(),
        }
def crafting(points, skill_level, items, item_desired):
    """
    Checks if the player has enough skill level and points to craft new objects,
    weapons, and survival necessities, and adds them to their inventory to 
    be used in the game and regulates the points and skill level of the player
    depending on what they are trying to unlock from the inventory.

    Args:
        points (int)- current point count for player
        skill_level (int)- current skill level
        items (dict)- items a player has
        item_desired (string)- name of object wanted by player

    Returns:
        Boolean- True if the crafting was successful and false if the craft 
        could not be done

    Side effects:
        Adds items to the dictionary if the player was able to gain any item

    """
    
    item_skill_level = {
        "sword": 3,
        "bomb": 6,
        "axe": 2,
        "hammer": 3,
        "gun": 5,
        "apple": 1,
        "meat": 3,
        "blanket": 1,
        "firewood": 2,
        "water": 1,
        "flashlight": 2
    }
    
    item_point_level = {
        "sword": 15,
        "bomb": 20,
        "axe": 10,
        "hammer": 7,
        "gun": 17,
        "apple": 2,
        "meat": 8,
        "blanket": 5,
        "firewood": 7,
        "water": 2,
        "flashlight": 4
    }
    
    if item_desired not in item_skill_level:
        return False
    
    if skill_level >= item_skill_level[item_desired] and \
        points >= item_point_level[item_desired]:
            
        items[item_desired] = items.get(item_desired,0) + 1
        
        points -= item_point_level[item_desired]
        
        return True
    
    else:
        if skill_level > 0:
            skill_level -= 1

        return False
    
