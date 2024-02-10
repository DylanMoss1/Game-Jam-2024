import pygame
from pygame.locals import *
import pymunk
import pymunk.pygame_util
import random


# --- Initialise PyGame (Rendering Engine) ---

pygame.init()
render_clock = pygame.time.Clock()

render_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

render_font = pygame.font.SysFont(None, 48)


# --- Initialise PyMunk (Physics Engine) ---

physics_space = pymunk.Space()
physics_space.gravity = (0.0, 900.0)


# --- Add Objects To Scene ---

BALL_MASS = 1
BALL_RADIUS = 14
BALL_ELASTICITY = 1.0
BALL_FRICTION = 1.0


def add_ball(physics_space, position) -> pymunk.Circle:

  inertia = pymunk.moment_for_circle(BALL_MASS, 0, BALL_RADIUS, (0, 0))

  body = pymunk.Body(BALL_MASS, inertia)
  body.position = position

  shape = pymunk.Circle(body, BALL_RADIUS)
  shape.elasticity = BALL_ELASTICITY
  shape.friction = BALL_FRICTION

  physics_space.add(body, shape)

  return shape


def add_line(physics_space, start_position, end_position) -> pymunk.Segment:
  body = pymunk.Body(body_type=pymunk.Body.STATIC)

  shape = pymunk.Segment(body, start_position, end_position, radius=1)

  shape.elasticity = 0.0
  shape.friction = 0.0

  physics_space.add(body, shape)

  return shape


def add_lines_from_position_list(positions):
  for start_position, end_position in positions:
    add_line(physics_space, start_position, end_position)


def main():

  is_main_game_loop_running = True

  # Lists must be kept alive for balls to render
  balls = [add_ball(physics_space, (120, 50))]
  lines = [add_lines_from_position_list([
      ((100, 100), (200, 200)),
      ((200, 200), (300, 300)),
      ((300, 300), (400, 400)),
      ((400, 400), (500, 500)),
  ])]

  draw_options = pymunk.pygame_util.DrawOptions(render_screen)

  while is_main_game_loop_running:

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        is_main_game_loop_running = False
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        is_main_game_loop_running = False

    render_screen.fill((255, 255, 255))
    physics_space.debug_draw(draw_options)

    pygame.display.flip()

    render_clock.tick(60)
    physics_space.step(1 / 60.0)


if __name__ == "__main__":
  main()
