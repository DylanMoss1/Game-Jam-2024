import math
import pygame
from pygame.locals import *
import pymunk
import pymunk.pygame_util
import numpy as np
import random

LEVEL_BACKGROUND_IMAGES = {
    "level_1": [("shake_two_look_clean.jpg", (0.1, 0.1), (0.4, 0.4))],
    "level_2": [("shake_two_look_clean.jpg", (0.1, 0.1), (0.4, 0.4))]
}

LEVEL_LINE_POS = {
    "level_1": [
      ((0.1, 0.1), (0.2, 0.15)),
      ((0.8, 0.8), (0.85, 0.85)),
  ],
    "level_2": [
      ((0.25, 0.25), (0.35, 0.35)),
      ((0.4, 0.4), (0.5, 0.5)),
      ((0.55, 0.55), (0.65, 0.65)),
  ]
}

LEVEL_FLAG_POS = {
    "level_1": (0.825, 0.825),
    "level_2": (0.5, 0.5)

}

LEVEL_BALL_POS = {
    "level_1": (0.11, 0.05),
    "level_2": (0.11, 0.05)
}

def level_generator():
  levels_list = list(LEVEL_BALL_POS.keys())
  n = 0
  while True:
    yield levels_list[n]
    n = (n + 1) % len(levels_list)


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

def add_physics_ellipse(space, pos, width, height, num_segments=50):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    # body.position = pos

    vertices = []
    for i in range(num_segments):
        angle = 2.0 * 3.1415 * i / num_segments
        x = pos[0] + width * 0.5 * pymunk.vec2d.Vec2d(0, 1).rotated(angle).x
        y = pos[1] + height * 0.5 * pymunk.vec2d.Vec2d(0, 1).rotated(angle).y
        vertices.append((x, y))
    # print(vertices)
    shape = pymunk.Poly(body, vertices, radius=1)
    space.add(body, shape)
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

def draw_physics_ellipse(position, width, height):

  pygame.draw.ellipse(render_screen, "blue", pygame.Rect(position[0] - width / 2, position[1] - height / 2, width, height), 1)
  

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
  rect = pygame.Rect(position_x, position_y - FLAT_POLE_HEIGHT - FLAG_WIDTH, FLAG_WIDTH, FLAG_WIDTH)
  pygame.draw.rect(render_screen, "green", rect)
  pygame.draw.line(render_screen, "black", (position_x, position_y), (position_x, position_y - FLAG_WIDTH - FLAT_POLE_HEIGHT))
  return rect

def load_and_scale_background_images(level):
  images = []
  for image_path, top_left, bottom_right in LEVEL_BACKGROUND_IMAGES[level]:
    # Load the image
    image = pygame.image.load(f"imgs/{image_path}")
    # Scale the image
    top_left_scaled = scale_positions_to_screen_size(top_left)
    bottom_right_scaled = scale_positions_to_screen_size(bottom_right)
    size_scaled = (bottom_right_scaled[0] - top_left_scaled[0], bottom_right_scaled[1] - top_left_scaled[1])
    image = pygame.transform.scale(image, size_scaled)
    images.append((image, top_left_scaled))
  return images

def draw_background_images(bg_images):
  for image, position in bg_images:
    render_screen.blit(image, position)

def change_level(current_level, balls=None, level_lines=None, flag=None):
  if balls is not None:
    for ball in balls:
      physics_space.remove(*ball)
  if level_lines is not None:
    for line in level_lines:
      physics_space.remove(*line)
  if flag is not None:
    physics_space.remove(*flag)
  # Lists must be kept alive for balls to render
  balls = [add_physics_ball(physics_space, LEVEL_BALL_POS[current_level])]

  level_lines = add_physics_lines_from_position_list(LEVEL_LINE_POS[current_level])

  flag = add_physics_flag(physics_space, LEVEL_FLAG_POS[current_level])

  bg_images = load_and_scale_background_images(current_level)

  return balls, level_lines, flag, bg_images

def start_game(get_pose_results_callback):

  levels = level_generator()
  current_level = next(levels)

  is_main_game_loop_running = True


  balls, level_lines, flag, bg_images = change_level(current_level)

  game_lines_3 = []
  game_lines_2 = []
  game_lines_1 = []
  game_lines_0 = []

  head_width = None
  head_height = None
  head_pos = None

  head_0 = None
  head_1 = None
  head_2 = None
  head_3 = None

  while is_main_game_loop_running:

    for line in game_lines_0:
      line_shape, line_body = line
      physics_space.remove(line_shape, line_body)
    
    if head_0 is not None:
      ellipse_shape, ellipse_body = head_0
      physics_space.remove(ellipse_shape, ellipse_body)

    head_0 = head_1
    head_1 = head_2
    head_2 = head_3
    head_3 = None

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
      (start_position_x, start_position_y, c1), (end_position_x, end_position_y, c2) = line

      start_position = (1 - start_position_x, start_position_y)
      end_position = (1 - end_position_x, end_position_y)

      # head
      if c1 == 8 and c2 == 7:
        start_position = scale_positions_to_screen_size(start_position)
        end_position = scale_positions_to_screen_size(end_position)
        head_pos = (start_position[0] + end_position[0]) / 2, (start_position[1] + end_position[1]) / 2
        head_width = math.sqrt((start_position[0] - end_position[0]) ** 2 + (start_position[1] - end_position[1]) ** 2)
        continue

      if c1 == 4 and c2 == 10:
        start_position = scale_positions_to_screen_size(start_position)
        end_position = scale_positions_to_screen_size(end_position)
        head_height = 3 * math.sqrt((start_position[0] - end_position[0]) ** 2 + (start_position[1] - end_position[1]) ** 2)
        continue

      game_lines_3.append(add_physics_line(physics_space, start_position, end_position))


    pygame.display.flip()

    render_screen.fill(color=(255, 255, 255))

    draw_background_images(bg_images)

    # physics_space.debug_draw(draw_options)

    for ball in balls:
      draw_physics_ball(ball)

    for line in level_lines:
      draw_physics_line(line)

    for line in game_lines_3:
      draw_physics_line(line)
    
    if head_width and head_height and head_pos:
      head_3 = add_physics_ellipse(physics_space, head_pos, head_width, head_height)
      draw_physics_ellipse(head_pos, head_width, head_height)

    rect = draw_physics_flag(flag)

    # Check if flag is touched, if so, change level
    for ball in balls:
      _, ball_body = ball
      if rect.collidepoint(ball_body.position):
        print("Flag touched")
        current_level = next(levels)
        balls, level_lines, flag, bg_images = change_level(current_level, balls, level_lines, flag)
        break

    render_clock.tick(60)
    physics_space.step(1 / 60.0)


if __name__ == "__main__":
  start_game()
