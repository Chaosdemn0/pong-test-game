"""Minimal pygame-ce presentation for the Pong rules."""
from __future__ import annotations

import argparse
import os


def configure_pygame(headless: bool):
    if headless:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    import pygame
    return pygame


def axis(pressed, negative, positive) -> int:
    return int(pressed[positive]) - int(pressed[negative])


def run(headless: bool = False, smoke_frames: int | None = None) -> None:
    pygame = configure_pygame(headless)
    from game_logic import HEIGHT, PADDLE_WIDTH, WIDTH, MatchState

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong")
    title_font = pygame.font.Font(None, 64)
    score_font = pygame.font.Font(None, 56)
    text_font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()
    state = None
    screen_name = "menu"
    frames = 0
    running = True

    def draw_centered(text, font, y):
        image = font.render(text, True, "white")
        screen.blit(image, image.get_rect(center=(WIDTH / 2, y)))

    while running:
        seconds = min(clock.tick(120) / 1000, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif screen_name == "menu" and event.key in (pygame.K_1, pygame.K_2):
                    state = MatchState("solo" if event.key == pygame.K_1 else "local")
                    screen_name = "play"
                elif screen_name == "winner" and event.key == pygame.K_SPACE:
                    state = None
                    screen_name = "menu"

        screen.fill("black")
        if screen_name == "menu":
            draw_centered("PONG", title_font, 155)
            draw_centered("1 — Solo vs AI", text_font, 275)
            draw_centered("2 — Two local players", text_font, 320)
            draw_centered("Left paddle: W / S     Right paddle: Up / Down", text_font, 410)
            draw_centered("First to 7 wins · Escape exits", text_font, 450)
        elif screen_name == "play" and state:
            pressed = pygame.key.get_pressed()
            scorer = state.step(
                seconds,
                axis(pressed, pygame.K_w, pygame.K_s),
                axis(pressed, pygame.K_UP, pygame.K_DOWN),
            )
            if scorer and state.winner:
                screen_name = "winner"
            pygame.draw.line(screen, "white", (WIDTH / 2, 0), (WIDTH / 2, HEIGHT), 2)
            for paddle in (state.left, state.right):
                pygame.draw.rect(screen, "white", (round(paddle.x), round(paddle.y), PADDLE_WIDTH, paddle.height))
            pygame.draw.circle(screen, "white", (round(state.ball.x), round(state.ball.y)), state.ball.radius)
            draw_centered(f"{state.left_score}     {state.right_score}", score_font, 48)
        elif screen_name == "winner" and state and state.winner:
            draw_centered(f"{state.winner.title()} player wins", title_font, 220)
            draw_centered("Press Space to return to the menu", text_font, 320)

        pygame.display.flip()
        frames += 1
        if smoke_frames and frames >= smoke_frames:
            assert screen.get_at((0, 0))[:3] == (0, 0, 0)
            print(f"PASS: rendered {frames} frames using {pygame.display.get_driver()}")
            running = False
    pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    arguments = parser.parse_args()
    run(headless=arguments.headless, smoke_frames=10 if arguments.smoke else None)
