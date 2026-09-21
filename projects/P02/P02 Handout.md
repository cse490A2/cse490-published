# Project 2: Insert Prompt to Play

**Due: Tuesday 11:59 pm**  
Prerequisites: Follow the [prereq instructions](Setup.md) to set up your AI workspace. We will be using [Visual Studio Code](https://code.visualstudio.com) (VS Code) as our IDE for this course and [LiteLLM as our model gateway](https://www.litellm.ai).

Which of the course's models can build a working program from one spec, and what does it take to fix the ones that can't? That's the project. The spec is an arcade game in a single HTML file, so you judge every answer the same way: open it in a browser and play.

Everyone starts with the same spec: Breakout doubles. It's Breakout with a twist no model has seen before: your paddle on the left half, a computer teammate's paddle on the right half that chases the ball on its own but only so fast, so it can miss. You write the prompt once, send it to each model, save each reply as a game file, and play it. Some will work first try. Most of the failures will be quiet: a teammate that never moves, or one that cheats. You fix one by changing the ask, not the code. Then, if you want to make it awesome, write a spec of your own: a blend of two arcade games.

## Instructions

1. Open your project folder in VS Code. Also open the LiteLLM extension. Refer to the [prereq instructions](Setup.md).  
2. Write your prompt in PROMPT.md. It already holds the Breakout doubles prompt. Fill in its Theme section: the colours, the teammate's name, and the words on the end screens. Keep the teammate's 3-pixel speed cap and the centre line; that is where the game breaks. If you are stuck, talk to a model on LiteLLM\!  
3. Once PROMPT.md is finished, send it to each model from the model selection menu below the prompt box. Sometimes, VS Code will suggest a file to attach to the prompt. Since we're evaluating every model against the same prompt, make sure that no other file is being fed into the model. Once a model is finished, start a new chat and switch to a different model under LiteLLM Bedrock. Save each created game as \<GAME\_NAME\>\_\<MODEL\_NAME\>.html.  
4. With every model response, document the model type, how long it took, and the number of turns/steps it took in SCORECARD.md.  
5. Now spend about 1 minute playing each created game, watching the right half. They can be played by opening the file in your browser. Continue filling out SCORECARD.md, documenting whether the game is playable, likes, dislikes, and what surprised you. Most of these models should be able to decently one-shot the output\!  
6. However, there may be a model that fails. In this case, use the same model that failed and continue prompting until you're satisfied with its output. Change the ask, not the code. Document the additional prompts in SCORECARD.md.

## Make it awesome

This part is optional. Write a spec of your own that blends two arcade games: Pong played on Frogger's road, Galaga with Mappy's trampolines, whatever you can picture. Put it in PROMPT2.md, in the shape of the Breakout doubles prompt: the constraints, the rules, one or two examples, and the output format. Then repeat steps 3 to 6 with it: every model, a game file per model named after your game, a SCORECARD.md line for each, and extra prompting for the one that failed.

Some examples of arcade games:

* [Pong](https://en.wikipedia.org/wiki/Pong)  
* [Frogger](https://en.wikipedia.org/wiki/Frogger)  
* [Mappy](https://en.wikipedia.org/wiki/Mappy)  
* [Galaga](https://en.wikipedia.org/wiki/Galaga)

## Turnin

By Tuesday 11:59 pm, on the Project 2 assignment in Canvas:

* Upload PROMPT.md and SCORECARD.md.  
* Upload every game file you saved, one per model.  
* If you made it awesome, upload PROMPT2.md and its game files too.  
* Submit as Upload: all of the files together, in one submission. Leave .env out.

## Grading

A model will autograde your submission. It checks that each step was properly followed: the Breakout doubles prompt in PROMPT.md, one game file per model you ran, at least 3 models, a SCORECARD.md block for each of them, and the extra prompts for any model that failed. If you made it awesome, it checks the same for PROMPT2.md and its games. Every check is pass or fail. It does not judge code style, prompt wording, how good the game is, or how many tries it took.

## Reference

The Breakout doubles prompt, to start from:  
Write a Breakout doubles game I can play in my browser with a computer teammate. Constraints: one complete HTML file with the CSS and JavaScript inline. No external libraries, fonts, images, or network requests. A 480 by 320 canvas. Two paddles side by side along the bottom: mine on the left half, moved with the left and right arrow keys and never crossing the centre line; the computer's on the right half, which moves toward the ball on its own by at most 3 pixels per frame and never crosses the centre line either. One ball. Six rows of ten bricks. The ball bounces off the walls, both paddles, and the bricks, and a brick disappears when it is hit. The score is shared and drawn on the canvas. When the ball falls below the paddles the game shows GAME OVER; when every brick is gone it shows YOU WIN; pressing Space restarts. Use requestAnimationFrame for the game loop. No alert or prompt dialogs. Keep it under 150 lines. Examples: the ball starts resting on my paddle and launches upward when Space is pressed. When the ball comes down on the right half, the computer paddle slides under it; if the ball is moving sideways faster than the paddle can, the computer misses and the ball is lost. Output format: reply with the HTML file in one code block and nothing else.  
