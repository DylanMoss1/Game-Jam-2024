import pygame
from pygame.locals import *
import pymunk
import pymunk.pygame_util
import numpy as np

# --- Initialise PyGame (Rendering Engine) ---

pygame.init()
render_clock = pygame.time.Clock()

render_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

render_font = pygame.font.SysFont(None, 48)

screen_width, screen_height = pygame.display.get_surface().get_size()

# --- Initialise PyMunk (Physics Engine) ---

physics_space = pymunk.Space()
physics_space.gravity = (0.0, 900.0)


# --- Add Objects To Scene ---

BALL_MASS = 1
BALL_RADIUS = 14
BALL_ELASTICITY = 1.0
BALL_FRICTION = 1.0


def scale_positions_to_screen_size(position):
  position_x, position_y = position
  return position_x * screen_width, position_y * screen_height


def add_ball(physics_space, position) -> pymunk.Circle:

  inertia = pymunk.moment_for_circle(BALL_MASS, 0, BALL_RADIUS, (0, 0))

  body = pymunk.Body(BALL_MASS, inertia)
  body.position = scale_positions_to_screen_size(position)

  shape = pymunk.Circle(body, BALL_RADIUS)
  shape.elasticity = BALL_ELASTICITY
  shape.friction = BALL_FRICTION

  physics_space.add(body, shape)

  return shape


def add_line(physics_space, start_position, end_position) -> pymunk.Segment:
  body = pymunk.Body(body_type=pymunk.Body.STATIC)

  shape = pymunk.Segment(body, scale_positions_to_screen_size(start_position), scale_positions_to_screen_size(end_position), radius=1)

  shape.elasticity = 0.0
  shape.friction = 0.0

  physics_space.add(body, shape)

  return shape


def add_lines_from_position_list(positions):
  for start_position, end_position in positions:
    add_line(physics_space, start_position, end_position)


def start_game(get_pose_results_callback):

  is_main_game_loop_running = True

  # Lists must be kept alive for balls to render
  balls = [add_ball(physics_space, (0.11, 0.05))]
  lines = [add_lines_from_position_list([
      ((0.1, 0.1), (0.2, 0.2)),
      ((0.25, 0.25), (0.35, 0.35)),
      ((0.4, 0.4), (0.5, 0.5)),
      ((0.55, 0.55), (0.65, 0.65)),
  ])]

  draw_options = pymunk.pygame_util.DrawOptions(render_screen)

  while is_main_game_loop_running:

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        is_main_game_loop_running = False
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        is_main_game_loop_running = False

    render_screen.fill(color=(255, 255, 255))
    physics_space.debug_draw(draw_options)

    previous_pose_results, previous_lines_results = get_pose_results_callback()

    if not (previous_pose_results is None):

      webcam_pose_image = np.array(previous_pose_results)
      # for some reason the image is rotated 90 degrees
      webcam_pose_image = np.rot90(webcam_pose_image)
      webcam_pose_image_surface = pygame.surfarray.make_surface(webcam_pose_image)

      rendered_webcam_width = screen_width * 1/6

      render_position_rect = pygame.Rect((screen_width - 2 * rendered_webcam_width, 0), (rendered_webcam_width, rendered_webcam_width))

      render_screen.blit(source=webcam_pose_image_surface, dest=render_position_rect)

    pygame.display.flip()

    render_clock.tick(60)
    physics_space.step(1 / 60.0)


if __name__ == "__main__":
  start_game()
