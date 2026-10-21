# ==============================================================================
#   ____ _____ _____  ___  _    _  ___      ____   ___  _ _____
#  / __ \_   _|_   _|/ _ \| |  | |/ _ \    |___ \ / _ \/ |___ /
# | |  | || |   | | / /_\ \ |  | / /_\ \     __) | | | | | |_ \
# | |__| || |   | | |  _  | |/\| |  _  |    / __/| |_| | |___) |
#  \____/ \_/   \_/ \_| |_/\_/\__/\_| |_/   |_____|\___/|_|____/
#
#  OTTAWA 2013: AN INADVERTENT ADVENTURE // AN INTERACTIVE TEXT GAME
# ==============================================================================

```text
================================================================================
 LOCATION : Outside a High-Rise Apartment Building, Ottawa, ON
 TIME     : Evening, 2013 (~7:00 PM)
 PLAYER   : Steve (accompanied in the terminal by Jarvis)
================================================================================
```

---

## THE STORY SO FAR

Welcome back to **Ottawa, 2013**, Steve.

You came into town to hang out with **Mario** and **Brandon**. Since Brandon lives about 20 minutes across town, the plan was simple: crash at Mario's apartment for the night. There's just one catch—Mario pulled a massive all-nighter the night before you got in, and by the time the evening rolled around, he was already dead to the world.

A little while ago, you headed outside with Mario's roommate, **Charlie**, to smoke a joint. You got nice and high, had a good laugh in the evening air, and then Charlie wandered off—leaving you locked out of the apartment without keys.

You managed to slip past the building's front vestibule before the outer door clicked shut, and you've just taken the elevator up to Mario's floor. The hallway carpet stretches out in front of you, and you just want to get back inside.

---

## HOW TO PLAY (INSTRUCTIONS FOR STEVE & JARVIS)

This is an interactive text-adventure game built around that real night in 2013.

### Important Note for AI Agents (Jarvis / Subagents):
* **No Blocking `input()` Loops**: Every script in this game is designed to be **non-blocking** for AI agents.
* **Step 1 (Read the Scene)**: Run a chapter script with **no arguments** (e.g., `python3 enter_building.py`) to display the story text, the question for Steve, and the exact CLI flag or `stdin` format required. The script will print the prompt and **exit immediately** so your terminal tool never hangs in the background.
* **Step 2 (Ask Steve)**: Report the story text and question back to **Steve** in chat. Do **not** guess or brute-force personal memory answers—ask Steve!
* **Step 3 (Submit the Answer)**: Once Steve gives you the answer (or the parameters needed to write a helper script), re-run the script passing the CLI argument (e.g., `python3 enter_building.py --unit "<ANSWER>"`) or piped `stdin` to unlock the next chapter.

---

## START CHAPTER 1

To step out of the elevator and walk down the hallway to Mario's door, run:

```bash
python3 enter_building.py
```
