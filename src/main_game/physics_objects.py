import random
from dataclasses import dataclass

import pymunk
import pymunk.pygame_util
from pygame.locals import *

from main_game.globals import (BALL_ELASTICITY, BALL_FRICTION, BALL_MASS,
                               BALL_RADIUS, FLAG_WIDTH, FLAT_POLE_HEIGHT,
                               WebcamInfo, level_data, physics_space,
                               screen_height, screen_REL_to_screen_POS_xy)


def is_touching_flag(flag, balls):
  if flag is None:
    return False
  for ball in balls:
    ball_shape, _ = ball
    flag_shape, _ = flag
    if len(flag_shape.shapes_collide(ball_shape).points) > 0:
      return True
  return False

def add_remove_balls(balls, current_level):
  if level_data[current_level]["spawn_balls"]:
    # Add new balls to the game randomly
    if random.random() < 0.01:
        balls.append(add_physics_ball((0.11, 0.05)))

  balls = remove_dead_balls(balls)
  return balls

def remove_dead_balls(balls):
  new_balls = []

  for ball in balls:
    _, ball_body = ball
    if ball_body.position.y > screen_height * 1.1:
      physics_space.remove(*ball)
    else:
      new_balls.append(ball)

  return new_balls

def add_physics_lines_from_position_list(positions):
  lines = []
  for line_pos in positions:
    start_position = line_pos["start_pos"]  # Anna was here
    end_position = line_pos["end_pos"]
    lines.append(add_physics_line(start_position, end_position))
  return lines

def add_physics_ellipse(pos, width, height, num_segments=50):
  body = pymunk.Body(body_type=pymunk.Body.STATIC)

  vertices = []
  for i in range(num_segments):
    angle = 2.0 * 3.1415 * i / num_segments
    x = pos[0] + width * 0.5 * pymunk.vec2d.Vec2d(0, 1).rotated(angle).x
    y = pos[1] + height * 0.5 * pymunk.vec2d.Vec2d(0, 1).rotated(angle).y
    vertices.append((x, y))
  shape = pymunk.Poly(body, vertices, radius=1)
  physics_space.add(body, shape)
  return shape, body


def add_physics_flag(position):
  body = pymunk.Body(body_type=pymunk.Body.STATIC)

  screen_position_x, screen_position_y = screen_REL_to_screen_POS_xy(position)

  # shape = pymunk.Poly(body, [(screen_position_x, screen_position_y), (screen_position_x + FLAG_WIDTH, screen_position_y), (screen_position_x,
  #                     screen_position_y - FLAG_WIDTH - FLAT_POLE_HEIGHT), (screen_position_x + FLAG_WIDTH, screen_position_y - FLAG_WIDTH - FLAT_POLE_HEIGHT)])
  shape = pymunk.Segment(body, (screen_position_x, screen_position_y), (screen_position_x, screen_position_y - FLAG_WIDTH - FLAT_POLE_HEIGHT), 1)

  shape.elasticity = 0.0
  shape.friction = 0.0

  physics_space.add(body, shape)

  return shape, body

def add_physics_ball(position):

  inertia = pymunk.moment_for_circle(BALL_MASS, 0, BALL_RADIUS, (0, 0))

  body = pymunk.Body(BALL_MASS, inertia)
  body.position = screen_REL_to_screen_POS_xy(position)

  shape = pymunk.Circle(body, BALL_RADIUS)
  shape.elasticity = BALL_ELASTICITY
  shape.friction = BALL_FRICTION

  physics_space.add(body, shape)

  return shape, body


def add_physics_line(start_position, end_position):
  body = pymunk.Body(body_type=pymunk.Body.STATIC)

  shape = pymunk.Segment(body, screen_REL_to_screen_POS_xy(start_position), screen_REL_to_screen_POS_xy(end_position), radius=1)

  shape.elasticity = 0.0
  shape.friction = 0.0

  physics_space.add(body, shape)

  return shape, body