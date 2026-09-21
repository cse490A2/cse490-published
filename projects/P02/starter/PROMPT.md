Write a Breakout doubles game I can play in my browser with a computer teammate.

## Theme

Use this theme. Where it gives end-screen words, show them in place of GAME OVER and YOU WIN.

Colours: 
Teammate's name: 
Words on the win screen: 
Words on the lose screen: 

## Constraints

One complete HTML file with the CSS and JavaScript inline. No external libraries, fonts, images, or network requests. A 480 by 320 canvas. Two paddles side by side along the bottom: mine on the left half, moved with the left and right arrow keys and never crossing the centre line; the computer's on the right half, which moves toward the ball on its own by at most 3 pixels per frame and never crosses the centre line either. One ball. Six rows of ten bricks. The ball bounces off the walls, both paddles, and the bricks, and a brick disappears when it is hit. The score is shared and drawn on the canvas. When the ball falls below the paddles the game shows GAME OVER; when every brick is gone it shows YOU WIN; pressing Space restarts. Use requestAnimationFrame for the game loop. No alert or prompt dialogs. Keep it under 150 lines.

## Examples

The ball starts resting on my paddle and launches upward when Space is pressed. When the ball comes down on the right half, the computer paddle slides under it; if the ball is moving sideways faster than the paddle can, the computer misses and the ball is lost.

## Output format

Reply with the HTML file in one code block and nothing else.
