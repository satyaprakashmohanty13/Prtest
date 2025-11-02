import streamlit as st
import numpy as np
import cv2
from PIL import Image
import sudoku  # make sure sudoku.py is available in the same directory

# -----------------------------
# Helper functions
# -----------------------------

def preprocess_image(cell_image: np.ndarray):
    """Preprocess a single cell image for model prediction."""
    image_resized = cv2.resize(cell_image, (28, 28), interpolation=cv2.INTER_AREA)
    image_float = image_resized.astype(np.float32) / 255.0
    image_normalized = (image_float - 0.5) / 0.5
    return image_normalized.reshape(1, 1, 28, 28)

def predict(cell_image: np.ndarray, onnx_model_path: str) -> int:
    """Predicts the digit in a cell using ONNX model."""
    classes = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    image_input = preprocess_image(cell_image)
    net = cv2.dnn.readNetFromONNX(onnx_model_path)
    net.setInput(image_input)
    output = net.forward()
    predicted_class = np.argmax(output, axis=1)[0]
    return classes[predicted_class]

def recognize_digits_onnx(grid_image: np.ndarray, onnx_model_path: str) -> np.ndarray:
    """Recognize digits in Sudoku grid image."""
    arr = np.zeros((9, 9), dtype=np.uint8)
    cells = sudoku.extract_cells(grid_image)
    for row in range(9):
        for col in range(9):
            cell = cells[row, col]
            if not sudoku.is_empty_cell(cell):
                arr[row, col] = predict(cell, onnx_model_path)
    return arr

def sudoku_solver(sudoku_image: np.ndarray):
    """Extract, recognize, solve, and display Sudoku solution."""
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

st.set_page_config(page_title="🧩 Sudoku Solver", layout="centered")

st.title("🧩 Sudoku Solver")
st.write("Upload a Sudoku puzzle image to automatically extract, recognize, and solve it!")

uploaded_file = st.file_uploader("Upload Sudoku Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    sudoku_image = np.array(Image.open(uploaded_file).convert("RGB"))
    st.image(sudoku_image, caption="Uploaded Sudoku", use_container_width=True)

    if st.button("Solve Puzzle"):
        with st.spinner("Solving... Please wait."):
            try:
                solved_img, message = sudoku_solver(sudoku_image)
                st.image(solved_img, caption="Solved Sudoku", use_container_width=True)
                st.success(message)
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("👆 Please upload a Sudoku image to get started.")
