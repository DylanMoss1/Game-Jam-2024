import pygame
from pygame.locals import *
import pymunk
import pymunk.pygame_util
import numpy as np
import random

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

# All sizes are relative to screen width

def scale_size_to_screen_size(size):
  return size * screen_width


BALL_MASS = 1
BALL_RADIUS = scale_size_to_screen_size(0.007)
BALL_ELASTICITY = 1.0
BALL_FRICTION = 1.0

FLAG_WIDTH = scale_size_to_screen_size(0.02)
FLAT_POLE_HEIGHT = scale_size_to_screen_size(0.02)

def scale_positions_to_screen_size(position):
  position_x, position_y = position
  return position_x * screen_width, position_y * screen_height


def add_physics_ball(physics_space, position):

  inertia = pymunk.moment_for_circle(BALL_MASS, 0, BALL_RADIUS, (0, 0))

  body = pymunk.Body(BALL_MASS, inertia)
  body.position = scale_positions_to_screen_size(position)

  shape = pymunk.Circle(body, BALL_RADIUS)
  shape.elasticity = BALL_ELASTICITY
  shape.friction = BALL_FRICTION

  physics_space.add(body, shape)

  return shape, body


def add_physics_line(physics_space, start_position, end_position):
  body = pymunk.Body(body_type=pymunk.Body.STATIC)

  shape = pymunk.Segment(body, scale_positions_to_screen_size(start_position), scale_positions_to_screen_size(end_position), radius=1)

  shape.elasticity = 0.0
  shape.friction = 0.0

  physics_space.add(body, shape)

  return shape, body


def add_physics_lines_from_position_list(positions):
  return [add_physics_line(physics_space, start_position, end_position) for start_position, end_position in positions]


def add_physics_flag(physics_space, position):
  body = pymunk.Body(body_type=pymunk.Body.STATIC)

  screen_position_x, screen_position_y = scale_positions_to_screen_size(position)

  shape = pymunk.Poly(body, [(screen_position_x, screen_position_y), (screen_position_x + FLAG_WIDTH, screen_position_y), (screen_position_x,
                      screen_position_y + FLAG_WIDTH + FLAT_POLE_HEIGHT), (screen_position_x + FLAG_WIDTH, screen_position_y + FLAG_WIDTH + FLAT_POLE_HEIGHT)])

  shape.elasticity = 0.0
  shape.friction = 0.0

  physics_space.add(body, shape)

  return shape, body

# --- Draw Objects ---


def draw_physics_ball(ball):
  ball_shape, ball_body = ball

  radius = ball_shape.radius
  position = ball_body.position

  pygame.draw.circle(render_screen, "blue", position, radius)


def draw_physics_line(line):
  line_shape, _ = line

  start_position_x = line_shape.a.x
  start_position_y = line_shape.a.y
  start_position = (start_position_x, start_position_y)

  end_position_x = line_shape.b.x
  end_position_y = line_shape.b.y
  end_position = (end_position_x, end_position_y)

  pygame.draw.line(render_screen, "black", start_position, end_position)


def draw_physics_flag(flag):
  flag_shape, _ = flag

  # print(flag_shape.get_vertices())

  position_x, position_y = flag_shape.get_vertices()[0]

  pygame.draw.rect(render_screen, "green", pygame.Rect(position_x, position_y - FLAT_POLE_HEIGHT - FLAG_WIDTH, FLAG_WIDTH, FLAG_WIDTH))
  pygame.draw.line(render_screen, "black", (position_x, position_y), (position_x, position_y - FLAG_WIDTH - FLAT_POLE_HEIGHT))


def start_game(get_pose_results_callback):

  is_main_game_loop_running = True

  # Lists must be kept alive for balls to render
  balls = [add_physics_ball(physics_space, (0.11, 0.05))]

  level_lines = add_physics_lines_from_position_list([
      ((0.1, 0.1), (0.2, 0.15)),
      # ((0.25, 0.25), (0.35, 0.35)),
      # ((0.4, 0.4), (0.5, 0.5)),
      # ((0.55, 0.55), (0.65, 0.65)),
      ((0.8, 0.8), (0.85, 0.85)),
  ])

  flag = add_physics_flag(physics_space, (0.825, 0.825))

  game_lines_3 = []
  game_lines_2 = []
  game_lines_1 = []
  game_lines_0 = []

  while is_main_game_loop_running:

    for line in game_lines_0:
      line_shape, line_body = line
      physics_space.remove(line_shape, line_body)

    game_lines_0 = game_lines_1
    game_lines_1 = game_lines_2
    game_lines_2 = game_lines_3
    game_lines_3 = []

    if random.random() < 0.01:
      balls.append(add_physics_ball(physics_space, (0.11, 0.05)))

    balls_to_remove = []

    for ball in balls:
      _, ball_body = ball
      if ball_body.position.y > screen_height * 1.1:
        balls_to_remove.append(ball)

    for ball in balls_to_remove:
      balls.remove(ball)
      physics_space.remove(*ball)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        is_main_game_loop_running = False
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        is_main_game_loop_running = False

    previous_pose_results, previous_lines_results = get_pose_results_callback()

    if not (previous_pose_results is None):

      webcam_pose_image = np.array(previous_pose_results)
      # for some reason the image is rotated 90 degrees
      webcam_pose_image = np.rot90(webcam_pose_image)
      webcam_pose_image_surface = pygame.surfarray.make_surface(webcam_pose_image)

      rendered_webcam_width = screen_width * 1/6

      render_position_rect = pygame.Rect((screen_width - 2 * rendered_webcam_width, 0), (rendered_webcam_width, rendered_webcam_width))

      render_screen.blit(source=webcam_pose_image_surface, dest=render_position_rect)

    else:
      print("Waiting for pose estimation")

    for line in previous_lines_results:
      (start_position_x, start_position_y), (end_position_x, end_position_y) = line

      start_position = (1 - start_position_x, start_position_y)
      end_position = (1 - end_position_x, end_position_y)

      game_lines_3.append(add_physics_line(physics_space, start_position, end_position))

    pygame.display.flip()

    render_screen.fill(color=(255, 255, 255))
    # physics_space.debug_draw(draw_options)

    for ball in balls:
      draw_physics_ball(ball)

    for line in level_lines:
      draw_physics_line(line)

    for line in game_lines_3:
      draw_physics_line(line)

    draw_physics_flag(flag)

    render_clock.tick(60)
    physics_space.step(1 / 60.0)


if __name__ == "__main__":
  start_game()
