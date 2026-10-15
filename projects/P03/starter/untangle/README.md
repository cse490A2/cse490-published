# Untangle

graph.json is a planar graph drawn with every node in the wrong place: 30
nodes on a 1000 by 1000 grid, 76 edges, hundreds of crossings. A drawing
with no crossing exists. Find one by moving nodes, and use as few moves as
you can.

Rules:
- A move is one node to one integer point inside the canvas, any distance.
- Every move costs one turn, a move back to the start included.
- At the end no two nodes may share a point, and an edge passing through a
  node counts as a crossing.
- The score is the number of turns when the crossings reach zero. Lower wins.
  One move per node is the reference.

Write solve.py. It reads graph.json and writes moves.json:

    {"moves": [[node, x, y], [node, x, y], ...]}

Then:

    python3 check.py graph.json moves.json     the judge: crossings and turns
    python3 view.py  graph.json moves.json     watch it: Play, Step, Restart

The judge is the only scorer. Your solver is graded on graphs you have not
seen, of the same size, with a time limit; a run that does not reach zero
crossings ranks below every run that does.

view.py needs Tk 8.6 or newer: python.org and Homebrew Pythons have it;
Apple's /usr/bin/python3 ships Tk 8.5 and draws a blank window.
