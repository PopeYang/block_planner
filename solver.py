from itertools import product

# --------------------------
# 方块定义（相对坐标）
# --------------------------
SHAPES = {
    "L3": [(0,0), (1,0), (1,1)],              # 三格L形
    "L4": [(0,0), (1,0), (2,0), (2,1)],       # 四格L形
    "I4": [(0,0), (1,0), (2,0), (3,0)],       # 直线4格
    "O4": [(0,0), (1,0), (0,1), (1,1)],       # 方块
    "T4": [(0,0), (1,0), (2,0), (1,1)],       # T型
    "Z4": [(0,0), (1,0), (1,1), (2,1)],       # Z型
}

# --------------------------
# 工具函数：生成旋转/镜像变体
# --------------------------
def generate_variants(shape):
    variants = set()
    for flip in [1, -1]:
        coords = [(x * flip, y) for (x, y) in shape]
        for _ in range(4):
            coords = [(y, -x) for (x, y) in coords]  # 旋转90°
            # 平移到(0,0)起始（归一化）
            minx = min(x for x, _ in coords)
            miny = min(y for _, y in coords)
            norm = tuple(sorted((x - minx, y - miny) for x, y in coords))
            variants.add(norm)
    return [list(v) for v in variants]

# --------------------------
# 彩色方块生成器 (Emoji 版本)
# --------------------------
COLORS = [
    "🟥",
    "🟩",
    "🟦",
    "🟨",
    "🟪",
    "🟧",
    "🟫",
    "🔴",
    "🟢",
    "🔵",
    "🟡",
    "🟣",
]

EMPTY = "⬜"

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

    def is_full(self):
        return all(all(cell is not None for cell in row) for row in self.grid)

    def print(self):
        print()
        for row in self.grid:
            # 这种 join 方式在大多数现代终端上能很好地对齐 Emoji
            print("".join(COLORS[c] if c is not None else EMPTY for c in row))
        print()

# --------------------------
# 回溯搜索求解器
# --------------------------
def solve(board, pieces, piece_shapes, used, mark_index=0):
    empty = board.find_empty()
    if not empty:
        # 已填满
        board.print()
        return True

    x, y = empty  # 选择当前左上角第一个空格
    for name, count in pieces.items():
        if used[name] >= count:
            continue

        for shape in piece_shapes[name]:
            # 尝试从 (x, y) 开始放置当前形状
            if board.can_place(shape, x, y):
                color_index = mark_index % len(COLORS)
                board.place(shape, x, y, color_index)
                used[name] += 1

                if solve(board, pieces, piece_shapes, used, mark_index + 1):
                    return True

                used[name] -= 1
                board.remove(shape, x, y)

    return False

# --------------------------
# 主程序入口
# --------------------------
if __name__ == "__main__":
    # ========== 参数配置 ==========
    board_size = (6, 6)
    pieces = {
        "L3": 4,
        "L4": 1,
        "I4": 1,
        "O4": 1,
        "T4": 1,
        "Z4": 2,
    }

    # ===== 可行性检查 =====
    area_board = board_size[0] * board_size[1]
    area_pieces = sum(len(SHAPES[name]) * count for name, count in pieces.items())
    if area_board != area_pieces:
        print(f"❌ 无法满布：棋盘面积 {area_board} ≠ 方块总面积 {area_pieces}")
        exit(0)

    # ========== 初始化 ==========
    piece_shapes = {k: generate_variants(v) for k, v in SHAPES.items()}
    used = {k: 0 for k in pieces}
    board = Board(*board_size)

    print(f"\n🎮 开始搜索 {board_size[0]}x{board_size[1]} 的平铺方案...\n")
    found = solve(board, pieces, piece_shapes, used)

    if not found:
        print("❌ 无法满布。")