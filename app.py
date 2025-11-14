from flask import Flask, request, jsonify
from solver_logic import find_solution

# 初始化 Flask app
app = Flask(__name__)

@app.route('/')
def home():
    # 一个简单的主页, 确保服务在运行
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
        pieces = data.get('pieces') # 这是一个字典, e.g. {"L4": 2, ...}

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
        }), 400 # 400 Bad Request

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
        }), 200 # 200 OK
    else:
        # 即使"未找到解", 请求本身也是成功的
        return jsonify({
            "status": "failure",
            "message": message,
            "board_size": f"{width}x{height}",
            "solution": None
        }), 200 # 200 OK

# 允许从本地运行
if __name__ == '__main__':
    app.run(debug=True, port=5000)