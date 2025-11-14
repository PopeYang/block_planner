from flask import Flask, request, jsonify
from flask_cors import CORS
from solver_logic import find_solution

# 初始化 Flask app
app = Flask(__name__)

# 配置 CORS
CORS(app, origins=[
    "http://localhost:3000",      # 允许本地开发
    "https://ppll.top",           # 允许你的自定义域名
    "https://popeyang.github.io"  # 允许 GitHub Pages 的实际域名
])


@app.route('/')
def home():
    """
    一个简单的主页, 确保服务在运行
    """
    return "Tiling Puzzle Solver API is running. POST to /solve"

@app.route('/solve', methods=['POST'])
def handle_solve():
    """
    API 主端点
    """
    # 1. 获取传入的 JSON 数据
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No input data provided"}), 400

    try:
        # 2. 解析输入
        width = int(data.get('width'))
        height = int(data.get('height'))
        pieces = data.get('pieces') 

        if not all([isinstance(width, int), isinstance(height, int), isinstance(pieces, dict)]):
             raise ValueError("Invalid input types.")
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers.")

    except (ValueError, TypeError, AttributeError):
        return jsonify({
            "status": "error",
            "message": "Invalid input format.",
            "expected_format": {
                "width": "integer (positive)",
                "height": "integer (positive)",
                "pieces": "A dictionary, e.g. {'L4': 2, 'I4': 2}"
            }
        }), 400 

    # 3. 调用核心逻辑
    print(f"API: Received job for {width}x{height} with pieces: {pieces}")
    solution_grid, message = find_solution(width, height, pieces)

    # 4. 根据结果返回 JSON
    if solution_grid:
        return jsonify({
            "status": "success",
            "message": message,
            "board_size": f"{width}x{height}",
            "solution": solution_grid
        }), 200 
    else:
        return jsonify({
            "status": "failure",
            "message": message,
            "board_size": f"{width}x{height}",
            "solution": None
        }), 200


# 允许从本地运行 (e.g. `python app.py`)
if __name__ == '__main__':
    app.run(debug=True, port=5000)