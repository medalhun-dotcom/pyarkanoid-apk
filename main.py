import pygame
import random
import math

pygame.init()

# Teljes képernyő (fekvő tájoláshoz igazítva)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("PyArkanoid Android")
clock = pygame.time.Clock()
FPS = 60

# Színek
BG_COLOR = (14, 16, 24)
PADDLE_COLOR = (70, 190, 255)
PADDLE_LASER_COLOR = (255, 85, 85)
BALL_COLOR = (255, 255, 255)
TEXT_COLOR = (230, 230, 240)
LASER_COLOR = (255, 60, 60)

ROW_COLORS = [
    (235, 64, 52),
    (245, 130, 48),
    (245, 215, 66),
    (75, 200, 110),
    (66, 135, 245),
    (165, 95, 235)
]

# Képernyőhöz arányosított méretek
BASE_PADDLE_W = int(WIDTH * 0.14)
WIDE_PADDLE_W = int(WIDTH * 0.22)
PADDLE_H = max(18, int(HEIGHT * 0.03))

BALL_RADIUS = max(9, int(HEIGHT * 0.015))
BALL_BASE_SPEED = max(6.0, HEIGHT * 0.009)

ROWS = 6
COLS = 11
BRICK_GAP = max(6, int(WIDTH * 0.006))
SIDE_MARGIN = int(WIDTH * 0.04)
BRICK_W = (WIDTH - 2 * SIDE_MARGIN - (COLS - 1) * BRICK_GAP) // COLS
BRICK_H = max(24, int(HEIGHT * 0.042))
TOP_OFFSET = int(HEIGHT * 0.11)

# Android-kompatibilis alapértelmezett betűtípusok
font_hud = pygame.font.Font(None, max(28, int(HEIGHT * 0.042)))
font_icon = pygame.font.Font(None, max(24, int(HEIGHT * 0.034)))
font_big = pygame.font.Font(None, max(64, int(HEIGHT * 0.11)))

POWERUP_TYPES = [
    {"type": "WIDE",  "icon": "W",  "color": (50, 160, 255)},
    {"type": "MULTI", "icon": "M",  "color": (60, 210, 100)},
    {"type": "LASER", "icon": "L",  "color": (240, 65, 65)},
    {"type": "LIFE",  "icon": "+1", "color": (245, 200, 50)},
]


def create_bricks():
    bricks = []
    for row in range(ROWS):
        for col in range(COLS):
            x = SIDE_MARGIN + col * (BRICK_W + BRICK_GAP)
            y = TOP_OFFSET + row * (BRICK_H + BRICK_GAP)
            rect = pygame.Rect(x, y, BRICK_W, BRICK_H)
            points = (ROWS - row) * 10
            bricks.append({
                "rect": rect,
                "color": ROW_COLORS[row % len(ROW_COLORS)],
                "points": points,
                "has_powerup": random.random() < 0.28
            })
    return bricks


def spawn_ball(x, y, speed=BALL_BASE_SPEED):
    angle = random.uniform(-math.pi / 4, math.pi / 4)
    return {
        "x": float(x),
        "y": float(y),
        "vx": speed * math.sin(angle),
        "vy": -speed * math.cos(angle)
    }


def draw_powerup_capsule(surface, p):
    rect = p["rect"]
    pygame.draw.rect(surface, p["color"], rect, border_radius=rect.height // 2)
    pygame.draw.rect(surface, (255, 255, 255), rect, width=2, border_radius=rect.height // 2)
    icon_surf = font_icon.render(p["icon"], True, (15, 15, 20))
    surface.blit(icon_surf, icon_surf.get_rect(center=rect.center))


def main():
    paddle = pygame.Rect((WIDTH - BASE_PADDLE_W) // 2, HEIGHT - int(HEIGHT * 0.09), BASE_PADDLE_W, PADDLE_H)
    bricks = create_bricks()
    balls = [spawn_ball(paddle.centerx, paddle.top - BALL_RADIUS - 4)]
    powerups = []
    lasers = []

    score = 0
    lives = 3
    game_state = "PLAYING"

    wide_until = 0
    laser_until = 0
    last_shot_time = 0

    running = True
    while running:
        clock.tick(FPS)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Android vissza gomb vagy ESC
                if event.key in (pygame.K_ESCAPE, getattr(pygame, "K_AC_BACK", 1073742094)):
                    running = False

            # Érintőképernyő kezelése (ujj lenyomása és húzása)
            elif event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION):
                touch_x = int(event.x * WIDTH)
                if game_state == "PLAYING":
                    paddle.centerx = touch_x
                elif event.type == pygame.FINGERDOWN and game_state != "PLAYING":
                    # Koppintásra újrakezdés
                    paddle.width = BASE_PADDLE_W
                    paddle.centerx = WIDTH // 2
                    bricks = create_bricks()
                    balls = [spawn_ball(paddle.centerx, paddle.top - BALL_RADIUS - 4)]
                    powerups.clear()
                    lasers.clear()
                    score = 0
                    lives = 3
                    wide_until = 0
                    laser_until = 0
                    game_state = "PLAYING"

            # Egér emuláció (ha asztali gépen teszteled)
            elif event.type == pygame.MOUSEMOTION and game_state == "PLAYING":
                paddle.centerx = event.pos[0]
            elif event.type == pygame.MOUSEBUTTONDOWN and game_state != "PLAYING":
                paddle.width = BASE_PADDLE_W
                paddle.centerx = WIDTH // 2
                bricks = create_bricks()
                balls = [spawn_ball(paddle.centerx, paddle.top - BALL_RADIUS - 4)]
                powerups.clear()
                lasers.clear()
                score = 0
                lives = 3
                wide_until = 0
                laser_until = 0
                game_state = "PLAYING"

        if game_state == "PLAYING":
            target_w = WIDE_PADDLE_W if now < wide_until else BASE_PADDLE_W
            if paddle.width != target_w:
                center = paddle.centerx
                paddle.width = target_w
                paddle.centerx = center

            paddle.clamp_ip(screen.get_rect())

            # Lézer módban automatikus tüzelés mobilon (kényelmesebb egy kézzel)
            if now < laser_until and now - last_shot_time > 320:
                last_shot_time = now
                lasers.append(pygame.Rect(paddle.left + 8, paddle.top - 18, 5, 18))
                lasers.append(pygame.Rect(paddle.right - 13, paddle.top - 18, 5, 18))

            # Lézersugarak
            laser_speed = max(12, int(HEIGHT * 0.02))
            for laser in lasers[:]:
                laser.y -= laser_speed
                if laser.bottom < 0:
                    lasers.remove(laser)
                    continue
                for brick in bricks[:]:
                    if laser.colliderect(brick["rect"]):
                        score += brick["points"]
                        if brick["has_powerup"]:
                            ptype = random.choice(POWERUP_TYPES)
                            cap_w, cap_h = max(52, int(WIDTH * 0.045)), max(28, int(HEIGHT * 0.04))
                            cap_rect = pygame.Rect(0, 0, cap_w, cap_h)
                            cap_rect.center = brick["rect"].center
                            powerups.append({**ptype, "rect": cap_rect})
                        bricks.remove(brick)
                        if laser in lasers:
                            lasers.remove(laser)
                        break

            # Bónusz kapszulák
            fall_speed = max(4, int(HEIGHT * 0.006))
            for p in powerups[:]:
                p["rect"].y += fall_speed
                if p["rect"].colliderect(paddle):
                    if p["type"] == "WIDE":
                        wide_until = now + 15000
                    elif p["type"] == "LASER":
                        laser_until = now + 12000
                    elif p["type"] == "LIFE":
                        lives += 1
                    elif p["type"] == "MULTI":
                        new_balls = []
                        for b in balls[:3]:
                            spd = math.hypot(b["vx"], b["vy"])
                            new_balls.append(spawn_ball(b["x"], b["y"], spd))
                            new_balls.append(spawn_ball(b["x"], b["y"], spd))
                        balls.extend(new_balls)
                    powerups.remove(p)
                elif p["rect"].top > HEIGHT:
                    powerups.remove(p)

            # Labdák
            for b in balls[:]:
                b["x"] += b["vx"]
                ball_rect = pygame.Rect(
                    int(b["x"] - BALL_RADIUS),
                    int(b["y"] - BALL_RADIUS),
                    BALL_RADIUS * 2,
                    BALL_RADIUS * 2
                )

                if ball_rect.left <= 0:
                    ball_rect.left = 0
                    b["x"] = float(ball_rect.centerx)
                    b["vx"] *= -1
                elif ball_rect.right >= WIDTH:
                    ball_rect.right = WIDTH
                    b["x"] = float(ball_rect.centerx)
                    b["vx"] *= -1

                for brick in bricks[:]:
                    if ball_rect.colliderect(brick["rect"]):
                        b["vx"] *= -1
                        score += brick["points"]
                        if brick["has_powerup"]:
                            ptype = random.choice(POWERUP_TYPES)
                            cap_w, cap_h = max(52, int(WIDTH * 0.045)), max(28, int(HEIGHT * 0.04))
                            cap_rect = pygame.Rect(0, 0, cap_w, cap_h)
                            cap_rect.center = brick["rect"].center
                            powerups.append({**ptype, "rect": cap_rect})
                        bricks.remove(brick)
                        break

                b["y"] += b["vy"]
                ball_rect.centery = int(b["y"])

                if ball_rect.top <= 0:
                    ball_rect.top = 0
                    b["y"] = float(ball_rect.centery)
                    b["vy"] *= -1

                for brick in bricks[:]:
                    if ball_rect.colliderect(brick["rect"]):
                        b["vy"] *= -1
                        score += brick["points"]
                        if brick["has_powerup"]:
                            ptype = random.choice(POWERUP_TYPES)
                            cap_w, cap_h = max(52, int(WIDTH * 0.045)), max(28, int(HEIGHT * 0.04))
                            cap_rect = pygame.Rect(0, 0, cap_w, cap_h)
                            cap_rect.center = brick["rect"].center
                            powerups.append({**ptype, "rect": cap_rect})
                        bricks.remove(brick)
                        break

                if ball_rect.colliderect(paddle) and b["vy"] > 0:
                    offset = (ball_rect.centerx - paddle.centerx) / (paddle.width / 2)
                    offset = max(-1.0, min(1.0, offset))
                    bounce_angle = offset * (math.pi / 3)
                    current_speed = min(math.hypot(b["vx"], b["vy"]) * 1.01, BALL_BASE_SPEED * 1.75)
                    b["vx"] = current_speed * math.sin(bounce_angle)
                    b["vy"] = -current_speed * math.cos(bounce_angle)
                    b["y"] = float(paddle.top - BALL_RADIUS)

                if ball_rect.top > HEIGHT:
                    balls.remove(b)

            if not balls:
                lives -= 1
                wide_until = 0
                laser_until = 0
                powerups.clear()
                lasers.clear()
                if lives <= 0:
                    game_state = "GAME_OVER"
                else:
                    paddle.width = BASE_PADDLE_W
                    balls = [spawn_ball(paddle.centerx, paddle.top - BALL_RADIUS - 4)]

            if not bricks:
                game_state = "WIN"

        # Kirajzolás
        screen.fill(BG_COLOR)

        for brick in bricks:
            pygame.draw.rect(screen, brick["color"], brick["rect"], border_radius=5)
            if brick["has_powerup"]:
                dot_rect = pygame.Rect(0, 0, 7, 7)
                dot_rect.center = brick["rect"].center
                pygame.draw.rect(screen, (255, 255, 255), dot_rect, border_radius=3)

        for p in powerups:
            draw_powerup_capsule(screen, p)

        for laser in lasers:
            pygame.draw.rect(screen, LASER_COLOR, laser, border_radius=2)

        p_color = PADDLE_LASER_COLOR if now < laser_until else PADDLE_COLOR
        pygame.draw.rect(screen, p_color, paddle, border_radius=8)
        if now < laser_until:
            pygame.draw.rect(screen, (255, 220, 220), (paddle.left + 6, paddle.top - 6, 8, 8), border_radius=2)
            pygame.draw.rect(screen, (255, 220, 220), (paddle.right - 14, paddle.top - 6, 8, 8), border_radius=2)

        for b in balls:
            pygame.draw.circle(screen, BALL_COLOR, (int(b["x"]), int(b["y"])), BALL_RADIUS)

        status_parts = [f"PONT: {score}", f"ÉLET: {lives}"]
        if now < wide_until:
            status_parts.append(f"[SZÉLES: {(wide_until - now)//1000 + 1}s]")
        if now < laser_until:
            status_parts.append(f"[LÉZER: {(laser_until - now)//1000 + 1}s]")

        hud_text = font_hud.render("    ".join(status_parts), True, TEXT_COLOR)
        screen.blit(hud_text, (SIDE_MARGIN, int(HEIGHT * 0.03)))

        if game_state in ("GAME_OVER", "WIN"):
            msg = "GYŐZELEM!" if game_state == "WIN" else "JÁTÉK VÉGE"
            color = (75, 220, 120) if game_state == "WIN" else (235, 70, 70)
            title_surf = font_big.render(msg, True, color)
            sub_surf = font_hud.render("Érintsd meg a képernyőt az újrakezdéshez", True, TEXT_COLOR)
            screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 35)))
            screen.blit(sub_surf, sub_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 35)))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()