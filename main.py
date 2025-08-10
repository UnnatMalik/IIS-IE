import streamlit as st
import cv2
import numpy as np
import heapq
from PIL import Image
import matplotlib.pyplot as plt

# --- A* Algorithm ---
def manhattan_dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(maze, start, end):
    rows, cols = len(maze), len(maze[0])
    open_set = [(0 + manhattan_dist(start, end), 0, start)]
    came_from = {}
    g_score = {start: 0}
    visited = set()

    while open_set:
        _, curr_cost, current = heapq.heappop(open_set)

        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        visited.add(current)

        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols:
                if maze[neighbor[0]][neighbor[1]] == 1 and neighbor not in visited:
                    tentative_g = curr_cost + 1
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        g_score[neighbor] = tentative_g
                        f_score = tentative_g + manhattan_dist(neighbor, end)
                        heapq.heappush(open_set, (f_score, tentative_g, neighbor))
                        came_from[neighbor] = current
    return None

# --- Convert Maze Image to Grid ---
def convert_image_to_maze(image):
    image = image.convert("L")  # grayscale
    image = image.resize((100, 100))  # resize for consistency
    img_np = np.array(image)
    _, binary = cv2.threshold(img_np, 128, 255, cv2.THRESH_BINARY_INV)
    maze = (binary == 255).astype(int)
    return maze

# --- Show maze with path ---
def draw_path_on_maze(maze, path):
    maze_copy = np.copy(maze).astype(np.float32)
    for r, c in path:
        maze_copy[r][c] = 0.5  # path in gray

    fig, ax = plt.subplots(figsize=(6,6))
    ax.imshow(maze_copy, cmap='gray')
    ax.axis('off')
    return fig

# --- Streamlit UI ---
st.title("🧠 A* Maze Solver")

uploaded_file = st.file_uploader("Upload a maze image (black & white)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Maze", use_column_width=True)

    maze_grid = convert_image_to_maze(image)
    start = (1, 1)
    end = (98, 98)

    with st.spinner("Solving maze using A*..."):
        path = a_star(maze_grid, start, end)

    if path:
        st.success(f"✅ Path found! Length: {len(path)}")
        fig = draw_path_on_maze(maze_grid, path)
        st.pyplot(fig)
    else:
        st.error("❌ No path found in the maze.")
