import json
import math
import pygame
from pygame.locals import *
import pymunk
import pymunk.pygame_util
import numpy as np
import random
from utils.clip_lines_within_box import line_clip
from utils.scale_and_translate_lines import scale_and_translate_lines

# Load level data from JSON
with open('main_game/levels.json', 'r') as file:
    level_data = json.load(file)


def level_generator():
  levels_list = list(level_data.keys())
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
# physics_space.collision_slop = 0.5

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


def add_physics_lines_from_position_list(physics_space, positions):
    lines = []
    for line_pos in positions:
        start_position = line_pos["start_pos"] # Anna was here
        end_position = line_pos["end_pos"]
        lines.append(add_physics_line(physics_space, start_position, end_position))
    return lines

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

  position_x, position_y = flag_shape.get_vertices()[0]
  rect = pygame.Rect(position_x, position_y - FLAT_POLE_HEIGHT - FLAG_WIDTH, FLAG_WIDTH, FLAG_WIDTH)
  pygame.draw.rect(render_screen, "green", rect)
  pygame.draw.line(render_screen, "black", (position_x, position_y), (position_x, position_y - FLAG_WIDTH - FLAT_POLE_HEIGHT))


def load_and_scale_background_images(level):
  images = []
  for image_info in level_data[level]["background_images"]:
    image_path = image_info["image"]
    top_left = tuple(image_info["start_pos"])
    bottom_right = tuple(image_info["end_pos"])
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

def change_level(current_level, physics_space, balls=None, level_lines=None, flag=None):
    if balls is not None:
        for ball in balls:
            physics_space.remove(*ball)
    if level_lines is not None:
        for line in level_lines:
            physics_space.remove(*line)
    if flag is not None:
        physics_space.remove(*flag)
    
    level_info = level_data[current_level]
    
    balls = [add_physics_ball(physics_space, tuple(level_info["ball_pos"]))]
    level_lines = add_physics_lines_from_position_list(physics_space, level_info["line_pos"])
    flag = add_physics_flag(physics_space, tuple(level_info["flag_pos"]))
    bg_images = load_and_scale_background_images(current_level)

    return balls, level_lines, flag, bg_images


def start_game(get_pose_results_callback):

  levels = level_generator()
  current_level = next(levels)

  is_main_game_loop_running = True


  balls, level_lines, flag, bg_images = change_level(current_level, physics_space)

  # [(game_position, webcam_position, colour)]
  # position in form (left, top, width, height)
  grids = [
      # ((0.5, 0.5, 0.1, 0.1), (0.5, 0.5, 0.1, 0.1), "green")
      ((0.1, 0.1, 0.2, 0.2), (0.3, 0.3, 0.3, 0.3), "green"),
      ((0.3, 0.3, 0.2, 0.2), (0.3, 0.3, 0.3, 0.3), "green"),
      ((0.5, 0.5, 0.2, 0.2), (0.3, 0.3, 0.3, 0.3), "green")
  ]

  TTL_MAX = 1
  WEBCAM_SIZE_SCALAR = 1/4

  game_lines = []

  head_width = None
  head_height = None
  head_pos = None

  head_lines = []

  webcam_pose_image_surface = None

  while is_main_game_loop_running:

    render_screen.fill(color=(255, 255, 255))

    draw_background_images(bg_images)

    for line, ttl in game_lines:
      if ttl == TTL_MAX:
        draw_physics_line(line)

    new_game_lines = []

    for line, ttl in game_lines:
      if ttl <= 0:
        line_shape, line_body = line
        physics_space.remove(line_shape, line_body)
      else:
        new_game_lines.append((line, ttl - 1))

    game_lines = new_game_lines

    new_head_lines = []

    for head, ttl in head_lines:
      if ttl <= 0:
        ellipse_shape, ellipse_body = head
        physics_space.remove(ellipse_shape, ellipse_body)
      else:
        new_head_lines.append((head, ttl - 1))

    head_lines = new_head_lines

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

    # render_screen.fill(color=(255, 255, 255))

    for ball in balls:
      draw_physics_ball(ball)

    draw_physics_flag(flag)

    pose_results, lines_results = get_pose_results_callback()

    if not(pose_results is None):
      webcam_pose_image = np.array(pose_results)
      # For some reason the image is rotated 90 degrees
      webcam_pose_image = np.rot90(webcam_pose_image)
      webcam_pose_image_surface = pygame.surfarray.make_surface(webcam_pose_image)

      # Dynamically calculate the webcam position and size
      # Assumisition data from the JSON structure
      webcam_positions = level_data[current_level]["webcam_pos"]
      webcam_top_left = tuple(webcam_positions["start_pos"])
      webcam_bottom_right = tuple(webcam_positions["end_pos"])

      webcam_top_left_scaled = scale_positions_to_screen_size(webcam_top_left)
      webcam_bottom_right_scaled = scale_positions_to_screen_size(webcam_bottom_right)
      webcam_width = webcam_bottom_right_scaled[0] - webcam_top_left_scaled[0]
      webcam_height = webcam_bottom_right_scaled[1] - webcam_top_left_scaled[1]

      render_position_rect = pygame.Rect(webcam_top_left_scaled, (webcam_width, webcam_height))

      render_screen.blit(source=webcam_pose_image_surface, dest=render_position_rect)

    # else:
      # print("Waiting for pose estimation")

    for line in lines_results:
      (start_position_x, start_position_y, c1), (end_position_x, end_position_y, c2) = line

      start_position = (1 - start_position_x, start_position_y)
      end_position = (1 - end_position_x, end_position_y)

      # allowed_connections = [(8, 6), (6, 5), (5, 4), (4, 0), (0, 1), (1, 2), (2, 3), (3, 7), (10, 9), (18, 20), (20, 16), (16, 18), (16, 22), (16, 14), (14, 12), (19, 17), (17, 15), (
      #     15, 19), (15, 21), (15, 13), (13, 11), (12, 11), (12, 24), (11, 23), (24, 23), (24, 26), (26, 28), (28, 32), (32, 30), (30, 28), (23, 25), (25, 27), (27, 29), (29, 31), (31, 27)]

      allowed_connections = [(13, 15)]

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

      # game_lines.append((add_physics_line(physics_space, start_position, end_position), TTL_MAX))

    # physics_space.debug_draw(draw_options)
    for line in lines_results:
      (start_position_x, start_position_y, connection1), (end_position_x, end_position_y, connection2) = line
      if ((connection1, connection2) in allowed_connections) or ((connection2, connection1) in allowed_connections):
        for grid in grids:
          game_position, webcam_position, _ = grid
          left, top, width, height = webcam_position
          game_left, game_top, game_width, game_height = game_position

          clipped_line = line_clip(((1 - start_position_x, start_position_y), (1 - end_position_x, end_position_y)), ((left, top), (left + width, top + height)))
          if clipped_line:
            start_pos, end_pos = scale_and_translate_lines([clipped_line], ((left, top), (left + width, top + height)),
                                                           ((game_left, game_top), (game_left + game_width, game_top + game_height)))[0]

            line = add_physics_line(physics_space, start_pos, end_pos)
            game_lines.append((line, TTL_MAX))

    for line in level_lines:
      draw_physics_line(line)

    for line, ttl in game_lines:
      if ttl == TTL_MAX:
        draw_physics_line(line)

    # if head_width and head_height and head_pos:
    #   head_lines.append((add_physics_ellipse(physics_space, head_pos, head_width, head_height), TTL_MAX))
    #   draw_physics_ellipse(head_pos, head_width, head_height)

    if webcam_pose_image_surface:
      for grid in grids:
        game_position, webcam_position, colour = grid

        webcam_position_left, webcam_position_top, webcam_position_width, webcam_position_height = webcam_position

        if webcam_pos: 
          webcam_pos_x, webcam_pos_y = webcam_pos

          webcam_position_left = webcam_pos_x + (webcam_pose_image_surface.get_width() * webcam_position_left)
          webcam_position_top = webcam_pos_y + webcam_pose_image_surface.get_height() * webcam_position_top
          webcam_position_width = webcam_pose_image_surface.get_width() * webcam_position_width
          webcam_position_height = webcam_pose_image_surface.get_height() * webcam_position_height

          webcam_position = webcam_position_left, webcam_position_top, webcam_position_width, webcam_position_height

          game_position_left, game_position_top, game_position_width, game_position_height = game_position

          pygame.draw.rect(render_screen, colour, pygame.Rect(webcam_position), 3)

          game_position_left = screen_width * game_position_left
          game_position_top = screen_height * game_position_top
          game_position_width = screen_width * game_position_width
          game_position_height = screen_height * game_position_height

          game_position = game_position_left, game_position_top, game_position_width, game_position_height

          pygame.draw.rect(render_screen, colour, pygame.Rect(game_position), 3)

    pygame.display.flip()

    # Check if flag is touched, if so, change level
    for ball in balls:
      ball_shape, _ = ball
      flag_shape, _ = flag
      if len(flag_shape.shapes_collide(ball_shape).points) > 0:
        print("Flag touched")
        current_level = next(levels)
        balls, level_lines, flag, bg_images = change_level(current_level, balls, level_lines, flag)
        break

    render_clock.tick(60)
    physics_space.step(1 / 60.0)

    # num_physics_steps = 10

    # render_clock.tick(60)
    # for _ in range(num_physics_steps):
    #   physics_space.step(1 / (60.0 * num_physics_steps))


if __name__ == "__main__":
  start_game()
