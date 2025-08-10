
# Maze Pathfinder Web App

This project is a **Streamlit-based web application** that allows users to upload a maze image, specify start/end points, and visualize the shortest path using the A\* algorithm.

***

## Features

- **Image Upload:** Upload maze images (JPG/PNG).
- **Image-to-Grid Conversion:** Turns image pixels into maze cells (walls/paths).
- **A\* Search Algorithm:** Finds shortest path from start to end.
- **Visual Path Display:** Overlays solution on the maze in the web UI.
- **User Point Selection:** Snap start/end points to nearest path if chosen on a wall.
- **Simple UI:** Powered by Streamlit.

***

## How it Works

1. **Upload & Preprocess Image:** Resizes and binarizes your maze image.
2. **Grid Extraction:** Turns image into a 2D maze grid (1 = path, 0 = wall).
3. **Point Picking:** Lets you choose start/end (auto-corrects invalid points).
4. **Pathfinding:** Uses A\* to compute shortest route.
5. **Visualization:** Draws solution path over the maze.

***

## How to Run

```bash
pip install streamlit pillow numpy opencv-python
streamlit run app.py
```

***

## Code Explanation

This section describes the code logic and how the main components work together:

### 1. Imports & Dependencies

- **Streamlit:** User web UI.
- **Pillow:** Image processing.
- **NumPy:** Array/matrix operations.
- **OpenCV:** Advanced image processing (blurring, thresholding).
- **heapq:** Efficient priority queue (for A\*).
- **Collections:** Fast BFS for point correction.

### 2. Key Functions and Their Roles

#### heuristic(a, b)
- Computes the Manhattan distance between two points for A\*'s heuristic function.

#### astar(maze, start, end)
- Implements the A* algorithm:
  - Works on a 2D array (`maze`) of 0s and 1s.
  - Explores neighboring cells to find the lowest-cost path from `start` to `end`.
  - Uses a priority queue (`heapq`) to always expand the most promising cell first.
  - Backtracks from the goal to reconstruct the final path once found.
  - Returns `None` if no path exists.

#### find_nearest_path(maze, point, max_search=50)
- If the user picks a start/end inside a wall, this function uses BFS to search for the nearest valid path cell (a cell with value 1), so that the app will still try to solve the maze.

#### convert_image_to_maze(image, target_size=(100, 100))
- Converts a raw image to a usable 2D grid:
  - Converts to grayscale and resizes to standard size for processing.
  - Applies Gaussian blur: removes small speckles/noise.
  - Uses adaptive thresholding: turns image into clear black-and-white.
  - Cleans up tiny holes via morphological "close" operation (OpenCV).
  - Produces a NumPy array of 0s (walls) / 1s (paths).

#### create_maze_html(maze, path=None, cell_size=6)
- Renders the maze visually in Streamlit:
  - Generates HTML/CSS to show the maze grid.
  - If given a solution `path`, overlays it on the grid for easy visualization.

### 3. Streamlit App Logic

- **File Upload Section:** Lets users upload a maze image.
- **Maze Processing:** Immediately cleans and converts the image into a usable maze grid.
- **Point Selector:** Allows users to set start/end rows and columns via number inputs, auto-corrects with `find_nearest_path`.
- **Pathfinding:** Triggers `astar` to solve the maze on user command.
- **Display:** Shows the maze and overlays the computed path when ready.

***

## File Overview

- `app.py` — Contains all main logic and UI for the application.

***

## Tips and Notes

- Use high-contrast maze images for best results.
- Very complex mazes may be resized during processing.
- If no path is found, try different start/end locations or a simpler maze image.

***

