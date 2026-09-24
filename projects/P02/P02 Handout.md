# Project 2: Insert Prompt to Play

**Due: Tuesday 11:59 pm**  
Prerequisites: Follow the [prereq instructions](Setup.md) to set up your AI workspace. We will be using [Visual Studio Code](https://code.visualstudio.com) (VS Code) as our IDE for this course and [LiteLLM as our model gateway](https://www.litellm.ai).

Which of the course's models can build a working program from one spec, and what does it take to fix the ones that can't? That's the project. The spec is an arcade game in a single HTML file, so you judge every answer the same way: open it in a browser and play.

Everyone starts with the same spec: Breakout doubles. It's Breakout with a twist no model has seen before: your paddle on the left half, a computer teammate's paddle on the right half that chases the ball on its own but only so fast, so it can miss. You write the prompt once, send it to each model, save each reply as a game file, and play it. Some will work first try. Most of the failures will be quiet: a teammate that never moves, or one that cheats. You fix one by changing the ask, not the code. Then, if you want to make it awesome, write a spec of your own: a blend of two arcade games.

## Instructions

1. Open the P02-starter folder in VS Code and open the chat panel. Its artifacts folder is where the games go, and its logs folder keeps your chat log. Refer to the [prereq instructions](Setup.md).  
2. Write your prompt in PROMPT.md. It already holds the Breakout doubles prompt. Fill in its Theme section: the colours, the teammate's name, and the words on the end screens. Keep the teammate's 3-pixel speed cap and the centre line; that is where the game breaks. If you are stuck, talk to a model on LiteLLM\!  
3. Once PROMPT.md is finished, send it to each of the three course models from the model selection menu below the prompt box: external/haiku-4-5-20251001, external/GLM5, and external/deepseek.v3.2. They are three different companies' models, all served through Bedrock, and they don't behave the same. Sometimes, VS Code will suggest a file to attach to the prompt. Since we're evaluating every model against the same prompt, make sure that no other file is being fed into the model. Once a model is finished, start a new chat and switch to the next model under CSE 490\. Save each created game in the artifacts folder as \<Game\>\_\<model\>.html: the game name, one underscore, the model's short name, for example artifacts/BreakoutDoubles\_kimi-k3.html.  
4. With every model response, start its block in SCORECARD.md: the model and the game file. The course gateway records your prompts, timing, and turns on its own.  
5. Now spend about 1 minute playing each created game, watching the right half. They can be played by opening the file in your browser. Continue filling out SCORECARD.md, documenting whether the game is playable, likes, dislikes, and what surprised you. At least one of the three usually gets it first try, and at least one usually doesn't.  
6. However, there may be a model that fails. In this case, use the same model that failed and continue prompting until you're satisfied with its output. Change the ask, not the code.

## Make it awesome

This part is optional and worth 5 extra points. Write a spec of your own that blends two arcade games: Pong played on Frogger's road, Galaga with Mappy's trampolines, whatever you can picture. Put it in PROMPT2.md, in the shape of the Breakout doubles prompt: a theme, the rules, the technical constraints, the expected behaviour, and the output format. Then repeat steps 3 to 6 with it: the same three models, a game file per model named after your game, a SCORECARD.md block for each with Prompt file set to PROMPT2.md.

Some examples of arcade games:

* [Pong](https://en.wikipedia.org/wiki/Pong)  
* [Frogger](https://en.wikipedia.org/wiki/Frogger)  
* [Mappy](https://en.wikipedia.org/wiki/Mappy)  
* [Galaga](https://en.wikipedia.org/wiki/Galaga)

## Turnin

By Tuesday 11:59 pm, on the Project 2 assignment in Canvas:

* In VS Code, open the Command Palette and run CSE 490: Package for turn-in. It checks your folder and writes P02-submission.zip next to PROMPT.md.  
* Upload P02-submission.zip. It holds your prompts, the scorecard, every game, and your chat log; .env is left out.  
* If you made it awesome, PROMPT2.md and its games are in the zip already.  
* Submit as Upload: the one zip.

## Grading

Your submission is autograded. It checks that each step was properly followed: the Breakout doubles prompt in PROMPT.md, one game file per model, and a SCORECARD.md block for each of the three course models. If you made it awesome, it checks the same for PROMPT2.md and its games, worth 5 extra points on top of the 100\. Every check is pass or fail. It does not judge code style, prompt wording, how good the game is, or how many tries it took.

## Reference

The Breakout doubles prompt is PROMPT.md in the starter files. It has five sections: Theme, Rules, Technical constraints, Expected behaviour, and Output format. You fill in Theme and leave the rest as written.  
