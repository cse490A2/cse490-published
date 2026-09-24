Write a Breakout doubles game I can play in my browser with a computer teammate.

## Theme
Colours:
Teammate's name:
Win screen words:
Lose screen words:
Use the colours for the page, paddles, bricks and text. Draw the teammate's
name under its paddle. Show the win and lose words on the end screens; if a
field is empty use YOU WIN and GAME OVER.

## Rules
- A 480 by 320 canvas, centred on the page.
- Two paddles side by side along the bottom, each 70 pixels wide. Mine is on
  the left half, moves smoothly with the left and right arrow keys while they
  are held, and never crosses the centre line. The computer's is on the right
  half; each frame it moves toward the ball's horizontal position by at most
  3 pixels and never crosses the centre line.
- One ball. It starts resting on my paddle and launches upward when Space is
  pressed.
- The ball moves at a constant speed of 4 pixels per frame. Where it hits a
  paddle sets its direction: the centre sends it straight up, the edges send
  it out at up to 60 degrees from vertical.
- Six rows of ten bricks. The ball bounces off the walls, both paddles and
  the bricks. A brick disappears when hit, at most one brick per frame.
- The score is shared, 10 points per brick, drawn on the canvas.
- When the ball falls below the paddles show the lose screen. When every
  brick is gone show the win screen. On either screen, Space starts a fresh
  game with all bricks back and the score at zero.

## Technical constraints
- One complete HTML file with the CSS and JavaScript inline. No external
  libraries, fonts, images or network requests.
- Use requestAnimationFrame for the game loop. Speeds are per frame; assume
  60 frames per second, no delta timing.
- No alert, prompt or confirm dialogs.
- Key listeners on the document. Arrow keys and Space must not scroll the
  page.
- At most 150 lines, no line longer than 120 characters.

## Expected behaviour (each will be checked)
1. The ball rests on my paddle and moves with it until Space; then it
   launches upward.
2. When the ball comes down on the right half, the computer paddle slides
   under it. If the ball moves sideways faster than 3 pixels per frame, the
   computer misses and the ball is lost.
3. Hitting the ball with the edge of my paddle sends it out at an angle;
   hitting it with the centre sends it straight up.
4. Holding an arrow key moves my paddle smoothly, with no pause after the
   first press.
5. After the win or lose screen, Space restarts with all bricks back and the
   score at zero.

## Output format
Reply with the HTML file in one ```html code block and nothing else.
