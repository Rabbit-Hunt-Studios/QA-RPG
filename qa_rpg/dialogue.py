from enum import Enum
from random import choice


class Dialogue(Enum):

    WALK_DIALOGUE = ["Wandered aimlessly around the corner.",
                     "Crept around the empty halls.",
                     "Cautiously looked at the dark paths.",
                     "Tread through the foul smells.",
                     "Stroll past the seemingly endless corridors.",
                     "Walked around the lifeless skeletons.",
                     "Leaped across over the corpses on the floor.",
                     "Howls and screams echo from in front of you."]
    BATTLE_DIALOGUE = [" jumps you from the shadows.",
                       " blocks your path.",
                       " rises from a pile of bones.",
                       " roars deafeningly from behind you.",
                       " obstructs you from going forward.",
                       "'s terrifying shadow looms over you."]
    MONSTER = ["Elite Goblin",
               "Blood Ogre",
               "Stone Golem",
               "Alpha Werewolf",
               "Crystallised Skeleton",
               "Fire Wyvern",
               "Frenzied Troll"]
    WIN_DIALOGUE = ["The monster draws its last breath.",
                    "You stand victoriously on top of the monster's corpse.",
                    "You slashed through the monster's torso.",
                    "The deceased body falls to the ground."]
    LOSE_DIALOGUE = ["The monster completely overpowers you.",
                     "You get caught the monster's rampage.",
                     "The monster smacks you across the room.",
                     "You can't seem to evade the monster's attacks."]
    RUN_FAIL_DIALOGUE = ["The monster stands tall in front of your escape route.",
                         "You struggle to run away but it utterly fails.",
                         "The monster attacks and diminishes your hope of escaping.",
                         "You stand there petrified in the gaze of the monster."]
    RUN_DIALOGUE = ["You cower in the face of the monster's strength.",
                    "The monster's inhuman power sends chills down your spine.",
                    "Fearing the monster's menacing gazes, you run away.",
                    "Just the thought of the monster frightens you to no end."]

    @property
    def get_text(self):
        return choice(self.value)
