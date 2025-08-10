# Save as app.py and run with: streamlit run app.py

import streamlit as st
from PIL import Image
import numpy as np
import cv2
import heapq

# --- A* Pathfinding Helper Functions ---
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(array, start, end):
    neighbors = [(0,1),(0,-1),(1,0),(-1,0)]
    close_set = set()
    came_from = {}
    gscore = {start:0}
    fscore = {start:heuristic(start, end)}
    oheap = []

    heapq.heappush(oheap, (fscore[start], start))

    while oheap:
        current = heapq.heappop(oheap)[1]

        if current == end:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data[::-1]

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0]+i, current[1]+j            
            tentative_g_score = gscore[current] + 1
            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:                
                    if array[neighbor[0]][neighbor[1]] == 0:
                        continue
                else:
                    continue
            else:
                continue

            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue
            
            if  tentative_g_score < gscore.get(neighbor, float('inf')) or neighbor not in [i[1] for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, end)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))
    
    return False

# --- Streamlit App ---
st.title("🧠 A* Maze Solver")
uploaded_file = st.file_uploader("Upload a maze image (black & white)")

if uploaded_file:
    image = Image.open(uploaded_file).convert("L")  # Grayscale
    image_np = np.array(image)
    
    # Threshold to make binary maze
    _, binary = cv2.threshold(image_np, 200, 255, cv2.THRESH_BINARY)
    binary = binary // 255  # 0 = wall, 1 = path

    st.image(image, caption="Uploaded Maze", use_column_width=True)

    start = (0, 0)
    end = (binary.shape[0] - 1, binary.shape[1] - 1)

    # Move start and end to nearest white pixel
    def find_nearest_white(binary, point):
        x, y = point
        for r in range(1, 50):
            for dx in range(-r, r+1):
                for dy in range(-r, r+1):
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < binary.shape[0] and 0 <= ny < binary.shape[1]:
                        if binary[nx][ny] == 1:
                            return (nx, ny)
        return None

    start = find_nearest_white(binary, start)
    end = find_nearest_white(binary, end)

    if start is None or end is None:
        st.error("No start/end point found in white area.")
    else:
        path = astar(binary, start, end)

        if not path:
            st.error("❌ No path found in the maze.")
        else:
            # Draw path on image
            for point in path:
                image_np[point[0]][point[1]] = 128  # Gray path

            st.image(image_np, caption="✅ Path Found", clamp=True, use_column_width=True)
