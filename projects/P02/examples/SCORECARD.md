This is an example document. It does not represent accurate information.

# Scorecard

Template: p02-scorecard-v2  

The three course models each have a block below; fill them in as you go. Copy a block for any extra model, and for each game from your own spec.
Keep the field names exactly as they are. Write your answer after the colon. The course gateway records your prompts, how long each answer took, and how many turns you sent, so none of that goes here.

- Model: the model's name exactly as the picker shows it.
- Prompt file: PROMPT.md, or PROMPT2.md for a game from your own spec.
- Game file: the exact name of the file you saved for this model.
- Playable: yes or no.

---

## Model: external/zai.glm-5

Prompt file: PROMPT.md  
Game file: BreakoutDoubles_zai.glm-5.html  
Playable: yes  
Liked: The model added a menu screen and pause screen in this game. I liked how the player can pause and restart the game.  
Disliked: It took multiple turns to get the html file correct. The first output had a few bugs it needed to fix. After 3 more turns, the model produced good code.  
Surprised me: Each response was super fast. It seemed as if the model did not use any thinking and prioritized speed over accuracy.  

---

## Model: external/haiku-4-5-20251001

Prompt file: PROMPT.md  
Game file: BreakoutDoubles_haiku-4-5-20251001.html  
Playable: yes  
Liked: The game rendered properly and the colors make it eye-catching. The physics worked and the ball properly interacted with other objects.  
Disliked: The CPU did not play well. It did a poor job hitting the ball back to the human player.  
Surprised me: I heard sound effects, even though that wasn't specified in the prompt.  

---

## Model: internal/Qwen3.6-35B-A3B

Prompt file: PROMPT.md  
Game file: BreakoutDoubles_Qwen3.6-35B-A3B.html  
Playable: no  
Liked: The bricks and paddles drew at the right sizes on the first try.  
Disliked: The teammate paddle never moved, so every ball on the right half was lost.  
Surprised me: The model insisted the teammate worked, even after I pasted the symptom back to it.  

---
