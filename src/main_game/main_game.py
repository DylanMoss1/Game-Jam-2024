import json
import math
import pygame
from pygame.locals import *
import pymunk
import pymunk.pygame_util
import numpy as np
import random
from utils.clip_lines_within_box import line_clip
from utils.scale_and_translate_ellipse import scale_and_translate_ellipse
from utils.scale_and_translate_lines import scale_and_translate_lines

# --- Load level data from JSON ---

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

BALL_MASS = 1
BALL_RADIUS = 0.007 * screen_width
BALL_ELASTICITY = 1.0
BALL_FRICTION = 1.0

FLAG_WIDTH = 0.02 * screen_width
FLAT_POLE_HEIGHT = 0.02 * screen_width


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
    start_position = line_pos["start_pos"]  # Anna was here
    end_position = line_pos["end_pos"]
    lines.append(add_physics_line(physics_space, start_position, end_position))
  return lines


def add_physics_ellipse(space, pos, width, height, num_segments=50):
  body = pymunk.Body(body_type=pymunk.Body.STATIC)

  vertices = []
  for i in range(num_segments):
    angle = 2.0 * 3.1415 * i / num_segments
    x = pos[0] + width * 0.5 * pymunk.vec2d.Vec2d(0, 1).rotated(angle).x
    y = pos[1] + height * 0.5 * pymunk.vec2d.Vec2d(0, 1).rotated(angle).y
    vertices.append((x, y))
  shape = pymunk.Poly(body, vertices, radius=1)
  space.add(body, shape)
  return shape, body


def add_physics_flag(physics_space, position):
  body = pymunk.Body(body_type=pymunk.Body.STATIC)

  screen_position_x, screen_position_y = scale_positions_to_screen_size(position)

  # shape = pymunk.Poly(body, [(screen_position_x, screen_position_y), (screen_position_x + FLAG_WIDTH, screen_position_y), (screen_position_x,
  #                     screen_position_y - FLAG_WIDTH - FLAT_POLE_HEIGHT), (screen_position_x + FLAG_WIDTH, screen_position_y - FLAG_WIDTH - FLAT_POLE_HEIGHT)])
  shape = pymunk.Segment(body, (screen_position_x, screen_position_y), (screen_position_x, screen_position_y - FLAG_WIDTH - FLAT_POLE_HEIGHT), 1)

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
  if flag:
    flag_shape, _ = flag

    position_x, position_y = flag_shape.a
    rect = pygame.Rect(position_x, position_y - FLAT_POLE_HEIGHT - FLAG_WIDTH, FLAG_WIDTH, FLAG_WIDTH)
    pygame.draw.rect(render_screen, "green", rect)
    pygame.draw.rect(render_screen, "black", rect, width=1)
    pygame.draw.line(render_screen, "black", (position_x, position_y), (position_x, position_y - FLAG_WIDTH - FLAT_POLE_HEIGHT))


# --- Handle Background Objects ---

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

# --- Handle Level Change ---


def parse_grids(grids):
  parsed_grids = []

  print(grids)

  for grid in grids:
    print(grid)
    game_pos, webcam_pos, colour = grid[0], grid[1], grid[2]
    game_pos = (game_pos[0], game_pos[1], game_pos[2], game_pos[3])
    webcam_pos = (webcam_pos[0], webcam_pos[1], webcam_pos[2], webcam_pos[3])
    parsed_grids.append((game_pos, webcam_pos, colour))

  return parsed_grids


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
  grids = parse_grids(level_info["grids"])
  text = level_info["instruction"]
  allow_head = level_info["allow_head"]

  return balls, level_lines, flag, bg_images, grids, allow_head, text

# --- Setup Action Grids (i.e. boxes which reflect poses onto the game) ---


# [(game_position, webcam_position, colour)]
# position in form (left, top, width, height)


# --- Main Game Loop Utils ---

TTL_MAX = 1
WEBCAM_SIZE_SCALAR = 1/4


def remove_dead_game_lines(game_lines):

  new_game_lines = []

  for line, ttl in game_lines:
    if ttl <= 0:
      physics_space.remove(*line)
    else:
      new_game_lines.append((line, ttl - 1))

  return new_game_lines


def remove_dead_head_lines(head_lines):

  new_head_lines = []

  for head, ttl in head_lines:
    if ttl <= 0:
      physics_space.remove(*head)
    else:
      new_head_lines.append((head, ttl - 1))

  return new_head_lines


def remove_dead_balls(balls):
  new_balls = []

  for ball in balls:
    _, ball_body = ball
    if ball_body.position.y > screen_height * 1.1:
      physics_space.remove(*ball)
    else:
      new_balls.append(ball)

  return new_balls


def parse(current_level):
  level_int = current_level[6:]
  return f"Level: {level_int}"

# --- Main Game Loop ---


def start_game(get_pose_results_callback):

  # --- Generate First Level ---

  levels = level_generator()
  current_level = next(levels)

  if current_level == "level_0":
    balls, level_lines, flag, bg_images, grids, allow_head, text = [], [], None, load_and_scale_background_images("level_0"), [], False, ""
  else:
    balls, level_lines, flag, bg_images, grids, allow_head, text = change_level(current_level, physics_space)

  is_main_game_loop_running = True

  game_lines = []
  head_lines = []

  webcam_pose_image_surface = None

  head_width = None
  head_height = None
  head_pos = None

  while is_main_game_loop_running:

    render_screen.fill(color=(255, 255, 255))
    if current_level == "level_0":
      draw_background_images(bg_images)

    # Draw most up-to-date line (i.e. one with the highest possible time-to-live)
    for line, ttl in game_lines:
      if ttl == TTL_MAX:
        draw_physics_line(line)

    game_lines = remove_dead_game_lines(game_lines)
    head_lines = remove_dead_head_lines(head_lines)

    if current_level != "level_0":
      # Add new balls to the game randomly
      if random.random() < 0.01:
        balls.append(add_physics_ball(physics_space, (0.11, 0.05)))

      balls = remove_dead_balls(balls)

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          is_main_game_loop_running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          is_main_game_loop_running = False

      # Draw any remaining balls
      for ball in balls:
        draw_physics_ball(ball)

    # Draw the end goal flag
    draw_physics_flag(flag)

    pose_results, lines_results = get_pose_results_callback()

    webcam_pos = None

    if not (pose_results is None):
      webcam_pose_image = np.array(pose_results)
      # For some reason the image is rotated 90 degrees
      webcam_pose_image = np.rot90(webcam_pose_image)
      webcam_pose_image_surface = pygame.surfarray.make_surface(webcam_pose_image)

      # Dynamically calculate the webcam position and size
      # Assumisition data from the JSON structure
      webcam_positions = level_data[current_level]["webcam_pos"]

      if current_level == "level_0":
        webcam_top_left = scale_positions_to_screen_size(tuple(webcam_positions["start_pos"]))
        webcam_bottom_right = scale_positions_to_screen_size(tuple(webcam_positions["end_pos"]))
      else:
        webcam_top_left = (screen_width - webcam_pose_image_surface.get_width(), 0)
        webcam_bottom_right = (screen_width, webcam_pose_image_surface.get_width())

      # webcam_top_left_scaled = scale_positions_to_screen_size(webcam_top_left)
      # webcam_bottom_right_scaled = scale_positions_to_screen_size(webcam_bottom_right)
      webcam_width = webcam_bottom_right[0] - webcam_top_left[0]
      webcam_height = webcam_bottom_right[1] - webcam_top_left[1]

      webcam_pos = webcam_top_left

      render_position_rect = pygame.Rect(webcam_pos, (0, 0))

      x = screen_width * 0.22
      y = screen_width * 0.22

      if current_level == "level_0":
        render_screen.blit(source=webcam_pose_image_surface, dest=render_position_rect, area=pygame.Rect(
            ((webcam_pose_image_surface.get_width() - x) / 2, (webcam_pose_image_surface.get_height() - y) / 2), (x, y)))
      else:
        render_screen.blit(source=webcam_pose_image_surface, dest=render_position_rect)
    # else:
      # print("Waiting for pose estimation")

    c16 = None
    c15 = None
    c8 = None
    c7 = None

    for line in lines_results:
      (start_position_x, start_position_y, c1), (end_position_x, end_position_y, c2) = line

      start_position = (1 - start_position_x, start_position_y)
      end_position = (1 - end_position_x, end_position_y)

      allowed_connections = level_data[current_level].get("allowed_limb_connections",
                                                          [[8, 6], [6, 5], [5, 4], [4, 0], [0, 1], [1, 2],
                                                           [2, 3], [3, 7], [10, 9], [18, 20], [20, 16], [16, 18],
                                                           [16, 22], [16, 14], [14, 12], [19, 17], [17, 15], [15, 19],
                                                           [15, 21], [15, 13], [13, 11], [12, 11], [12, 24], [11, 23],
                                                           [24, 23], [24, 26], [26, 28], [28, 32], [32, 30], [30, 28],
                                                           [23, 25], [25, 27], [27, 29], [29, 31], [31, 27]])

      if c1 == 16:
        c16 = start_position_y
      elif c2 == 16:
        c16 = end_position_y
      if c1 == 15:
        c15 = start_position_y
      elif c2 == 15:
        c15 = end_position_y
      if c1 == 7:
        c7 = start_position_y
      elif c2 == 7:
        c7 = end_position_y
      if c1 == 8:
        c8 = start_position_y
      elif c2 == 8:
        c8 = end_position_y

      # head
      if c1 == 8 and c2 == 7:
        # start_position = scale_positions_to_screen_size(start_position)
        # end_position = scale_positions_to_screen_size(end_position)
        head_pos = (start_position[0] + end_position[0]) / 2, (start_position[1] + end_position[1]) / 2
        head_width = math.sqrt((start_position[0] - end_position[0]) ** 2 + (start_position[1] - end_position[1]) ** 2)
        continue

      if c1 == 4 and c2 == 10:
        # start_position = scale_positions_to_screen_size(start_position)
        # end_position = scale_positions_to_screen_size(end_position)
        head_height = 3 * math.sqrt((start_position[0] - end_position[0]) ** 2 + (start_position[1] - end_position[1]) ** 2)
        continue

    if current_level == "level_0":
      if c16 and c8 and c15 and c7:
        if c16 < c8 and c15 < c7:
          current_level = next(levels)
          balls, level_lines, flag, bg_images, grids, allow_head, text = change_level(current_level, physics_space, balls, level_lines, flag)

      # game_lines.append((add_physics_line(physics_space, start_position, end_position), TTL_MAX))

    # physics_space.debug_draw(draw_options)
    for line in lines_results:
      (start_position_x, start_position_y, connection1), (end_position_x, end_position_y, connection2) = line
      if ([connection1, connection2] in allowed_connections) or ([connection2, connection1] in allowed_connections):
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

    if allow_head and head_width and head_height and head_pos:
      for grid in grids:
        game_position, webcam_position, _ = grid
        left, top, width, height = webcam_position
        game_left, game_top, game_width, game_height = game_position

        in_box = head_pos[0] > left and head_pos[0] < left + width and head_pos[1] > top and head_pos[1] < top + height
        if in_box:
          new_head_pos, new_head_width, new_head_height = scale_and_translate_ellipse((head_pos, head_width, head_height), ((left, top), (left + width, top + height)),
                                                                                      ((game_left, game_top), (game_left + game_width, game_top + game_height)))
          new_head_pos = scale_positions_to_screen_size(new_head_pos)
          new_head_width, new_head_height = scale_positions_to_screen_size((new_head_width, new_head_height))
          head_lines.append((add_physics_ellipse(physics_space, new_head_pos, new_head_width, new_head_height), TTL_MAX))
          draw_physics_ellipse(new_head_pos, new_head_width, new_head_height)

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

    render_screen.blit(render_font.render(parse(current_level), True, (0, 0, 0)), (0, 0))
    if webcam_pos:
      render_screen.blit(render_font.render(text, True, (0, 0, 0)), (webcam_pos[0] + webcam_width / 2.2, screen_height / 2.2))
    pygame.display.flip()

    # Check if flag is touched, if so, change level
    if flag:
      for ball in balls:
        ball_shape, _ = ball
        flag_shape, _ = flag
        if len(flag_shape.shapes_collide(ball_shape).points) > 0:
          current_level = next(levels)
          balls, level_lines, flag, bg_images, grids, allow_head, text = change_level(current_level, physics_space, balls, level_lines, flag)

    render_clock.tick(60)
    physics_space.step(1 / 60.0)


if __name__ == "__main__":
  start_game()
