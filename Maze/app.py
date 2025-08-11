# app.py
import streamlit as st
import random
import heapq
import time
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# --- basic setup ---
st.set_page_config(page_title="A* Maze (11x11)", page_icon="🧭", layout="centered")

N = 11
start = (0, 0)
goal = (N - 1, N - 1)

def make_grid(n, wall_p=0.25):
    g = [[1 if random.random() < wall_p else 0 for _ in range(n)] for _ in range(n)]
    g[start[0]][start[1]] = 0
    g[goal[0]][goal[1]] = 0
    return g

def h(a, b):
    # Manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def neighbors(r, c, n):
    for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < n and 0 <= nc < n:
            yield nr, nc

def draw_grid(grid, path=set(), open_set=set(), closed_set=set(), current=None, placeholder=None):
    n = len(grid)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_aspect("equal")
    ax.axis("off")

    for r in range(n):
        for c in range(n):
            # base color
            if grid[r][c] == 1:
                color = "#111827"  # wall
            else:
                color = "#e5e7eb"  # empty

            cell = (r, c)
            if cell in closed_set:
                color = "#fb923c"  # closed (orange)
            if cell in open_set:
                color = "#38bdf8"  # open (sky)
            if cell in path:
                color = "#22c55e"  # path (green)
            if cell == current:
                color = "#f59e0b"  # current (amber)
            if cell == start:
                color = "#a78bfa"  # start (violet)
            if cell == goal:
                color = "#ef4444"  # goal (red)

            ax.add_patch(Rectangle((c, n - r - 1), 1, 1, facecolor=color, edgecolor="#9ca3af", linewidth=0.75))

    # grid lines (subtle)
    for i in range(n + 1):
        ax.plot([0, n], [i, i], color="#d1d5db", linewidth=0.3)
        ax.plot([i, i], [0, n], color="#d1d5db", linewidth=0.3)

    if placeholder:
        placeholder.pyplot(fig, clear_figure=True)
    else:
        st.pyplot(fig, clear_figure=True)
    plt.close(fig)

def reconstruct(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

def astar_with_visuals(grid, start, goal, delay_ms=80, placeholder=None):
    n = len(grid)
    open_heap = []
    heapq.heappush(open_heap, (h(start, goal), 0, start))
    came_from = {}
    g_score = {start: 0}
    open_set = {start}
    closed_set = set()

    while open_heap:
        _, g, current = heapq.heappop(open_heap)
        if current not in open_set:
            continue
        open_set.remove(current)

        if current == goal:
            path = set(reconstruct(came_from, current))
            draw_grid(grid, path=path, open_set=open_set, closed_set=closed_set, current=current, placeholder=placeholder)
            return list(path)

        closed_set.add(current)

        # draw each step
        draw_grid(grid, path=set(), open_set=open_set, closed_set=closed_set, current=current, placeholder=placeholder)
        time.sleep(max(0, delay_ms) / 1000.0)

        r, c = current
        for nr, nc in neighbors(r, c, n):
            if grid[nr][nc] == 1:
                continue
            nxt = (nr, nc)
            if nxt in closed_set:
                continue
            tentative_g = g + 1
            if tentative_g < g_score.get(nxt, float("inf")):
                came_from[nxt] = current
                g_score[nxt] = tentative_g
                f = tentative_g + h(nxt, goal)
                heapq.heappush(open_heap, (f, tentative_g, nxt))
                open_set.add(nxt)

    # no path
    draw_grid(grid, placeholder=placeholder)
    return None

# --- UI ---
st.title("A* Pathfinding on a Random 11×11 Maze")
col1, col2, col3 = st.columns(3)
with col1:
    wall_p = st.slider("Wall density", 0.0, 0.45, 0.25, 0.01)
with col2:
    delay_ms = st.slider("Step delay (ms)", 0, 300, 80, 10)
with col3:
    seed_val = st.number_input("Seed (optional)", value=0, step=1)

btns = st.columns(2)
new_maze = btns[0].button("New maze")
run = btns[1].button("Run A*")

if new_maze and seed_val:
    random.seed(int(seed_val))

if "grid" not in st.session_state or new_maze:
    st.session_state.grid = make_grid(N, wall_p)

placeholder = st.empty()
draw_grid(st.session_state.grid, placeholder=placeholder)

if run:
    path = astar_with_visuals(st.session_state.grid, start, goal, delay_ms=delay_ms, placeholder=placeholder)
    if path is None:
        st.warning("No path found. Try a lower wall density or generate a new maze.")
    else:
        st.success(f"Path length: {len(path)}")

# Tip text
st.caption("Start: top-left. Goal: bottom-right. A* uses Manhattan distance.")
