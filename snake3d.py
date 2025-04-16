import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random
import math
import time

# Constants
WIN_SIZE = (800, 600)
GRID_SIZE = 20
CELL_SIZE = WIN_SIZE[0] // GRID_SIZE
SPEED = 0.15

# Game state
snake = [(GRID_SIZE // 2, GRID_SIZE // 2)]
direction = (1, 0)
food = None
food_type = None
score = 0
food_eaten = 0
game_state = "playing"
last_move_time = 0
game_over_text_x = -800
eat_animation = {'active': False, 'start_time': 0, 'scale': 1.0, 'food_alpha': 255}
game_over_animation = {'active': False, 'start_time': 0, 'alpha': 1.0}

# Initialize pygame
pygame.init()
pygame.mixer.init()
pygame.display.set_mode(WIN_SIZE, DOUBLEBUF | OPENGL)
pygame.display.set_caption("Realistic Snake Game")
gluOrtho2D(0, WIN_SIZE[0], 0, WIN_SIZE[1])
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# Load sound (optional)
try:
    beep = pygame.mixer.Sound("beep.wav")
except:
    beep = None
try:
    game_over_sound = pygame.mixer.Sound("gameover.wav")
except:
    game_over_sound = None

# === Grass Background ===
def generate_grass_texture():
    surf = pygame.Surface((128, 128), pygame.SRCALPHA)
    for x in range(128):
        for y in range(128):
            base_green = 180 + int(20 * math.sin(x / 20.0) * math.cos(y / 20.0))
            base_yellow = 100 + int(20 * math.sin(x / 20.0) * math.cos(y / 20.0))
            surf.set_at((x, y), (base_yellow, base_green, base_yellow // 2, 255))
    for _ in range(1000):
        x = random.randint(0, 127)
        y = random.randint(0, 127)
        height = random.randint(4, 10)
        yellow = random.randint(180, 220)
        green = random.randint(160, 200)
        for dy in range(height):
            if y + dy < 128:
                offset = int(math.sin(dy / height * math.pi) * 2)
                alpha = int(255 * (1 - dy / height))
                surf.set_at((x + offset, y + dy), (yellow, green, yellow // 2, alpha))
    return surf

def draw_background(texture_id):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(0, 0)
    glTexCoord2f(4, 0)
    glVertex2f(WIN_SIZE[0], 0)
    glTexCoord2f(4, 4)
    glVertex2f(WIN_SIZE[0], WIN_SIZE[1])
    glTexCoord2f(0, 4)
    glVertex2f(0, WIN_SIZE[1])
    glEnd()
    glDisable(GL_TEXTURE_2D)

# === Food Textures ===
def generate_apple_texture():
    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
    center = (32, 32)
    for x in range(64):
        for y in range(64):
            dx = x - center[0]
            dy = y - center[1]
            d = math.sqrt(dx ** 2 + dy ** 2)
            if d < 28:
                red = int(180 - d * 2.5)
                green = int(20 - d * 1)
                green = max(0, green)
                light = max(0, (dx - dy) / 28)
                red = min(255, max(0, int(red + light * 60)))
                green = min(255, max(0, int(green + light * 30)))
                alpha = int(255 * (1 - d / 30))
                surf.set_at((x, y), (red, green, 0, alpha))
                if random.random() < 0.02 and d > 10:
                    surf.set_at((x, y), (120, 80, 0, alpha))
                if d < 12 and dx < -8 and dy > 8:
                    surf.set_at((x, y), (220, 220, 220, 140))
    for i in range(10):
        shade = 100 - i * 5
        surf.set_at((31, 4 + i), (shade, shade // 2, shade // 4, 255))
        surf.set_at((32, 4 + i), (shade, shade // 2, shade // 4, 255))
    for x in range(24, 40):
        for y in range(2, 12):
            dx = x - 32
            dy = y - 7
            if math.sqrt(dx ** 2 + dy ** 2) < 6:
                green = 100 + int(20 * math.sin(dx / 3.0))
                alpha = int(255 * (1 - dy / 6))
                alpha = max(0, min(255, alpha))
                surf.set_at((x, y), (20, green, 20, alpha))
                if abs(dx - dy) < 1:
                    surf.set_at((x, y), (10, green - 20, 10, alpha))
    return surf

def generate_banana_texture():
    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
    center = (32, 32)
    for x in range(64):
        for y in range(64):
            dx = x - center[0]
            dy = y - center[1]
            if abs(dx) < 14 and abs(dy - 12 * math.sin(dx / 14)) < 9:
                yellow = int(200 - abs(dx) * 4)
                green = int(60 - abs(dx) * 1.5)
                light = max(0, (dx - dy) / 22)
                yellow = min(255, max(0, int(yellow + light * 50)))
                green = min(255, max(0, int(green + light * 30)))
                alpha = 255
                surf.set_at((x, y), (yellow, green, 0, alpha))
                if random.random() < 0.03 and abs(dx) > 5:
                    surf.set_at((x, y), (100, 50, 10, 200))
                if abs(dx) < 7 and dy > 0 and light > 0.6:
                    surf.set_at((x, y), (220, 220, 200, 130))
    for x in range(18, 22):
        surf.set_at((x, 32), (80, 80, 40, 255))
        surf.set_at((x, 33), (80, 80, 40, 255))
    for x in range(42, 46):
        surf.set_at((x, 32), (80, 80, 40, 255))
        surf.set_at((x, 33), (80, 80, 40, 255))
    return surf

def generate_strawberry_texture():
    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
    center = (32, 32)
    for x in range(64):
        for y in range(64):
            dx = x - center[0]
            dy = y - center[1]
            d = math.sqrt(dx ** 2 + dy ** 2)
            if d < 22 and dy < 12 * math.cos(dx / 12):
                red = int(190 - d * 3.5)
                light = max(0, (dx - dy) / 22)
                red = min(255, max(0, int(red + light * 70)))
                alpha = int(255 * (1 - d / 24))
                surf.set_at((x, y), (red, 0, 0, alpha))
                if (x * y) % 5 < 2 and d > 4:
                    surf.set_at((x, y), (200, 200, 80, 220))
                if d < 10 and dx < -6 and dy > 6:
                    surf.set_at((x, y), (220, 220, 220, 150))
    for x in range(26, 38):
        for y in range(8, 18):
            dx = x - 32
            dy = y - 13
            if math.sqrt(dx ** 2 + dy ** 2) < 5:
                green = 100 + int(20 * math.cos(dx / 2.0))
                alpha = 255
                surf.set_at((x, y), (20, green, 20, alpha))
                if abs(dx) % 2 < 1:
                    surf.set_at((x, y), (10, green - 30, 10, alpha))
    return surf

def generate_mouse_texture():
    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
    center = (32, 32)
    for x in range(64):
        for y in range(64):
            dx = x - center[0]
            dy = y - center[1]
            if abs(dx) < 16 and abs(dy) < 11:
                gray = int(140 - abs(dx) * 2.5)
                light = max(0, (dx - dy) / 22)
                gray = min(255, max(0, int(gray + light * 50)))
                alpha = 255
                surf.set_at((x, y), (gray, gray, gray, alpha))
                if random.random() < 0.05 and abs(dx) > 4:
                    surf.set_at((x, y), (gray - 30, gray - 30, gray - 30, alpha))
                if abs(dx) < 9 and dy > 0 and light > 0.6:
                    surf.set_at((x, y), (220, 220, 220, 110))
    for x in range(29, 31):
        for y in range(19, 21):
            surf.set_at((x, y), (0, 0, 0, 255))
            surf.set_at((x + 4, y), (0, 0, 0, 255))
    for x in range(24, 28):
        surf.set_at((x, 21), (180, 180, 180, 200))
        surf.set_at((x + 8, 21), (180, 180, 180, 200))
    for x in range(48, 56):
        dy = int(2 * math.sin((x - 48) / 2))
        surf.set_at((x, 32 + dy), (80, 80, 80, 255))
    return surf

def generate_paper_texture():
    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
    center = (32, 32)
    for x in range(64):
        for y in range(64):
            dx = x - center[0]
            dy = y - center[1]
            if abs(dx) < 22 and abs(dy) < 22 and math.sin(dx / 4) * math.cos(dy / 4) > -0.6:
                white = int(170 + 20 * math.sin(dx / 2) * math.cos(dy / 2))
                yellow = int(150 + 20 * math.sin(dx / 2) * math.cos(dy / 2))
                alpha = int(255 * (1 - (abs(dx) + abs(dy)) / 44))
                surf.set_at((x, y), (white, yellow, yellow, alpha))
                if abs(dx - dy) < 1.5 and abs(dx) > 4:
                    surf.set_at((x, y), (120, 120, 120, 180))
                if abs(dx) > 18 or abs(dy) > 18:
                    if random.random() < 0.3:
                        surf.set_at((x, y), (white - 20, yellow - 20, yellow - 20, alpha * 0.7))
    return surf

def create_texture(surface):
    data = pygame.image.tostring(surface, "RGBA", True)
    w, h = surface.get_size()
    texid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texid)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    return texid

def draw_food(food_textures):
    if food is None or food_type is None:
        return
    fx, fy = food
    x = fx * CELL_SIZE
    y = fy * CELL_SIZE
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, food_textures[food_type])
    glColor4f(1, 1, 1, eat_animation['food_alpha'] / 255.0 if eat_animation['active'] else 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(x, y)
    glTexCoord2f(1, 0)
    glVertex2f(x + CELL_SIZE, y)
    glTexCoord2f(1, 1)
    glVertex2f(x + CELL_SIZE, y + CELL_SIZE)
    glTexCoord2f(0, 1)
    glVertex2f(x, y + CELL_SIZE)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def draw_circle(x, y, r, color, alpha=1.0):
    glColor4f(color[0], color[1], color[2], alpha)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for angle in range(0, 361, 5):
        rad = math.radians(angle)
        glVertex2f(x + r * math.cos(rad), y + r * math.sin(rad))
    glEnd()

def draw_snake():
    now = time.time()
    for i, segment in enumerate(snake):
        cx = segment[0] * CELL_SIZE + CELL_SIZE / 2
        cy = segment[1] * CELL_SIZE + CELL_SIZE / 2
        dx, dy = direction
        eye_offset_x = -dy * 4
        eye_offset_y = dx * 4
        alpha = game_over_animation['alpha'] if game_over_animation['active'] else 1.0
        shake_offset = 0
        if game_over_animation['active']:
            t = now - game_over_animation['start_time']
            shake_offset = 3 * math.sin(t * 10) * max(0, 1 - t / 2)
            cx += shake_offset
        tail_offset = 0
        if i == len(snake) - 1 and game_state == "playing":
            tail_offset = 2 * math.sin(now * 5)
            cx += tail_offset
        if i == 0:
            scale = eat_animation['scale'] if eat_animation['active'] else 1.0
            draw_circle(cx, cy, (CELL_SIZE / 2 - 1) * scale, (0, 0.5, 0.1), alpha)
            draw_circle(cx + 2, cy - 2, (CELL_SIZE / 4) * scale, (0.3, 0.8, 0.3), alpha)
            draw_circle(cx + eye_offset_x - 4, cy + eye_offset_y + 3, 2.5 * scale, (1, 1, 1), alpha)
            draw_circle(cx + eye_offset_x + 4, cy + eye_offset_y + 3, 2.5 * scale, (1, 1, 1), alpha)
            draw_circle(cx + eye_offset_x - 4, cy + eye_offset_y + 3, 1.2 * scale, (0, 0, 0), alpha)
            draw_circle(cx + eye_offset_x + 4, cy + eye_offset_y + 3, 1.2 * scale, (0, 0, 0), alpha)
            if not eat_animation['active']:
                glBegin(GL_LINES)
                glColor4f(0.8, 0, 0, alpha)
                glVertex2f(cx + dx * 8, cy + dy * 8)
                glVertex2f(cx + dx * 12, cy + dy * 12)
                glEnd()
        elif i == len(snake) - 1:
            draw_circle(cx, cy, (CELL_SIZE / 2 - 4), (0, 0.3, 0.05), alpha)
        else:
            base_color = (0, 0.6, 0.1)
            if i % 3 == 0:
                base_color = (0.6, 0.6, 0)
            draw_circle(cx, cy, (CELL_SIZE / 2 - 2), base_color, alpha)
            draw_circle(cx + 1, cy + 1, CELL_SIZE / 8, (0.7, 0.7, 0.3), alpha * 0.7)
            draw_circle(cx - 1, cy - 1, CELL_SIZE / 10, (0.5, 0.8, 0.5), alpha * 0.6)

def move_snake():
    global food, score, game_state, eat_animation, food_type, food_eaten
    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    
    if head[0] < 0 or head[0] >= GRID_SIZE or head[1] < 0 or head[1] >= GRID_SIZE or head in snake:
        game_state = "game_over"
        food = None
        food_type = None
        if game_over_sound:
            game_over_sound.play()
        game_over_animation['active'] = True
        game_over_animation['start_time'] = time.time()
        return

    snake.insert(0, head)
    if head == food:
        points = 20 if food_type == 'paper' else 10
        score += points
        food_eaten += 1
        if food_eaten >= 50:
            game_state = "game_over"
            food = None
            food_type = None
            if game_over_sound:
                game_over_sound.play()
            game_over_animation['active'] = True
            game_over_animation['start_time'] = time.time()
            return
        if beep:
            beep.play()
        eat_animation['active'] = True
        eat_animation['start_time'] = time.time()
        eat_animation['scale'] = 1.2
        eat_animation['food_alpha'] = 255
        food = None
        food_type = None
        manage_food()
    else:
        snake.pop()

def manage_food():
    global food, food_type
    possible_positions = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE) if (x, y) not in snake]
    if not possible_positions:
        return
    food = random.choice(possible_positions)
    food_type = 'paper' if random.random() < 0.2 else random.choice(['apple', 'banana', 'strawberry', 'mouse'])

def restart_game():
    global snake, direction, food, food_type, score, game_state, last_move_time, game_over_text_x, eat_animation, game_over_animation, food_eaten
    snake = [(GRID_SIZE // 2, GRID_SIZE // 2)]
    direction = (1, 0)
    food = None
    food_type = None
    score = 0
    food_eaten = 0
    game_state = "playing"
    last_move_time = 0
    game_over_text_x = -800
    eat_animation = {'active': False, 'start_time': 0, 'scale': 1.0, 'food_alpha': 255}
    game_over_animation = {'active': False, 'start_time': 0, 'alpha': 1.0}
    manage_food()

def main():
    global direction, game_over_text_x, eat_animation, game_over_animation, food_type, food, last_move_time
    clock = pygame.time.Clock()
    food_textures = {
        'apple': create_texture(generate_apple_texture()),
        'banana': create_texture(generate_banana_texture()),
        'strawberry': create_texture(generate_strawberry_texture()),
        'mouse': create_texture(generate_mouse_texture()),
        'paper': create_texture(generate_paper_texture())
    }
    grass_tex = create_texture(generate_grass_texture())
    manage_food()

    running = True
    while running:
        now = time.time()
        glClear(GL_COLOR_BUFFER_BIT)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_UP and direction != (0, -1):
                    direction = (0, 1)
                elif event.key == K_DOWN and direction != (0, 1):
                    direction = (0, -1)
                elif event.key == K_LEFT and direction != (1, 0):
                    direction = (-1, 0)
                elif event.key == K_RIGHT and direction != (-1, 0):
                    direction = (1, 0)
                elif event.key == K_RETURN and game_state == "game_over":
                    restart_game()
                elif event.key == K_q and game_state == "game_over":
                    running = False

        if game_state == "playing":
            if now - last_move_time > SPEED:
                move_snake()
                last_move_time = now
            if eat_animation['active']:
                t = now - eat_animation['start_time']
                if t < 0.5:
                    eat_animation['scale'] = 1.2 - 0.4 * (t / 0.5)
                    eat_animation['food_alpha'] = 255 * (1 - t / 0.5)
                else:
                    eat_animation['active'] = False
                    eat_animation['scale'] = 1.0
                    eat_animation['food_alpha'] = 255
            if food is None and food_eaten < 50:
                manage_food()
        elif game_state == "game_over":
            game_over_text_x += 5
            if game_over_text_x > WIN_SIZE[0]:
                game_over_text_x = -800
            if game_over_animation['active']:
                t = now - game_over_animation['start_time']
                if t < 2:
                    game_over_animation['alpha'] = 1 - t / 2
                else:
                    game_over_animation['alpha'] = 0

        draw_background(grass_tex)
        draw_snake()
        draw_food(food_textures)

        # Draw food eaten counter
        font = pygame.font.SysFont('Arial', 24)
        counter_text = font.render(f"Food Eaten: {food_eaten}/50", True, (255, 255, 255))
        tex_id = create_texture(counter_text)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glColor4f(1, 1, 1, 1)
        text_width, text_height = counter_text.get_size()
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex2f(10, WIN_SIZE[1] - text_height - 10)
        glTexCoord2f(1, 0)
        glVertex2f(10 + text_width, WIN_SIZE[1] - text_height - 10)
        glTexCoord2f(1, 1)
        glVertex2f(10 + text_width, WIN_SIZE[1] - 10)
        glTexCoord2f(0, 1)
        glVertex2f(10, WIN_SIZE[1] - 10)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glDeleteTextures([tex_id])

        if game_state == "game_over":
            font = pygame.font.SysFont('Arial', 36)
            game_over_text = font.render("Game Over! Press Enter to Restart or Q to Quit", True, (255, 147, 0))
            tex_id = create_texture(game_over_text)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glColor4f(1, 1, 1, 1)
            text_width, text_height = game_over_text.get_size()
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0)
            glVertex2f(game_over_text_x, WIN_SIZE[1] // 3)
            glTexCoord2f(1, 0)
            glVertex2f(game_over_text_x + text_width, WIN_SIZE[1] // 3)
            glTexCoord2f(1, 1)
            glVertex2f(game_over_text_x + text_width, WIN_SIZE[1] // 3 + text_height)
            glTexCoord2f(0, 1)
            glVertex2f(game_over_text_x, WIN_SIZE[1] // 3 + text_height)
            glEnd()
            glDisable(GL_TEXTURE_2D)
            glDeleteTextures([tex_id])

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()