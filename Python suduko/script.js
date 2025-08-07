document.addEventListener('DOMContentLoaded', () => {
    // Initialize UI elements
    const gridDisplay = document.getElementById('sudoku-grid');
    const solveBtn = document.getElementById('solve-btn');
    const clearBtn = document.getElementById('clear-btn');
    const resetBtn = document.getElementById('reset-btn');
    const imageLoader = document.getElementById('imageLoader');
    const uploadArea = document.getElementById('uploadArea');
    const canvas = document.getElementById('imageCanvas');
    const ctx = canvas.getContext('2d');
    const statusDisplay = document.getElementById('status');
    const loadingIndicator = document.getElementById('loadingIndicator');
    
    // Initialize game state
    let cells = [];
    let board = Array(9).fill(null).map(() => Array(9).fill(0));
    let originalBoard = Array(9).fill(null).map(() => Array(9).fill(0));
    let isProcessing = false;
    
    // Create the grid immediately when the page loads
    createGrid();
    setupDragAndDrop();
    
    // Enhanced status update function
    function updateStatus(message, type = 'info', icon = 'fas fa-info-circle') {
        // Check if statusDisplay exists
        if (!statusDisplay) {
            console.error('Status display element not found');
            return;
        }
        
        const statusElement = statusDisplay;
        const iconElement = statusElement.querySelector('i');
        const textElement = statusElement.querySelector('span');
        
        // Check if required elements exist before updating
        if (iconElement && textElement) {
            // Update content
            iconElement.className = icon;
            textElement.textContent = message;
            
            // Update styling based on type
            statusElement.className = `status-message ${type}`;
            
            // Auto-hide success messages after 3 seconds
            if (type === 'success') {
                setTimeout(() => {
                    if (statusElement && statusElement.classList.contains('success')) {
                        updateStatus('Ready for next puzzle', 'info');
                    }
                }, 3000);
            }
        } else {
            console.error('Status icon or text element not found');
            // Fallback: update the status display text directly
            statusElement.textContent = message;
        }
    }
    
    // Show/hide loading indicator
    function setLoading(isLoading, message = 'Processing...') {
        isProcessing = isLoading;
        
        // Check if loadingIndicator exists
        if (!loadingIndicator) {
            console.error('Loading indicator element not found');
            return;
        }
        
        if (isLoading) {
            const messageSpan = loadingIndicator.querySelector('span');
            if (messageSpan) {
                messageSpan.textContent = message;
            }
            loadingIndicator.classList.remove('hidden');
            
            if (solveBtn) {
                solveBtn.disabled = true;
            }
        } else {
            loadingIndicator.classList.add('hidden');
            updateSolveButtonState();
        }
    }
    
    // Update solve button state based on board content
    function updateSolveButtonState() {
        if (!solveBtn) {
            console.error('Solve button element not found');
            return;
        }
        
        const hasNumbers = board.some(row => row.some(cell => cell !== 0));
        solveBtn.disabled = !hasNumbers || isProcessing;
    }
    
    // Setup drag and drop functionality
    function setupDragAndDrop() {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            uploadArea.classList.add('dragover');
        }
        
        function unhighlight() {
            uploadArea.classList.remove('dragover');
        }
        
        uploadArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        }
        
        // Also handle click on upload area
        uploadArea.addEventListener('click', (e) => {
            // Prevent click if the target is already the file input
            if (e.target === imageLoader) {
                return;
            }
            
            if (!isProcessing) {
                // Explicitly focus and click the file input
                imageLoader.focus();
                imageLoader.click();
            }
        });
        
        // Make sure the file input is properly initialized
        if (imageLoader) {
            // Reset the file input to ensure it's in a clean state
            imageLoader.value = '';
        }
    }

    function createGrid() {
        gridDisplay.innerHTML = '';
        cells = [];
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                const cell = document.createElement('input');
                cell.type = 'text';
                cell.maxLength = 1;
                cell.id = `cell-${i}-${j}`;
                cell.classList.add('cell');

                if ((j + 1) % 3 === 0 && j < 8) {
                    cell.classList.add('border-right');
                }
                if ((i + 1) % 3 === 0 && i < 8) {
                    cell.classList.add('border-bottom');
                }

                cell.addEventListener('input', (e) => {
                    e.target.value = e.target.value.replace(/[^1-9]/g, '');
                });
                cells.push(cell);
                gridDisplay.appendChild(cell);
            }
        }
    }

    function getBoardFromGrid() {
        // This is the critical fix. We must create a deep copy of the board
        // so the solver doesn't interfere with other board states.
        const board = Array(9).fill(null).map(() => Array(9).fill(0));
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                const cell = document.getElementById(`cell-${i}-${j}`);
                board[i][j] = parseInt(cell.value) || 0;
            }
        }
        return board;
    }

    function updateGrid(currentBoard, animate = false) {
        // Safety check: ensure cells array is populated
        if (cells.length !== 81) {
            console.error('Grid not properly initialized. Cells array length:', cells.length);
            return;
        }
        
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                const cell = cells[i * 9 + j];
                if (!cell) {
                    console.error(`Cell at [${i}][${j}] is undefined`);
                    continue;
                }
                
                // Remove all special classes
                cell.classList.remove('original-digit', 'solved-digit');
                
                if (currentBoard[i][j] !== 0) {
                    const oldValue = cell.value;
                    cell.value = currentBoard[i][j];
                    
                    if (originalBoard[i][j] !== 0) {
                        cell.classList.add('original-digit');
                    } else if (animate && oldValue !== currentBoard[i][j].toString()) {
                        // Add animation for newly solved cells
                        cell.classList.add('solved-digit');
                        setTimeout(() => {
                            cell.classList.remove('solved-digit');
                        }, 500);
                    }
                } else {
                    cell.value = '';
                }
            }
        }
        
        // Update solve button state
        updateSolveButtonState();
    }
    
    // Handle file selection (both drag & drop and click)
    function handleFiles(files) {
        if (files.length === 0) return;
        
        const file = files[0];
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
            updateStatus('Please select a valid image file', 'error', 'fas fa-exclamation-triangle');
            return;
        }
        
        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            updateStatus('File size too large. Please select an image under 10MB', 'error', 'fas fa-exclamation-triangle');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(evt) {
            const base64Image = evt.target.result;
            displayImage(base64Image);
            processImageWithAPI(base64Image);
        };
        
        reader.onerror = function() {
            updateStatus('Error reading file', 'error', 'fas fa-exclamation-triangle');
        };
        
        reader.readAsDataURL(file);
    }
    
    // Display uploaded image on canvas
    function displayImage(base64Image) {
        const img = new Image();
        img.onload = function() {
            canvas.width = 450;
            canvas.height = 450;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Calculate aspect ratio to fit image properly
            const aspectRatio = img.width / img.height;
            let drawWidth = canvas.width;
            let drawHeight = canvas.height;
            let offsetX = 0;
            let offsetY = 0;
            
            if (aspectRatio > 1) {
                drawHeight = canvas.width / aspectRatio;
                offsetY = (canvas.height - drawHeight) / 2;
            } else {
                drawWidth = canvas.height * aspectRatio;
                offsetX = (canvas.width - drawWidth) / 2;
            }
            
            ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);
            canvas.classList.add('visible');
        };
        img.src = base64Image;
    }

    async function processImageWithAPI(base64Image) {
        setLoading(true, 'Analyzing image with AI...');
        updateStatus('Processing image...', 'info', 'fas fa-cog fa-spin');
        
        try {
            const response = await fetch('http://127.0.0.1:5000/process-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: base64Image }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server error (${response.status}): ${errorText}`);
            }

            const data = await response.json();
            if (data.grid) {
                originalBoard = JSON.parse(JSON.stringify(data.grid)); // Deep copy
                board = JSON.parse(JSON.stringify(data.grid)); // Copy to working board
                updateGrid(board);
                updateStatus('Puzzle detected successfully! Ready to solve.', 'success', 'fas fa-check-circle');
            } else {
                throw new Error('No puzzle detected in image. Please try a clearer image.');
            }
        } catch (error) {
            console.error('Error processing image:', error);
            updateStatus(error.message, 'error', 'fas fa-exclamation-triangle');
        } finally {
            setLoading(false);
        }
    }

    imageLoader.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            handleFiles(e.target.files);
        }
    });

    solveBtn.addEventListener('click', async () => {
        if (isProcessing) return;
        
        board = getBoardFromGrid();
        setLoading(true, 'Solving puzzle...');
        updateStatus('AI is solving the puzzle...', 'info', 'fas fa-magic');
        
        try {
            const response = await fetch('http://127.0.0.1:5000/solve-puzzle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ board }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server error (${response.status}): ${errorText}`);
            }

            const data = await response.json();
            if (data.solution) {
                board = data.solution;
                updateGrid(board, true); // Enable animations for solved cells
                updateStatus('Puzzle solved successfully! 🎉', 'success', 'fas fa-trophy');
            } else if (data.error) {
                throw new Error(data.error);
            } else {
                throw new Error('No solution found for this puzzle.');
            }
        } catch (error) {
            console.error('Error solving puzzle:', error);
            updateStatus(error.message, 'error', 'fas fa-exclamation-triangle');
        } finally {
            setLoading(false);
        }
    });

    clearBtn.addEventListener('click', () => {
        board = Array(9).fill(null).map(() => Array(9).fill(0));
        originalBoard = Array(9).fill(null).map(() => Array(9).fill(0));
        updateGrid(board);
        updateStatus('Board cleared.', 'info', 'fas fa-eraser');
    });

    resetBtn.addEventListener('click', () => {
        // Reset board and grid
        board = Array(9).fill(null).map(() => Array(9).fill(0));
        originalBoard = Array(9).fill(null).map(() => Array(9).fill(0));
        updateGrid(board);
        // Clear and hide canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        canvas.style.display = 'none';
        // Reset file input
        imageLoader.value = '';
        // Reset status
        statusDisplay.textContent = 'Upload an image of a Sudoku puzzle to begin.';
    });
});
