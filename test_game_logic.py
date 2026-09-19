import math

import pytest

from game_logic import (
    AI_SPEED,
    BALL_RADIUS,
    BALL_SPEED_STEP,
    HEIGHT,
    MAX_BALL_SPEED,
    PADDLE_HEIGHT,
    WIDTH,
    MatchState,
    Paddle,
)


def test_paddle_is_clamped_to_the_playfield():
    paddle = Paddle(0, 20)
    paddle.move(-1, 1)
    assert paddle.y == 0
    paddle.move(1, 10)
    assert paddle.y == HEIGHT - PADDLE_HEIGHT


@pytest.mark.parametrize(("ball_x", "expected"), [(-BALL_RADIUS - 1, "right"), (WIDTH + BALL_RADIUS + 1, "left")])
def test_score_is_awarded_when_ball_leaves_the_field(ball_x, expected):
    state = MatchState("local")
    state.ball.x = ball_x
    assert state._score_if_needed() == expected
    assert (state.right_score if expected == "right" else state.left_score) == 1


def test_serve_moves_toward_the_player_who_lost_the_point():
    state = MatchState("local")
    state.ball.x = -BALL_RADIUS - 1
    state._score_if_needed()
    assert state.ball.vx < 0  # Left missed, so the ball serves toward left.


def test_paddle_hit_changes_direction_angle_and_speed():
    state = MatchState("local")
    state.ball.x = state.left.x + state.left.width + BALL_RADIUS
    state.ball.y = state.left.y
    state.ball.vx = -state.ball.speed
    previous_speed = state.ball.speed
    state._bounce_off_paddles()
    assert state.ball.vx > 0
    assert state.ball.vy < 0
    assert state.ball.speed == previous_speed + BALL_SPEED_STEP


def test_ball_speed_has_a_cap():
    state = MatchState("local")
    state.ball.speed = MAX_BALL_SPEED
    state._bounce_from_paddle(state.left, 1)
    assert state.ball.speed == MAX_BALL_SPEED


def test_ai_moves_only_toward_an_approaching_ball_and_is_capped():
    state = MatchState("solo")
    initial_y = state.right.y
    state.ball.vx = -1
    state.update_ai(1)
    assert state.right.y == initial_y
    state.ball.vx = 1
    state.ball.y = HEIGHT
    state.update_ai(1)
    assert state.right.y == HEIGHT - PADDLE_HEIGHT
    assert state.right.y - initial_y <= AI_SPEED + PADDLE_HEIGHT
