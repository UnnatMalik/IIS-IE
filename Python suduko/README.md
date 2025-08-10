# Sudoku Solver Web App

A web-based Sudoku solver that uses a Python Flask backend for image-based grid extraction and puzzle solving.

## Features

- Upload a Sudoku puzzle image and extract the grid using OCR.space API.
- Solve the puzzle using Sugoku API.
- Interactive web UI for manual entry, clearing, and resetting the board.

## Setup

1. **Clone the repository** and navigate to the project folder.

2. **Create a virtual environment** (optional but recommended):
   ```sh
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure OCR.space API key**:
   - Get a free API key from [OCR.space](https://ocr.space/ocrapi).
   - Create a `.env` file in the project root:
     ```
     OCR_API_KEY=YOUR_API_KEY_HERE
     ```

5. **Run the Flask server**:
   ```sh
   python app.py
   ```

6. **Open the app**:
   - Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## API Endpoints

- `POST /process-image`  
  Accepts: `{ "image": "<base64 image>" }`  
  Returns: `{ "grid": [[...], ...] }`

- `POST /solve-puzzle`  
  Accepts: `{ "board": [[...], ...] }`  
  Returns: `{ "solution": [[...], ...] }`

## File Structure

- `app.py` — Flask backend
- `index.html` — Frontend UI
- `script.js` — Frontend logic
- `style.css` — Styling
- `.env` — API key (not committed)
- `requirements.txt` — Python dependencies

## License

MIT License
