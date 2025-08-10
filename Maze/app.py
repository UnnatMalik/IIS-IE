# Save as app.py and run with: streamlit run app.py

import streamlit as st
from PIL import Image
import numpy as np
import cv2
import heapq

# --- A* Pathfinding Helper Functions ---
def heuristic(a, b):
    """Calculate Manhattan distance between two points"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(maze, start, end):
    """A* pathfinding algorithm"""
    if maze[start[0]][start[1]] == 0 or maze[end[0]][end[1]] == 0:
        return None  # Start or end is a wall
    
    rows, cols = maze.shape
    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, end)}
    oheap = []
    
    heapq.heappush(oheap, (fscore[start], start))
    
    while oheap:
        current = heapq.heappop(oheap)[1]
        
        if current == end:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
        
        close_set.add(current)
        
        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            
            # Check bounds
            if not (0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols):
                continue
            
            # Check if neighbor is a wall
            if maze[neighbor[0]][neighbor[1]] == 0:
                continue
            
            # Check if already evaluated
            if neighbor in close_set:
                continue
            
            tentative_g_score = gscore[current] + 1
            
            if neighbor not in gscore or tentative_g_score < gscore[neighbor]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, end)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))
    
    return None

def find_nearest_path(maze, point, max_search=50):
    """Find the nearest path pixel to a given point"""
    x, y = point
    rows, cols = maze.shape
    
    # Start from the point and expand outward
    for r in range(max_search):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    if maze[nx][ny] == 1:  # 1 = path
                        return (nx, ny)
    return None

def convert_image_to_maze(image, target_size=(100, 100)):
    """Convert image to binary maze grid"""
    # Convert to grayscale and resize
    image = image.convert("L")
    image = image.resize(target_size)
    img_np = np.array(image)
    
    # Threshold to create binary image
    _, binary = cv2.threshold(img_np, 128, 255, cv2.THRESH_BINARY)
    
    # Convert to maze grid: 0 = wall, 1 = path
    maze = (binary == 255).astype(int)
    return maze

def draw_path_on_maze(maze, path):
    """Draw the path on the maze as a continuous line and return the image"""
    if path is None:
        return maze
    
    # Create a copy of the maze for visualization
    maze_with_path = maze.copy().astype(np.uint8) * 255
    
    # Draw path as a continuous line
    if len(path) > 1:
        # Convert path to numpy array for easier manipulation
        path_array = np.array(path)
        
        # Draw line segments between consecutive points
        for i in range(len(path) - 1):
            start_point = path_array[i]
            end_point = path_array[i + 1]
            
            # Use OpenCV line drawing for smooth lines
            # For grayscale images, use a dark color value (0 = black, 255 = white)
            cv2.line(maze_with_path, 
                     (start_point[1], start_point[0]),  # OpenCV uses (x, y) format
                     (end_point[1], end_point[0]), 
                     color=0,  # Black color for maximum visibility
                     thickness=2)  # Line thickness
    
    return maze_with_path

def draw_path_points(maze, path):
    """Draw the path on the maze as individual points and return the image"""
    if path is None:
        return maze
    
    # Create a copy of the maze for visualization
    maze_with_path = maze.copy().astype(np.uint8) * 255
    
    # Draw each path point
    for point in path:
        # Draw a small circle at each point
        cv2.circle(maze_with_path, 
                   (point[1], point[0]),  # OpenCV uses (x, y) format
                   radius=2,  # Larger radius for better visibility
                   color=0,  # Black color for maximum visibility
                   thickness=-1)  # Filled circle
    
    return maze_with_path

# --- Streamlit App ---
st.title("🧠 A* Maze Solver")
st.markdown("Upload a black and white maze image to find the shortest path from top-left to bottom-right.")

uploaded_file = st.file_uploader("Upload a maze image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    try:
        # Load and process image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Maze", use_container_width=True)
        
        # Convert to maze grid
        maze = convert_image_to_maze(image)
        
        # Display maze grid info
        st.write(f"Maze size: {maze.shape[0]} x {maze.shape[1]}")
        
        # Set start and end points
        start = (0, 0)
        end = (maze.shape[0] - 1, maze.shape[1] - 1)
        
        # Find nearest path pixels for start and end
        start = find_nearest_path(maze, start)
        end = find_nearest_path(maze, end)
        
        if start is None or end is None:
            st.error("❌ Could not find valid start/end points in the maze.")
        else:
            st.write(f"Start: {start}, End: {end}")
            
            # Solve maze
            with st.spinner("Solving maze using A* algorithm..."):
                path = astar(maze, start, end)
            
            if path is None:
                st.error("❌ No path found in the maze.")
            else:
                st.success(f"✅ Path found! Length: {len(path)}")
                
                # Debug information
                st.write(f"Path starts at: {path[0]}, ends at: {path[-1]}")
                st.write(f"Number of path points: {len(path)}")
                
                # Visualization choice
                viz_choice = st.radio(
                    "Choose visualization style:",
                    ["Line Path", "Point Path", "Both"],
                    horizontal=True
                )
                
                # Draw path based on choice
                if viz_choice == "Line Path":
                    maze_with_path = draw_path_on_maze(maze, path)
                    st.image(maze_with_path, caption="Maze with line path", use_container_width=True)
                    
                    # Debug: Show original maze for comparison
                    st.write("Debug: Original maze (white = path, black = wall):")
                    st.image(maze * 255, caption="Original maze grid", use_container_width=True)
                    
                elif viz_choice == "Point Path":
                    maze_with_path = draw_path_points(maze, path)
                    st.image(maze_with_path, caption="Maze with point path", use_container_width=True)
                else:  # Both
                    col1, col2 = st.columns(2)
                    with col1:
                        maze_line = draw_path_on_maze(maze, path)
                        st.image(maze_line, caption="Line Path", use_container_width=True)
                    with col2:
                        maze_points = draw_path_points(maze, path)
                        st.image(maze_points, caption="Point Path", use_container_width=True)
                
                # Show path coordinates
                with st.expander("View path coordinates"):
                    st.write("Path coordinates (row, col):")
                    for i, point in enumerate(path):
                        st.write(f"{i+1}: {point}")
                        
    except Exception as e:
        st.error(f"❌ Error processing image: {str(e)}")
        st.write("Please make sure you've uploaded a valid image file.")

# Add some helpful information
with st.sidebar:
    st.header("How to use:")
    st.markdown("""
    1. **Upload a maze image** - Should be black and white
    2. **Black pixels** = Walls
    3. **White pixels** = Paths
    4. **Algorithm** will find shortest path from top-left to bottom-right
    5. **Choose visualization**: Line path (smooth) or Point path (detailed)
    """)
    
    st.header("Visualization Options:")
    st.markdown("""
    - **Line Path**: Smooth continuous line showing the route
    - **Point Path**: Individual points showing each step
    - **Both**: Side-by-side comparison
    """)
    
    st.header("Tips:")
    st.markdown("""
    - Use clear, high-contrast images
    - Ensure walls are completely black
    - Ensure paths are completely white
    - Maze should have a clear start and end
    - Line visualization is best for understanding the route
    - Point visualization shows exact path details
    """)
