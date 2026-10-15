"""A window that replays a move list, the way the judge scores it.

  python3 view.py graph.json moves.json
  python3 view.py graph.json --planar      staff: the hidden drawing, one move per node

Buttons: Play / Pause, Step (one turn), Restart. Keys: space, n, r, q.
Edges are tinted by how many crossings they carry; each crossing is an x;
a moved node keeps a ghost at its start; the strip plots crossings against
turns, which is the score.
"""
import json
import sys
import tkinter as tk

from check import crossing_pairs, node_hits

SIZE, PAD, R, STRIP = 720, 36, 6, 120
BG, EDGE, GHOST, NODE, MOVED, FLY, MARK, TEXT = "#0f1117", "#3a3f4b", "#2a2f3a", "#e6e6e6", "#4aa3ff", "#5df0a0", "#ff4d4d", "#c8ccd4"


def tint(k):
    if k == 0:
        return EDGE
    t = min(1.0, k / 6.0)
    return "#%02x%02x%02x" % (255, int(170 * (1 - t) + 60 * t), int(40 * (1 - t) + 60 * t))


def meet(p1, p2, q1, q2):
    d = (p2[0] - p1[0]) * (q2[1] - q1[1]) - (p2[1] - p1[1]) * (q2[0] - q1[0])
    if d == 0:
        return None
    t = ((q1[0] - p1[0]) * (q2[1] - q1[1]) - (q1[1] - p1[1]) * (q2[0] - q1[0])) / d
    return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))


def ease(t):
    return 1 - (1 - t) ** 3


class Viewer:
    def __init__(self, graph, moves):
        self.g = graph
        self.edges = [tuple(e) for e in graph["edges"]]
        self.lo, self.hi = graph["canvas"]
        self.start = [tuple(p) for p in graph["nodes"]]
        self.moves = moves
        self.root = tk.Tk()
        self.root.title("Untangle: seed %d, %d nodes, %d edges, %d turns in the move list"
                        % (graph["seed"], graph["n"], len(self.edges), len(moves)))
        self.root.configure(bg=BG)
        self.cv = tk.Canvas(self.root, width=SIZE, height=SIZE + STRIP, bg=BG, highlightthickness=0)
        self.cv.pack()
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=PAD, pady=(0, 12))
        self.play_btn = tk.Button(bar, text="Play", width=8, command=self.toggle)
        self.play_btn.pack(side="left", padx=(0, 8))
        tk.Button(bar, text="Step", width=8, command=self.step_once).pack(side="left", padx=(0, 8))
        tk.Button(bar, text="Restart", width=8, command=self.restart).pack(side="left")
        tk.Label(bar, text="space play/pause   n step   r restart   q quit", bg=BG, fg=EDGE, font=("Menlo", 11)).pack(side="right")
        self.root.bind("<space>", lambda e: self.toggle())
        self.root.bind("n", lambda e: self.step_once())
        self.root.bind("r", lambda e: self.restart())
        self.root.bind("q", lambda e: self.root.destroy())
        self.restart()
        self.tick()

    # ---- state
    def restart(self):
        self.pos = list(self.start)
        self.i = 0
        self.playing = False
        self.busy = False
        self.flying = None
        self.rings = []
        self.history = []
        self.moved = set()
        self.play_btn.config(text="Play")
        self.draw()

    def toggle(self):
        if self.i >= len(self.moves):
            return
        self.playing = not self.playing
        self.play_btn.config(text="Pause" if self.playing else "Play")

    def step_once(self):
        if not self.busy and self.i < len(self.moves):
            self.playing = False
            self.play_btn.config(text="Play")
            self.animate_move()

    def tick(self):
        if self.playing and not self.busy and self.i < len(self.moves):
            self.animate_move()
        elif self.rings:
            self.draw()
        self.root.after(90, self.tick)

    def animate_move(self):
        self.busy = True
        v, x1, y1 = self.moves[self.i]
        x0, y0 = self.pos[v]
        self.flying = v
        frames = 12
        for k in range(1, frames + 1):
            t = ease(k / frames)
            self.pos[v] = (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)
            self.draw()
            self.root.update()
            self.root.after(14)
        self.pos[v] = (x1, y1)
        self.moved.add(v)
        self.flying = None
        self.rings.append([v, 0])
        self.i += 1
        self.busy = False
        if self.i >= len(self.moves):
            self.playing = False
            self.play_btn.config(text="Play")
        self.draw()

    # ---- drawing
    def px(self, p):
        s = (SIZE - 2 * PAD) / (self.hi - self.lo)
        return PAD + (p[0] - self.lo) * s, PAD + (self.hi - p[1]) * s

    def draw(self):
        cv, pos, edges = self.cv, self.pos, self.edges
        cv.delete("all")
        pairs = crossing_pairs(pos, edges)
        hits = node_hits(pos, edges) if self.flying is None else []
        load = [0] * len(edges)
        for i, j in pairs:
            load[i] += 1; load[j] += 1
        for v in self.moved:
            x0, y0 = self.px(self.start[v]); x1, y1 = self.px(pos[v])
            cv.create_line(x0, y0, x1, y1, fill=GHOST, dash=(2, 4))
            cv.create_oval(x0 - 3, y0 - 3, x0 + 3, y0 + 3, outline=GHOST, fill="")
        for k in sorted(range(len(edges)), key=lambda k: load[k]):
            a, b = edges[k]
            cv.create_line(*self.px(pos[a]), *self.px(pos[b]), fill=tint(load[k]), width=1 if load[k] == 0 else 2)
        for i, j in pairs:
            a, b = edges[i]; c, d = edges[j]
            m = meet(pos[a], pos[b], pos[c], pos[d])
            if m:
                x, y = self.px(m)
                cv.create_line(x - 3, y - 3, x + 3, y + 3, fill=MARK, width=2)
                cv.create_line(x - 3, y + 3, x + 3, y - 3, fill=MARK, width=2)
        keep = []
        for ring in self.rings:
            v, age = ring
            x, y = self.px(pos[v])
            rr = R + 4 + age * 3
            cv.create_oval(x - rr, y - rr, x + rr, y + rr, outline=FLY, width=max(1, 3 - age // 3))
            if age < 8:
                ring[1] += 1
                keep.append(ring)
        self.rings = keep
        for v, p in enumerate(pos):
            x, y = self.px(p)
            fill = FLY if v == self.flying else (MOVED if v in self.moved else NODE)
            cv.create_oval(x - R - 2, y - R - 2, x + R + 2, y + R + 2, fill=BG, outline="")
            cv.create_oval(x - R, y - R, x + R, y + R, fill=fill, outline="")
        # the strip: crossings against turns
        c = len(pairs) + len(hits)
        if self.flying is None and (not self.history or self.history[-1][0] != self.i):
            self.history.append((self.i, c))
        top = SIZE + 8
        base = top + STRIP - 48
        cv.create_line(PAD, base, SIZE - PAD, base, fill=EDGE)
        c0 = max(1, self.history[0][1]) if self.history else 1
        total = max(1, len(self.moves))
        pts = []
        for turn, k in self.history:
            pts += [PAD + (SIZE - 2 * PAD) * turn / total, base - (STRIP - 60) * k / c0]
        if len(pts) >= 4:
            cv.create_line(*pts, fill=MOVED, width=2)
        if pts:
            cv.create_oval(pts[-2] - 3, pts[-1] - 3, pts[-2] + 3, pts[-1] + 3, fill=FLY, outline="")
        done = self.i >= len(self.moves)
        status = ("score %d turns" % self.i if c == 0 else "did not finish") if done else ("playing" if self.playing else "")
        cv.create_text(PAD, base + 22, anchor="w", fill=TEXT, font=("Menlo", 13),
                       text="crossings %d    turn %d of %d    %s" % (c, self.i, len(self.moves), status))
        cv.create_text(SIZE - PAD, base + 22, anchor="e", fill=EDGE, font=("Menlo", 11), text="crossings vs turns")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    g = json.load(open(sys.argv[1]))
    if sys.argv[2] == "--planar":
        import graph
        moves = [[v, x, y] for v, (x, y) in enumerate(graph.planar_layout(g["seed"], g["n"]))]
    else:
        moves = json.load(open(sys.argv[2]))["moves"]
    Viewer(g, moves).root.mainloop()


if __name__ == "__main__":
    main()
