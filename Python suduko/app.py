import os
import base64
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

from flask import send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')
OCR_API_KEY = os.getenv('OCR_API_KEY')

if not OCR_API_KEY or OCR_API_KEY == 'YOUR_API_KEY_HERE':
    raise RuntimeError('ERROR: OCR.space API key is missing. Please add it to your .env file.')

def is_valid(board, row, col, num):
    """Check if placing num at board[row][col] is valid according to Sudoku rules"""
    # Check row
    for x in range(9):
        if board[row][x] == num:
            return False
 
    # Check column
    for x in range(9):
        if board[x][col] == num:
            return False
 
    # Check 3x3 sub-grid
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
 
    return True

def solve_sudoku(board):
    """Solve Sudoku puzzle using backtracking algorithm"""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:  # Empty cell found
                for num in range(1, 10):  # Try numbers 1-9
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0  # Backtrack
                return False  # No valid number found
    return True  # All cells filled successfully

def encode_board(board):
    return '%5B' + '%5D%2C%5B'.join([','.join(map(str, row)) for row in board]) + '%5D'

def encode_params(params):
    return '&'.join(f'{key}=%5B{encode_board(value)}%5D' for key, value in params.items())

def parse_ocr_result(parsed_result):
    grid = [[0 for _ in range(9)] for _ in range(9)]
    lines = parsed_result.get('TextOverlay', {}).get('Lines', [])
    if not lines:
        return grid
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    for line in lines:
        for word in line['Words']:
            min_x = min(min_x, word['Left'])
            min_y = min(min_y, word['Top'])
            max_x = max(max_x, word['Left'] + word['Width'])
            max_y = max(max_y, word['Top'] + word['Height'])
    if float('inf') in [min_x, min_y] or float('-inf') in [max_x, max_y]:
        return grid
    puzzle_width = max_x - min_x
    puzzle_height = max_y - min_y
    cell_width = puzzle_width / 9
    cell_height = puzzle_height / 9
    for line in lines:
        for word in line['Words']:
            digit_text = word['WordText'].strip()[:1]
            try:
                digit = int(digit_text)
            except ValueError:
                continue
            if 1 <= digit <= 9:
                center_x = word['Left'] + word['Width'] / 2
                center_y = word['Top'] + word['Height'] / 2
                col = int((center_x - min_x) / cell_width)
                row = int((center_y - min_y) / cell_height)
                if 0 <= row < 9 and 0 <= col < 9 and grid[row][col] == 0:
                    grid[row][col] = digit
    return grid

@app.route('/process-image', methods=['POST'])
def process_image():
    data = request.get_json()
    image = data.get('image')
    if not image:
        return jsonify({'error': 'No image provided'}), 400
    if not image.startswith('data:image'):
        image = f'data:image/png;base64,{image}'
    payload = {
        'base64Image': image,
        'OCREngine': '2',
        'isOverlayRequired': 'true',
        'detectOrientation': 'true'
    }
    headers = {'apikey': OCR_API_KEY}
    response = requests.post('https://api.ocr.space/parse/image', data=payload, headers=headers)
    data = response.json()
    if data.get('IsErroredOnProcessing'):
        return jsonify({'error': data.get('ErrorMessage', ['Unknown error'])[0]}), 500
    parsed_result = data['ParsedResults'][0]
    grid = parse_ocr_result(parsed_result)
    return jsonify({'grid': grid})

@app.route('/solve-puzzle', methods=['POST'])
def solve_puzzle():
    data = request.get_json()
    board = data.get('board')
    
    if not board or not isinstance(board, list):
        return jsonify({'error': 'Invalid board data provided.'}), 400
    
    # Validate board dimensions
    if len(board) != 9 or any(len(row) != 9 for row in board):
        return jsonify({'error': 'Board must be 9x9 grid.'}), 400
    
    # Validate board values
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if not isinstance(cell, int) or cell < 0 or cell > 9:
                return jsonify({'error': f'Invalid value at position ({i}, {j}). Values must be integers 0-9.'}), 400
    
    # Create a deep copy of the board to avoid modifying the original
    import copy
    solution_board = copy.deepcopy(board)
    
    # Try to solve the puzzle
    if solve_sudoku(solution_board):
        return jsonify({'solution': solution_board})
    else:
        return jsonify({'error': 'No solution exists for this Sudoku puzzle.'}), 400

@app.route('/')
def root():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    # Serve static files (script.js, style.css)
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(debug=True)