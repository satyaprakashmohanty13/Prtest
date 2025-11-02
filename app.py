import streamlit as st
import numpy as np
import cv2
from PIL import Image
import sudoku  # your existing sudoku module

# -----------------------------
# Helper functions
# -----------------------------
def preprocess_image(cell_image: np.ndarray):
    image_resized = cv2.resize(cell_image, (28, 28), interpolation=cv2.INTER_AREA)
    image_float = image_resized.astype(np.float32) / 255.0
    image_normalized = (image_float - 0.5) / 0.5
    return image_normalized.reshape(1, 1, 28, 28)

def predict(cell_image: np.ndarray, onnx_model_path: str) -> int:
    classes = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    image_input = preprocess_image(cell_image)
    net = cv2.dnn.readNetFromONNX(onnx_model_path)
    net.setInput(image_input)
    output = net.forward()
    predicted_class = np.argmax(output, axis=1)[0]
    return classes[predicted_class]

def recognize_digits_onnx(grid_image: np.ndarray, onnx_model_path: str) -> np.ndarray:
    arr = np.zeros((9, 9), dtype=np.uint8)
    cells = sudoku.extract_cells(grid_image)
    for row in range(9):
        for col in range(9):
            cell = cells[row, col]
            if not sudoku.is_empty_cell(cell):
                arr[row, col] = predict(cell, onnx_model_path)
    return arr

# -----------------------------
# Simple backtracking solver
# -----------------------------
def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def solve_sudoku(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                return False
    return True

# -----------------------------
# Sudoku solver from image
# -----------------------------
def sudoku_solver(sudoku_image: np.ndarray):
    sudoku_grid = sudoku.extract_grid(sudoku_image, size=9 * 50)
    if sudoku_grid is not None:
        puzzle = recognize_digits_onnx(sudoku_grid, 'digits.onnx')
        puzzle_copy = puzzle.copy()
        if sudoku.solve(puzzle):
            solution = sudoku.get_solution(puzzle_copy, puzzle)
            sudoku.draw_solution(sudoku_grid, solution, (0, 0, 255))
            sudoku_grid = cv2.cvtColor(sudoku_grid, cv2.COLOR_BGR2RGB)
            return Image.fromarray(sudoku_grid), "✅ Puzzle Solved!"
        else:
            return Image.new("RGB", (450, 450), color="red"), "❌ Puzzle is unsolvable!"
    else:
        return Image.new("RGB", (450, 450), color="gray"), "⚠️ Can't extract Sudoku grid!"

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="🧩 Sudoku Solver", layout="wide")
st.title("🧩 Sudoku Solver")
st.write("Upload a Sudoku puzzle image or enter digits manually to solve it!")

tab1, tab2 = st.tabs(["📸 Solve from Image", "✏️ Solve Manually"])

# -----------------------------
# Tab 1 — Image Upload
# -----------------------------
with tab1:
    uploaded_file = st.file_uploader("Upload Sudoku Image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        sudoku_image = np.array(Image.open(uploaded_file).convert("RGB"))
        st.image(sudoku_image, caption="Uploaded Sudoku", use_container_width=True)

        if st.button("🔍 Solve from Image"):
            with st.spinner("Solving... Please wait."):
                try:
                    solved_img, message = sudoku_solver(sudoku_image)
                    st.image(solved_img, caption="Solved Sudoku", use_container_width=True)
                    st.success(message)
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info("👆 Please upload a Sudoku image to get started.")

# -----------------------------
# Tab 2 — Manual Input Sudoku
# -----------------------------
with tab2:
    st.write("Enter Sudoku numbers below (leave 0 or blank for empty cells):")
    grid = np.zeros((9, 9), dtype=int)
    cols = st.columns(9)
    for i in range(9):
        for j in range(9):
            key = f"cell_{i}_{j}"
            val = cols[j].text_input("", value="", key=key, max_chars=1)
            grid[i][j] = int(val) if val.isdigit() else 0

    if st.button("🧠 Solve Manually Entered Sudoku"):
        with st.spinner("Solving Sudoku..."):
            puzzle = grid.copy()
            if solve_sudoku(puzzle):
                st.success("✅ Solution Found!")
                solved_grid = puzzle.tolist()
                st.table(solved_grid)
            else:
                st.error("❌ This Sudoku puzzle is unsolvable!")
