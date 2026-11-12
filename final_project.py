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