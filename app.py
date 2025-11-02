import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# -----------------------------
# Backtracking Sudoku Solver
# -----------------------------
def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    start_row, start_col = 3*(row//3), 3*(col//3)
    for i in range(3):
        for j in range(3):
            if board[start_row+i][start_col+j] == num:
                return False
    return True

def solve_sudoku(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1,10):
                    if is_valid(board,row,col,num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                return False
    return True

# -----------------------------
# Draw Sudoku grid as image
# -----------------------------
def draw_sudoku_image(board):
    cell_size = 50
    grid_size = 9*cell_size
    img = Image.new("RGB", (grid_size, grid_size), color="white")
    draw = ImageDraw.Draw(img)
    
    # Load a font
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()
    
    # Draw numbers
    for i in range(9):
        for j in range(9):
            if board[i][j] != 0:
                x = j*cell_size + 15
                y = i*cell_size + 10
                draw.text((x,y), str(board[i][j]), fill="black", font=font)
    
    # Draw grid lines
    for i in range(10):
        width = 3 if i%3==0 else 1
        # Horizontal
        draw.line([(0,i*cell_size),(grid_size,i*cell_size)], fill="black", width=width)
        # Vertical
        draw.line([(i*cell_size,0),(i*cell_size,grid_size)], fill="black", width=width)
    
    return img

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="🧩 Sudoku Solver", layout="centered")
st.title("🧩 Sudoku Solver — Manual Input")
st.write("Type digits into the grid. Leave blank for empty cells.")

# -----------------------------
# Generate CSS Sudoku Grid
# -----------------------------
grid_html = """
<style>
.sudoku-grid {
  display: grid;
  grid-template-columns: repeat(9, 40px);
  grid-template-rows: repeat(9, 40px);
  gap: 1px;
  margin: 10px 0;
}
.sudoku-grid input {
  width: 40px;
  height: 40px;
  text-align: center;
  font-size: 20px;
  border: 1px solid #555;
  outline: none;
}
.sudoku-grid input:focus {
  border: 2px solid #007BFF;
}
.sudoku-grid input:nth-child(3n) {
  border-right: 2px solid #000;
}
.sudoku-grid input:nth-child(n+19):nth-child(-n+27),
.sudoku-grid input:nth-child(n+46):nth-child(-n+54),
.sudoku-grid input:nth-child(n+73):nth-child(-n+81) {
  border-bottom: 2px solid #000;
}
</style>
<div class="sudoku-grid">
"""

# Create input boxes
for i in range(9):
    for j in range(9):
        grid_html += f'<input type="text" id="cell_{i}_{j}" maxlength="1" />'
grid_html += "</div>"

# Display grid
st.components.v1.html(grid_html, height=400)

# -----------------------------
# Hidden Text Inputs for Python
# -----------------------------
st.write("Alternatively, you can fill numbers here for Python to read:")
board_input = []
for i in range(9):
    row_input = st.text_input(f"Row {i+1}", value="0 0 0 0 0 0 0 0 0")
    board_input.append([int(x) if x.isdigit() else 0 for x in row_input.strip().split()[:9]])

# -----------------------------
# Solve Button
# -----------------------------
if st.button("🧠 Solve Sudoku"):
    board = np.array(board_input)
    puzzle = board.copy()
    if solve_sudoku(puzzle):
        st.success("✅ Sudoku Solved!")
        img = draw_sudoku_image(puzzle)
        st.image(img, use_column_width=False)
    else:
        st.error("❌ This Sudoku puzzle is unsolvable!")
