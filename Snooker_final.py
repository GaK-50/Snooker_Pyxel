# Snooker Game with Difficulty, Point Chart, and Menu Indicator
import pyxel
import math

CANVAS_WIDTH = 320
CANVAS_HEIGHT = 280
TABLE_WIDTH = 256
TABLE_HEIGHT = 144
TABLE_X = (CANVAS_WIDTH - TABLE_WIDTH) // 2
TABLE_Y = 20

BALL_RADIUS = 5
POCKET_RADIUS = int(8 * 1.5)
FRICTION = 0.96

WHITE = 7
RED = 8
YELLOW = 10
GREEN = 11
BROWN = 12
BLUE = 13
PINK = 6
BLACK = 0
TABLE_COLOR = 3
WOOD_COLOR = BROWN
BLANK_SPACE_COLOR = 5

POINT_VALUES = {
    "red": 1,
    "yellow": 2,
    "green": 3,
    "brown": 4,
    "blue": 5,
    "pink": 6,
    "black": 7,
}

COLOR_BALLS = {"yellow", "green", "brown", "blue", "pink", "black"}

class Ball:
    def __init__(self, x, y, color, name=""):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.color = color
        self.name = name
        self.in_play = True

    def update(self):
        if not self.in_play:
            return
        self.x += self.vx
        self.y += self.vy
        self.vx *= FRICTION
        self.vy *= FRICTION
        if abs(self.vx) < 0.05: self.vx = 0
        if abs(self.vy) < 0.05: self.vy = 0

        if self.x - BALL_RADIUS < TABLE_X:
            self.vx = -self.vx
            self.x = TABLE_X + BALL_RADIUS
        elif self.x + BALL_RADIUS > TABLE_X + TABLE_WIDTH:
            self.vx = -self.vx
            self.x = TABLE_X + TABLE_WIDTH - BALL_RADIUS

        if self.y - BALL_RADIUS < TABLE_Y:
            self.vy = -self.vy
            self.y = TABLE_Y + BALL_RADIUS
        elif self.y + BALL_RADIUS > TABLE_Y + TABLE_HEIGHT:
            self.vy = -self.vy
            self.y = TABLE_Y + TABLE_HEIGHT - BALL_RADIUS

    def draw(self):
        if self.in_play:
            pyxel.circ(self.x, self.y, BALL_RADIUS, self.color)

class Game:
    def __init__(self):
        pyxel.init(CANVAS_WIDTH, CANVAS_HEIGHT, title="Snooker Game")
        pyxel.mouse(True)
        self.state = "menu"
        self.difficulty = None
        self.init_sounds()
        pyxel.run(self.update, self.draw)

    def init_sounds(self):
        pyxel.sound(0).set("c1", "p", "7", "n", 10)
        pyxel.sound(1).set("c2", "p", "4", "n", 8)
        pyxel.sound(2).set("f1f0f1", "t", "777", "n", 20)
        pyxel.sound(3).set("g3c2", "s", "7531", "n", 30)

    def start_game(self, difficulty):
        self.state = "play"
        self.difficulty = difficulty
        self.score = 0
        self.shots = 0
        self.message = ""
        self.game_cleared = False
        self.potted = []
        self.balls = []
        self.pockets = self.create_pockets()
        self.create_balls(difficulty)
        self.cue_ball = self.balls[0]

    def create_pockets(self):
        return [
            (TABLE_X, TABLE_Y),
            (TABLE_X + TABLE_WIDTH // 2, TABLE_Y),
            (TABLE_X + TABLE_WIDTH - 1, TABLE_Y),
            (TABLE_X, TABLE_Y + TABLE_HEIGHT - 1),
            (TABLE_X + TABLE_WIDTH // 2, TABLE_Y + TABLE_HEIGHT - 1),
            (TABLE_X + TABLE_WIDTH - 1, TABLE_Y + TABLE_HEIGHT - 1),
        ]

    def create_balls(self, difficulty):
        red_counts = {
            "easy": 3,
            "normal": 6,
            "hard": 10,
        }
        red_count = red_counts[difficulty]

        # Cue ball
        d_x = TABLE_X + 32
        d_y = TABLE_Y + TABLE_HEIGHT // 2
        self.balls.append(Ball(d_x, d_y, WHITE, "cue"))

        # Red triangle
        triangle_x = TABLE_X + TABLE_WIDTH // 2 + 30
        triangle_y = TABLE_Y + TABLE_HEIGHT // 2
        offset = BALL_RADIUS * 2 + 1
        reds = 0
        row = 0
        while reds < red_count:
            for col in range(row + 1):
                if reds >= red_count:
                    break
                x = triangle_x + row * offset
                y = triangle_y - row * offset / 2 + col * offset
                self.balls.append(Ball(x, y, RED, "red"))
                reds += 1
            row += 1

        # Color balls
        self.balls.append(Ball(triangle_x - 2 * offset, triangle_y, PINK, "pink"))
        self.balls.append(Ball(triangle_x + 4 * offset, triangle_y, BLACK, "black"))
        center_x = TABLE_X + TABLE_WIDTH // 2
        center_y = TABLE_Y + TABLE_HEIGHT // 2
        self.balls.append(Ball(center_x, center_y, BLUE, "blue"))
        baulk_y = TABLE_Y + TABLE_HEIGHT // 2
        baulk_x = TABLE_X + 20
        self.balls.append(Ball(baulk_x - 20, baulk_y - 20, GREEN, "green"))
        self.balls.append(Ball(baulk_x, baulk_y, BROWN, "brown"))
        self.balls.append(Ball(baulk_x - 20, baulk_y + 20, YELLOW, "yellow"))

    def update(self):
        if self.state == "menu":
            if pyxel.btnp(pyxel.KEY_1): self.start_game("easy")
            if pyxel.btnp(pyxel.KEY_2): self.start_game("normal")
            if pyxel.btnp(pyxel.KEY_3): self.start_game("hard")

        elif self.state == "play":
            if pyxel.btnp(pyxel.KEY_R):
                self.start_game(self.difficulty)
                self.message = "Game restarted."
            if pyxel.btnp(pyxel.KEY_M):
                self.state = "menu"

            if pyxel.btnp(pyxel.KEY_P) and not self.is_ball_moving() and not self.game_cleared:
                mx, my = pyxel.mouse_x, pyxel.mouse_y
                dx = self.cue_ball.x - mx
                dy = self.cue_ball.y - my
                dist = math.hypot(dx, dy)
                if dist > 0:
                    power = min(dist / 10, 7)
                    self.cue_ball.vx = dx / dist * power
                    self.cue_ball.vy = dy / dist * power
                    self.shots += 1
                    self.message = f"Shot! Total shots: {self.shots}"
                    pyxel.play(0, 0)

            for ball in self.balls:
                ball.update()

            self.handle_collisions()

            for ball in self.balls:
                if ball.in_play:
                    for px, py in self.pockets:
                        if math.hypot(ball.x - px, ball.y - py) < POCKET_RADIUS:
                            ball.in_play = False
                            ball.vx = ball.vy = 0
                            self.handle_potted(ball)
                            break

            if not self.cue_ball.in_play:
                self.reset_cue_ball()

            if not self.game_cleared:
                self.check_game_clear()

    def handle_collisions(self):
        for i, b1 in enumerate(self.balls):
            if not b1.in_play:
                continue
            for j in range(i + 1, len(self.balls)):
                b2 = self.balls[j]
                if not b2.in_play:
                    continue
                dx = b2.x - b1.x
                dy = b2.y - b1.y
                dist = math.hypot(dx, dy)
                if dist == 0 or dist >= BALL_RADIUS * 2:
                    continue
                nx, ny = dx / dist, dy / dist
                overlap = BALL_RADIUS * 2 - dist

                b1.x -= nx * overlap / 2
                b1.y -= ny * overlap / 2
                b2.x += nx * overlap / 2
                b2.y += ny * overlap / 2

                tx, ty = -ny, nx
                v1n = b1.vx * nx + b1.vy * ny
                v1t = b1.vx * tx + b1.vy * ty
                v2n = b2.vx * nx + b2.vy * ny
                v2t = b2.vx * tx + b2.vy * ty

                b1.vx = v2n * nx + v1t * tx
                b1.vy = v2n * ny + v1t * ty
                b2.vx = v1n * nx + v2t * tx
                b2.vy = v1n * ny + v2t * ty

                pyxel.play(1, 1)

    def handle_potted(self, ball):
        if ball.name == "cue":
            self.message = "Cue ball potted!"
            pyxel.play(2, 2)
        else:
            self.potted.append(ball.name)
            self.score += POINT_VALUES.get(ball.name, 0)
            self.message = f"Potted {ball.name}! +{POINT_VALUES.get(ball.name, 0)}"
            pyxel.play(1, 1)

    def check_game_clear(self):
        if all(not b.in_play for b in self.balls if b.name in COLOR_BALLS):
            self.game_cleared = True
            self.message = f"🎉 GAME CLEAR! Score: {self.score}, Shots: {self.shots}"
            pyxel.play(3, 3)

    def reset_cue_ball(self):
        self.cue_ball.x = TABLE_X + 32
        self.cue_ball.y = TABLE_Y + TABLE_HEIGHT // 2
        self.cue_ball.vx = self.cue_ball.vy = 0
        self.cue_ball.in_play = True
        self.message += " Cue ball reset."

    def is_ball_moving(self):
        return any(abs(b.vx) > 0 or abs(b.vy) > 0 for b in self.balls if b.in_play)

    def draw(self):
        pyxel.cls(BLANK_SPACE_COLOR)

        if self.state == "menu":
            pyxel.text(100, 50, "--- Snooker Game ---", 7)
            pyxel.text(90, 80, "Select Difficulty:", 10)
            pyxel.text(90, 100, "1 - Easy (3 reds)", 6)
            pyxel.text(90, 110, "2 - Normal (6 reds)", 6)
            pyxel.text(90, 120, "3 - Hard (10 reds)", 6)
            return

        pyxel.rect(TABLE_X - 6, TABLE_Y - 6, TABLE_WIDTH + 12, TABLE_HEIGHT + 12, WOOD_COLOR)
        pyxel.rect(TABLE_X, TABLE_Y, TABLE_WIDTH, TABLE_HEIGHT, TABLE_COLOR)

        for px, py in self.pockets:
            pyxel.circ(px, py, POCKET_RADIUS, 0)

        if not self.is_ball_moving() and not self.game_cleared:
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            pyxel.line(mx, my, self.cue_ball.x, self.cue_ball.y, WHITE)

        for ball in self.balls:
            ball.draw()

        ui_y = TABLE_Y + TABLE_HEIGHT + 10
        pyxel.text(10, ui_y, f"Score: {self.score}", 7)
        pyxel.text(10, ui_y + 10, f"Shots: {self.shots}", 13)
        pyxel.text(10, ui_y + 20, f"Difficulty: {self.difficulty.title()}", 6)

        if not self.is_ball_moving() and not self.game_cleared:
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            dist = math.hypot(mx - self.cue_ball.x, my - self.cue_ball.y)
            power = min(dist / 10, 7)
            pyxel.text(10, ui_y + 35, "Power:", 7)
            pyxel.rect(60, ui_y + 36, int(power * 10), 5, RED)

        pyxel.text(10, ui_y + 50, self.message, 7)

        # Point chart
        pyxel.text(240, ui_y, "Points", 7)
        for i, (name, pts) in enumerate(POINT_VALUES.items()):
            pyxel.text(240, ui_y + 10 + i * 8, f"{name.capitalize()}: {pts}", 6)

        # Menu indicator
        pyxel.text(5, CANVAS_HEIGHT - 10, "M: Menu", 5)

        if self.game_cleared:
            pyxel.text(90, ui_y + 70, "🎉 GAME CLEAR! 🎉", pyxel.frame_count % 16)

Game()

