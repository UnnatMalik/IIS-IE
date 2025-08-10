# Save as app.py and run with: streamlit run app.py

import streamlit as st
from PIL import Image
import numpy as np
import cv2
import heapq
import json
import base64
from io import BytesIO

# --- A* Pathfinding Algorithm ---
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
    """Find the nearest path pixel to a given point using BFS"""
    x, y = point
    rows, cols = maze.shape
    
    # Check if the point is already valid
    if 0 <= x < rows and 0 <= y < cols and maze[x][y] == 1:
        return (x, y)
    
    # Use BFS to find nearest valid path
    from collections import deque
    queue = deque([(x, y, 0)])  # (row, col, distance)
    visited = set([(x, y)])
    
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    
    while queue:
        cx, cy, dist = queue.popleft()
        
        if dist > max_search:
            break
            
        # Check if current position is a valid path
        if 0 <= cx < rows and 0 <= cy < cols and maze[cx][cy] == 1:
            return (cx, cy)
        
        # Add neighbors to queue
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if (nx, ny) not in visited and 0 <= nx < rows and 0 <= ny < cols:
                visited.add((nx, ny))
                queue.append((nx, ny, dist + 1))
    
    return None

def convert_image_to_maze(image, target_size=(100, 100)):
    """Convert image to binary maze grid with improved processing"""
    # Convert to grayscale and resize
    image = image.convert("L")
    image = image.resize(target_size, Image.Resampling.LANCZOS)
    img_np = np.array(image)
    
    # Apply Gaussian blur to reduce noise
    img_np = cv2.GaussianBlur(img_np, (3, 3), 0)
    
    # Use adaptive threshold for better results
    binary = cv2.adaptiveThreshold(img_np, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Convert to maze grid: 1 = path (white), 0 = wall (black)
    maze = (binary > 127).astype(int)
    
    # Clean up small noise
    kernel = np.ones((2, 2), np.uint8)
    maze = cv2.morphologyEx(maze.astype(np.uint8), cv2.MORPH_CLOSE, kernel).astype(int)
    
    return maze

def create_maze_html(maze, path=None, cell_size=6):
    """Create HTML representation of the maze with proper path visualization"""
    rows, cols = maze.shape
    
    # Create CSS for the maze
    css = f"""
    <style>
    .maze-container {{
        display: inline-block;
        background: #f0f0f0;
        border: 2px solid #333;
        padding: 5px;
        margin: 10px auto;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}
    .maze-grid {{
        display: grid;
        grid-template-columns: repeat({cols}, {cell_size}px);
        grid-template-rows: repeat({rows}, {cell_size}px);
        gap: 0;
        background: transparent;
    }}
    .maze-cell {{
        width: {cell_size}px;
        height: {cell_size}px;
        border: none;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        position: relative;
    }}
    .wall {{
        background-color: #000000;
    }}
    .path {{
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
    }}
    .solution-path {{
        background-color: #ff0000 !important;
        border: 1px solid #cc0000 !important;
        box-shadow: 0 0 2px rgba(255,0,0,0.6);
        z-index: 10;
    }}
    .start-point {{
        background-color: #00ff00 !important;
        border: 2px solid #00cc00 !important;
        box-shadow: 0 0 4px rgba(0,255,0,0.8);
        z-index: 15;
    }}
    .end-point {{
        background-color: #0000ff !important;
        border: 2px solid #0000cc !important;
        box-shadow: 0 0 4px rgba(0,0,255,0.8);
        z-index: 15;
    }}
    .maze-info {{
        margin: 15px 0;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
    .legend {{
        display: flex;
        justify-content: center;
        gap: 20px;
        margin: 10px 0;
        flex-wrap: wrap;
    }}
    .legend-item {{
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 5px 10px;
        background: white;
        border-radius: 5px;
        border: 1px solid #ddd;
        font-size: 14px;
    }}
    .legend-color {{
        width: 16px;
        height: 16px;
        border: 1px solid #333;
        border-radius: 2px;
    }}
    .path-stats {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 10px;
        margin: 10px 0;
    }}
    .stat-box {{
        text-align: center;
        padding: 12px;
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        border-radius: 6px;
        border: 1px solid #90caf9;
    }}
    .stat-box strong {{
        color: #1565c0;
        display: block;
        margin-bottom: 5px;
        font-size: 14px;
    }}
    .stat-box span {{
        color: #333;
        font-size: 12px;
    }}
    </style>
    """
    
    # Create HTML for the maze
    html = f"""
    {css}
    <div class="maze-container">
        <div class="maze-grid">
    """
    
    # Convert path to set for O(1) lookup
    path_set = set(path) if path else set()
    path_cells_rendered = 0
    
    # Generate maze cells
    for i in range(rows):
        for j in range(cols):
            cell_classes = ["maze-cell"]
            
            if maze[i][j] == 0:
                cell_classes.append("wall")
            else:
                cell_classes.append("path")
                
                # Check if this cell is part of the solution path
                if path and (i, j) in path_set:
                    # Special styling for start and end points
                    if path and (i, j) == path[0]:
                        cell_classes.append("start-point")
                    elif path and (i, j) == path[-1]:
                        cell_classes.append("end-point")
                    else:
                        cell_classes.append("solution-path")
                    path_cells_rendered += 1
            
            html += f'<div class="{" ".join(cell_classes)}" title="({i}, {j})"></div>'
    
    html += """
        </div>
    </div>
    """
    
    # Add legend and statistics
    html += f"""
    <div class="maze-info">
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #000000;"></div>
                <span>Wall</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #ffffff; border: 2px solid #e0e0e0;"></div>
                <span>Path</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #ff0000;"></div>
                <span>Solution</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #00ff00;"></div>
                <span>Start</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #0000ff;"></div>
                <span>End</span>
            </div>
        </div>
    """
    
    # Add path statistics if path exists
    if path:
        efficiency = round((abs(path[-1][0] - path[0][0]) + abs(path[-1][1] - path[0][1])) / len(path) * 100, 1)
        html += f"""
        <div class="path-stats">
            <div class="stat-box">
                <strong>Path Length</strong>
                <span>{len(path)} steps</span>
            </div>
            <div class="stat-box">
                <strong>Start Point</strong>
                <span>({path[0][0]}, {path[0][1]})</span>
            </div>
            <div class="stat-box">
                <strong>End Point</strong>
                <span>({path[-1][0]}, {path[-1][1]})</span>
            </div>
            <div class="stat-box">
                <strong>Path Efficiency</strong>
                <span>{efficiency}%</span>
            </div>
            <div class="stat-box">
                <strong>Cells Rendered</strong>
                <span>{path_cells_rendered} / {len(path)}</span>
            </div>
        </div>
        """
    
    html += "</div>"
    return html

def create_test_maze():
    """Create a test maze for debugging"""
    maze = np.ones((15, 15), dtype=int)
    
    # Create walls to form a simple maze
    # Outer walls
    maze[0, :] = 0  # Top wall
    maze[-1, :] = 0  # Bottom wall
    maze[:, 0] = 0  # Left wall
    maze[:, -1] = 0  # Right wall
    
    # Inner walls
    maze[3:12, 3] = 0  # Vertical wall
    maze[3:12, 11] = 0  # Vertical wall
    maze[3, 3:12] = 0  # Horizontal wall
    maze[11, 3:12] = 0  # Horizontal wall
    maze[7, 6:9] = 0  # Small horizontal wall
    
    # Create openings
    maze[1, 1:14] = 1  # Top path
    maze[13, 1:14] = 1  # Bottom path
    maze[1:14, 1] = 1  # Left path
    maze[1:14, 13] = 1  # Right path
    maze[7, 7] = 1  # Opening in middle wall
    
    return maze

# --- Streamlit App ---
st.set_page_config(page_title="Maze Solver", layout="wide")

st.title("🧠 Interactive Maze Solver - Fixed Version")
st.markdown("Upload a black and white maze image to find the shortest path using A* algorithm")

# Sidebar
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    1. **Upload a maze image** (PNG, JPG, JPEG)
    2. **Black pixels** = Walls
    3. **White pixels** = Paths
    4. **Green cell** = Start point
    5. **Blue cell** = End point
    6. **Red path** = Solution
    """)
    
    st.header("⚙️ Settings")
    cell_size = st.slider("Cell Size (pixels)", 4, 15, 8, help="Adjust maze cell size for better visibility")
    maze_size = st.slider("Maze Size", 30, 150, 80, help="Resize maze for processing")
    
    st.header("🧪 Test Options")
    if st.button("🎯 Test with Simple Maze"):
        test_maze = create_test_maze()
        start = (1, 1)
        end = (13, 13)
        
        # Find path
        test_path = astar(test_maze, start, end)
        
        if test_path:
            st.success(f"✅ Test maze solved! Path length: {len(test_path)}")
            
            # Display test maze
            test_html = create_maze_html(test_maze, test_path, 12)
            st.components.v1.html(test_html, height=400, scrolling=True)
        else:
            st.error("❌ Could not solve test maze")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Upload Maze")
    uploaded_file = st.file_uploader("Choose a maze image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        try:
            # Load and display original image
            image = Image.open(uploaded_file)
            st.image(image, caption="Original Maze Image", use_container_width=True)
            
            # Convert to maze grid
            with st.spinner("🔄 Processing image..."):
                maze = convert_image_to_maze(image, (maze_size, maze_size))
            
            # Display maze statistics
            wall_count = np.sum(maze == 0)
            path_count = np.sum(maze == 1)
            st.info(f"📊 Maze: {maze.shape[0]}×{maze.shape[1]} | Walls: {wall_count} | Paths: {path_count}")
            
            if path_count == 0:
                st.error("❌ No paths found in the image. Make sure white areas represent paths.")
                st.stop()
            
            # Find start and end points
            start = find_nearest_path(maze, (1, 1))  # Near top-left
            end = find_nearest_path(maze, (maze.shape[0]-2, maze.shape[1]-2))  # Near bottom-right
            
            if start is None:
                start = find_nearest_path(maze, (0, 0), max_search=maze.shape[0])
            if end is None:
                end = find_nearest_path(maze, (maze.shape[0]-1, maze.shape[1]-1), max_search=maze.shape[0])
                
            if start is None or end is None:
                st.error("❌ Could not find valid start or end points")
                st.stop()
            
            st.success(f"🎯 Start: {start} | End: {end}")
            
            # Solve maze
            with st.spinner("🔍 Finding optimal path..."):
                path = astar(maze, start, end)
            
            if path is None:
                st.error("❌ No solution found - maze may be unsolvable")
                
                # Show maze without path for debugging
                debug_html = create_maze_html(maze, None, cell_size)
                st.markdown("**Maze visualization (no solution):**")
                st.components.v1.html(debug_html, height=400, scrolling=True)
            else:
                st.success(f"✅ Solution found! Path length: {len(path)} steps")
                
                # Calculate path efficiency
                manhattan_distance = abs(end[0] - start[0]) + abs(end[1] - start[1])
                efficiency = round(manhattan_distance / len(path) * 100, 1)
                st.info(f"📈 Path efficiency: {efficiency}% (Manhattan distance: {manhattan_distance})")
                
                with col2:
                    st.header("🎯 Solution Visualization")
                    
                    # Create and display the solved maze
                    maze_html = create_maze_html(maze, path, cell_size)
                    st.components.v1.html(maze_html, height=600, scrolling=True)
                    
                    # Download options
                    maze_data = {
                        "maze_size": maze.shape,
                        "path_length": len(path),
                        "start": start,
                        "end": end,
                        "path": path,
                        "efficiency": efficiency
                    }
                    
                    st.download_button(
                        label="📥 Download Solution Data",
                        data=json.dumps(maze_data, indent=2),
                        file_name=f"maze_solution_{maze.shape[0]}x{maze.shape[1]}.json",
                        mime="application/json"
                    )
                        
        except Exception as e:
            st.error(f"❌ Error processing image: {str(e)}")
            st.exception(e)

# Footer
st.markdown("---")
st.markdown("**Fixed Maze Solver** - Improved path visualization and debugging")