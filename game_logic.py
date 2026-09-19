"""Framework-independent rules and collision handling for Pong."""
from __future__ import annotations

from dataclasses import dataclass, field
from math import cos, radians, sin
from typing import Literal

WIDTH, HEIGHT = 960, 540
PADDLE_WIDTH, PADDLE_HEIGHT = 18, 100
PADDLE_MARGIN = 32
BALL_RADIUS = 10
PADDLE_SPEED = 420.0
AI_SPEED = 310.0
BASE_BALL_SPEED = 380.0
BALL_SPEED_STEP = 30.0
MAX_BALL_SPEED = 720.0
MAX_BOUNCE_ANGLE = radians(60)
WINNING_SCORE = 7

Side = Literal["left", "right"]
Mode = Literal["solo", "local"]


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


@dataclass
class Paddle:
    x: float
    y: float
    width: int = PADDLE_WIDTH
    height: int = PADDLE_HEIGHT

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2

    def move(self, direction: int, seconds: float, speed: float = PADDLE_SPEED) -> None:
        self.y = clamp(self.y + direction * speed * seconds, 0, HEIGHT - self.height)


@dataclass
class Ball:
    x: float = WIDTH / 2
    y: float = HEIGHT / 2
    vx: float = BASE_BALL_SPEED
    vy: float = BASE_BALL_SPEED * 0.25
    radius: int = BALL_RADIUS
    speed: float = BASE_BALL_SPEED

    def reset(self, toward: Side, serve_number: int) -> None:
        direction = -1 if toward == "left" else 1
        vertical_direction = -1 if serve_number % 2 else 1
        self.x, self.y = WIDTH / 2, HEIGHT / 2
        self.speed = BASE_BALL_SPEED
        self.vx = direction * self.speed
        self.vy = vertical_direction * self.speed * 0.25


@dataclass
class MatchState:
    mode: Mode
    left: Paddle = field(default_factory=lambda: Paddle(PADDLE_MARGIN, (HEIGHT - PADDLE_HEIGHT) / 2))
    right: Paddle = field(default_factory=lambda: Paddle(WIDTH - PADDLE_MARGIN - PADDLE_WIDTH, (HEIGHT - PADDLE_HEIGHT) / 2))
    ball: Ball = field(default_factory=Ball)
    left_score: int = 0
    right_score: int = 0
    winner: Side | None = None
    serve_number: int = 0
    last_event: str | None = None

    def reset_round(self, toward: Side) -> None:
        self.left.y = self.right.y = (HEIGHT - PADDLE_HEIGHT) / 2
        self.serve_number += 1
        self.ball.reset(toward, self.serve_number)

    def update_ai(self, seconds: float) -> None:
        if self.ball.vx <= 0:
            return
        direction = 1 if self.ball.y > self.right.center_y else -1 if self.ball.y < self.right.center_y else 0
        self.right.move(direction, seconds, AI_SPEED)

    def step(self, seconds: float, left_direction: int, right_direction: int = 0) -> Side | None:
        if self.winner:
            return None
        self.left.move(left_direction, seconds)
        if self.mode == "solo":
            self.update_ai(seconds)
        else:
            self.right.move(right_direction, seconds)

        self.ball.x += self.ball.vx * seconds
        self.ball.y += self.ball.vy * seconds
        self._bounce_off_walls()
        self._bounce_off_paddles()
        return self._score_if_needed()

    def _bounce_off_walls(self) -> None:
        if self.ball.y - self.ball.radius < 0:
            self.ball.y = self.ball.radius
            self.ball.vy = abs(self.ball.vy)
            self.last_event = "wall"
        elif self.ball.y + self.ball.radius > HEIGHT:
            self.ball.y = HEIGHT - self.ball.radius
            self.ball.vy = -abs(self.ball.vy)
            self.last_event = "wall"

    def _intersects(self, paddle: Paddle) -> bool:
        return (
            self.ball.x + self.ball.radius >= paddle.x
            and self.ball.x - self.ball.radius <= paddle.x + paddle.width
            and self.ball.y + self.ball.radius >= paddle.y
            and self.ball.y - self.ball.radius <= paddle.y + paddle.height
        )

    def _bounce_from_paddle(self, paddle: Paddle, direction: int) -> None:
        relative_hit = clamp((self.ball.y - paddle.center_y) / (paddle.height / 2), -1, 1)
        angle = relative_hit * MAX_BOUNCE_ANGLE
        self.ball.speed = min(self.ball.speed + BALL_SPEED_STEP, MAX_BALL_SPEED)
        self.ball.vx = direction * cos(angle) * self.ball.speed
        self.ball.vy = sin(angle) * self.ball.speed
        self.last_event = "paddle"
        if direction > 0:
            self.ball.x = paddle.x + paddle.width + self.ball.radius
        else:
            self.ball.x = paddle.x - self.ball.radius

    def _bounce_off_paddles(self) -> None:
        if self.ball.vx < 0 and self._intersects(self.left):
            self._bounce_from_paddle(self.left, 1)
        elif self.ball.vx > 0 and self._intersects(self.right):
            self._bounce_from_paddle(self.right, -1)

    def _score_if_needed(self) -> Side | None:
        scorer: Side | None = None
        if self.ball.x + self.ball.radius < 0:
            self.right_score += 1
            scorer = "right"
        elif self.ball.x - self.ball.radius > WIDTH:
            self.left_score += 1
            scorer = "left"
        if scorer:
            self.last_event = "score"
            if (self.left_score if scorer == "left" else self.right_score) >= WINNING_SCORE:
                self.winner = scorer
            else:
                self.reset_round("right" if scorer == "left" else "left")
        return scorer
