from itertools import product

# --------------------------
# 方块定义
# --------------------------
SHAPES = {
    "I2": [(0,0), (1,0)],
    "L3": [(0,0), (1,0), (1,1)],
    "L4": [(0,0), (1,0), (2,0), (2,1)],
    "I4": [(0,0), (1,0), (2,0), (3,0)],
    "O4": [(0,0), (1,0), (0,1), (1,1)],
    "T4": [(0,0), (1,0), (2,0), (1,1)],
    "Z4": [(0,0), (1,0), (1,1), (2,1)],
    "C5": [(0,0), (1,0), (1,1), (1,2), (0,2)],
}

# --------------------------
# Emoji 定义
# --------------------------
COLORS = [
    "🟥", "🟩", "🟦", "🟨", "🟪", "🟧", "🟫",
    "🔴", "🟢", "🔵", "🟡", "🟣",
]
EMPTY = "⬜"

# --------------------------
# 工具函数：生成旋转/镜像变体
# --------------------------
def generate_variants(shape):
    variants = set()
    for flip in [1, -1]:
        coords = [(x * flip, y) for (x, y) in shape]
        for _ in range(4):
            coords = [(y, -x) for (x, y) in coords]
            minx = min(x for x, _ in coords)
            miny = min(y for _, y in coords)
            norm = tuple(sorted((x - minx, y - miny) for x, y in coords))
            variants.add(norm)
    return [list(v) for v in variants]

# --------------------------
# 棋盘类
# --------------------------
class Board:
    def __init__(self, width, height):
        self.w, self.h = width, height
        self.grid = [[None] * width for _ in range(height)]

    def find_empty(self):
        for y, x in product(range(self.h), range(self.w)):
            if self.grid[y][x] is None:
                return x, y
        return None

    def can_place(self, shape, x, y):
        for dx, dy in shape:
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx >= self.w or ny >= self.h:
                return False
            if self.grid[ny][nx] is not None:
                return False
        return True

    def place(self, shape, x, y, mark):
        for dx, dy in shape:
            self.grid[y + dy][x + dx] = mark

    def remove(self, shape, x, y):
        for dx, dy in shape:
            self.grid[y + dy][x + dx] = None
    
    def get_solution_grid(self):
        """返回表示最终棋盘的字符串列表"""
        solution_rows = []
        for row in self.grid:
            solution_rows.append(
                "".join(COLORS[c] if c is not None else EMPTY for c in row)
            )
        return solution_rows

# --------------------------
# 回溯搜索求解器
# --------------------------
def solve_recursive(board, pieces, piece_shapes, used, mark_index=0):
    empty = board.find_empty()
    if not empty:
        return True

    x, y = empty
    for name, count in pieces.items():
        if used[name] >= count:
            continue

        for shape in piece_shapes[name]:
            if board.can_place(shape, x, y):
                color_index = mark_index % len(COLORS)
                board.place(shape, x, y, color_index)
                used[name] += 1

                if solve_recursive(board, pieces, piece_shapes, used, mark_index + 1):
                    return True # 成功, 停止搜索并层层返回 True

                # 回溯
                used[name] -= 1
                board.remove(shape, x, y)

    return False # 此路不通

# --------------------------
# [!] 新增: API 的主入口函数
# --------------------------
def find_solution(width, height, pieces_input):
    """
    供 API 调用的主函数
    :param width: 棋盘宽度
    :param height: 棋盘高度
    :param pieces_input: 字典, e.g. {"L4": 2, "I4": 2, ...}
    :return: (solution, message)
             如果成功: (solution_grid, "Solution found.")
             如果失败: (None, "Error message.")
    """
    # ===== 过滤无效方块 =====
    relevant_pieces = {k: v for k, v in pieces_input.items() if k in SHAPES}
    
    # ===== 可行性检查 =====
    area_board = width * height
    area_pieces = sum(len(SHAPES[name]) * count for name, count in relevant_pieces.items())
    
    if area_board == 0:
        return None, "Error: Board area is zero."
        
    if area_board != area_pieces:
        msg = f"Error: Area mismatch. Board is {area_board}, pieces are {area_pieces}."
        return None, msg

    # ========== 初始化 ==========
    # 只为需要的方块生成变体
    piece_shapes = {k: generate_variants(SHAPES[k]) for k in relevant_pieces}
    used = {k: 0 for k in relevant_pieces}
    board = Board(width, height)

    print(f"INFO: Starting search for {width}x{height} board...") # (日志可以保留, 会打印到服务器日志中)

    # ========== 求解 ==========
    found = solve_recursive(board, relevant_pieces, piece_shapes, used)

    if found:
        print("INFO: Solution found.")
        return board.get_solution_grid(), "Solution found."
    else:
        print("INFO: No solution found.")
        return None, "No solution found for this configuration."

# --------------------------
# 主程序入口 (用于本地测试)
# --------------------------
if __name__ == "__main__":
    # 这个 main 块现在只用于本地测试
    print("--- [本地测试] ---")
    board_w, board_h = 6, 6
    test_pieces = {
        "I2": 0,
        "L3": 0, "L4": 2, "I4": 2,
        "O4": 1, "T4": 2, "Z4": 2,
        "C5": 0
    }
    
    solution, message = find_solution(board_w, board_h, test_pieces)
    
    if solution:
        print(f"成功: {message}")
        for row in solution:
            print(row)
    else:
        print(f"失败: {message}")
    print("--- [本地测试结束] ---")