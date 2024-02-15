from dataclasses import dataclass
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
    if n == 0:
      n = 1

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


def add_physics_ball(position):

  inertia = pymunk.moment_for_circle(BALL_MASS, 0, BALL_RADIUS, (0, 0))

  body = pymunk.Body(BALL_MASS, inertia)
  body.position = scale_positions_to_screen_size(position)

  shape = pymunk.Circle(body, BALL_RADIUS)
  shape.elasticity = BALL_ELASTICITY
  shape.friction = BALL_FRICTION

  physics_space.add(body, shape)

  return shape, body


def add_physics_line(start_position, end_position):
  body = pymunk.Body(body_type=pymunk.Body.STATIC)

  shape = pymunk.Segment(body, scale_positions_to_screen_size(start_position), scale_positions_to_screen_size(end_position), radius=1)

  shape.elasticity = 0.0
  shape.friction = 0.0

  physics_space.add(body, shape)

  return shape, body


def add_physics_lines_from_position_list(positions):
  lines = []
  for line_pos in positions:
    start_position = line_pos["start_pos"]  # Anna was here
    end_position = line_pos["end_pos"]
    lines.append(add_physics_line(start_position, end_position))
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


def add_physics_flag(position):
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


def change_level(current_level, balls=None, level_lines=None, flag=None):
  if balls is not None:
    for ball in balls:
      physics_space.remove(*ball)
  if level_lines is not None:
    for line in level_lines:
      physics_space.remove(*line)
  if flag is not None:
    physics_space.remove(*flag)

  level_info = level_data[current_level]

  balls = [add_physics_ball(tuple(level_info["ball_pos"]))]
  level_lines = add_physics_lines_from_position_list(level_info["line_pos"])
  flag = add_physics_flag(tuple(level_info["flag_pos"]))
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


def remove_dead_game_limbs(game_limbs):

  new_game_limbs = []

  for line, ttl in game_limbs:
    if ttl <= 0:
      physics_space.remove(*line)
    else:
      new_game_limbs.append((line, ttl - 1))

  return new_game_limbs


def remove_dead_game_heads(game_heads):

  new_game_heads = []

  for head, ttl in game_heads:
    if ttl <= 0:
      physics_space.remove(*head)
    else:
      new_game_heads.append((head, ttl - 1))

  return new_game_heads


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


def get_events():
  is_main_game_loop_running = True
  for event in pygame.event.get():
        if event.type == pygame.QUIT:
          is_main_game_loop_running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          is_main_game_loop_running = False
  return is_main_game_loop_running

def initialise_game():
    levels = level_generator()
    current_level = next(levels)

    if current_level == "level_0":
      balls, level_lines, flag, bg_images, grids, allow_head, text = [], [], None, load_and_scale_background_images("level_0"), [], False, ""
    else:
      balls, level_lines, flag, bg_images, grids, allow_head, text = change_level(current_level, physics_space)

    is_main_game_loop_running = True

    game_limbs = []
    game_heads = []

    webcam_pose_image_surface = None

    head_width = None
    head_height = None
    head_pos = None

    webcam_pos = None

    return levels, current_level, balls, level_lines, flag, bg_images, grids, allow_head, text, is_main_game_loop_running, game_limbs, game_heads, head_width, head_height, head_pos

def draw_background(bg_images):
    render_screen.fill(color=(255, 255, 255))
    #if current_level == "level_0":
    draw_background_images(bg_images)

def add_remove_balls(balls):
  # Add new balls to the game randomly
  if random.random() < 0.01:
      balls.append(add_physics_ball((0.11, 0.05)))

  balls = remove_dead_balls(balls)
  return balls

def draw_balls(balls):
    # Draw any remaining balls
    for ball in balls:
        draw_physics_ball(ball)

def add_game_limbs(level_data, current_level, pose_lines, grids, game_limbs, TTL_MAX):
    allowed_connections = level_data[current_level].get("allowed_limb_connections",
        [[8, 6], [6, 5], [5, 4], [4, 0], [0, 1], [1, 2],
          [2, 3], [3, 7], [10, 9], [18, 20], [20, 16], [16, 18],
          [16, 22], [16, 14], [14, 12], [19, 17], [17, 15], [15, 19],
          [15, 21], [15, 13], [13, 11], [12, 11], [12, 24], [11, 23],
          [24, 23], [24, 26], [26, 28], [28, 32], [32, 30], [30, 28],
          [23, 25], [25, 27], [27, 29], [29, 31], [31, 27]])

    # physics_space.debug_draw(draw_options)
    for line in pose_lines:
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

            line = add_physics_line(start_pos, end_pos)
            game_limbs.append((line, TTL_MAX))
    
    return game_limbs


def add_heads(allow_head, head_width, head_height, head_pos, grids, game_heads, TTL_MAX):
    game_heads = []
    if allow_head and head_width and head_height and head_pos:
        for grid in grids:
            game_position, webcam_position, _ = grid
            left, top, width, height = webcam_position
            game_left, game_top, game_width, game_height = game_position

            in_box = head_pos[0] > left and head_pos[0] < left + width and head_pos[1] > top and head_pos[1] < top + height
            if in_box:
                new_head_pos, new_head_width, new_head_height = scale_and_translate_ellipse(
                    (head_pos, head_width, head_height),
                    ((left, top), (left + width, top + height)),
                    ((game_left, game_top), (game_left + game_width, game_top + game_height))
                )
                new_head_pos = scale_positions_to_screen_size(new_head_pos)
                new_head_width, new_head_height = scale_positions_to_screen_size((new_head_width, new_head_height))

                # Add head to the physics space and keep the reference for drawing
                game_heads.append((add_physics_ellipse(new_head_pos, new_head_width, new_head_height), TTL_MAX))
    return game_heads

def draw_heads(game_heads):
    for head_line, _ in game_heads:
        physics_object, _ = head_line # Assuming the physics_object contains position and dimensions
        draw_physics_ellipse(physics_object.position, physics_object.width, physics_object.height)

def draw_rectangles(webcam_pose_image_surface, grids, webcam_pos):
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

def get_xflipped_points_dict_from_lines(pose_lines):
    points_dict = {}
    for line in pose_lines:
      (start_position_x, start_position_y, c1), (end_position_x, end_position_y, c2) = line
      if c1 not in points_dict:
        points_dict[c1] = (1 - start_position_x, start_position_y)
      if c2 not in points_dict:
        points_dict[c2] = (1 - end_position_x, end_position_y)
    return points_dict

def get_head_info(points_dict):
    # Assuming the points for head and head height are available in points_dict
    # and using the identifiers 8, 7 for head width, and 4, 10 for head height calculation
    
    # Calculate head position and width
    if 8 in points_dict and 7 in points_dict:
        start_position, end_position = points_dict[8], points_dict[7]
        head_pos = ((start_position[0] + end_position[0]) / 2, (start_position[1] + end_position[1]) / 2)
        head_width = math.sqrt((start_position[0] - end_position[0]) ** 2 + (start_position[1] - end_position[1]) ** 2)
    else:
        head_pos = (None, None)
        head_width = None

    # Calculate head height
    if 4 in points_dict and 10 in points_dict:
        start_position, end_position = points_dict[4], points_dict[10]
        head_height = 3 * math.sqrt((start_position[0] - end_position[0]) ** 2 + (start_position[1] - end_position[1]) ** 2)
    else:
        head_height = None

    return head_width, head_height, head_pos


def are_arms_above_head(points_dict):
  return all(key in points_dict for key in [16, 8, 15, 7]) and points_dict[16][1] < points_dict[8][1] and points_dict[15][1] < points_dict[7][1]

def get_webcam_info(webcam_img, current_level):
    if webcam_img is None: return None, None, None, None, None

    webcam_pose_arr = np.array(webcam_img)
    # For some reason the image is rotated 90 degrees
    webcam_pose_arr = np.rot90(webcam_pose_arr)
    webcam_pose_image_surface = pygame.surfarray.make_surface(webcam_pose_arr)

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

    return webcam_pose_image_surface, webcam_pos, webcam_width, webcam_height, render_position_rect


def is_touching_flag(flag, balls):
  if flag is None:
    return False
  for ball in balls:
    ball_shape, _ = ball
    flag_shape, _ = flag
    if len(flag_shape.shapes_collide(ball_shape).points) > 0:
      return True
  return False

@dataclass
class WebcamInfo:
    pose_image_surface: any
    position: any
    width: any
    height: any
    image: any

def draw_webcam(current_level, webcam_info: WebcamInfo, render_position_rect):
    if current_level == "level_0":
      cropped_webcam_width = screen_width * 0.22
      cropped_webcam_height = screen_width * 0.22
      render_screen.blit(source=webcam_info.pose_image_surface, dest=render_position_rect, area=pygame.Rect(
          (webcam_info.pose_image_surface.get_width() - cropped_webcam_width) / 2, # left
          (webcam_info.pose_image_surface.get_height() - cropped_webcam_height) / 2, # top
          cropped_webcam_width, # width
          cropped_webcam_height)) # height
    else:
      render_screen.blit(source=webcam_info.pose_image_surface, dest=render_position_rect)

def get_webcam_and_pose_info(get_pose_results_callback, current_level):
    webcam_img, pose_lines = get_pose_results_callback()
    points_dict = get_xflipped_points_dict_from_lines(pose_lines)

    webcam_pose_image_surface, webcam_pos, webcam_width, webcam_height, render_position_rect = get_webcam_info(webcam_img, current_level)
    head_width, head_height, head_pos = get_head_info(points_dict)

    webcam_info = WebcamInfo(webcam_pose_image_surface, webcam_pos, webcam_width, webcam_height, webcam_img)

    return webcam_info, render_position_rect, head_width, head_height, head_pos, pose_lines, points_dict

def update_game_body(game_limbs, game_heads, current_level, pose_lines, grids, allow_head, head_width, head_height, head_pos, TTL_MAX, level_data):
    game_limbs = remove_dead_game_limbs(game_limbs)
    game_limbs = add_game_limbs(level_data, current_level, pose_lines, grids, game_limbs, TTL_MAX)

    game_heads = remove_dead_game_heads(game_heads)
    game_heads = add_heads(allow_head, head_width, head_height, head_pos, grids, game_heads, TTL_MAX)

    return game_limbs, game_heads



def draw_game(bg_images, current_level, balls, flag, webcam_info: WebcamInfo, render_position_rect, level_lines, game_limbs, game_heads, grids, text, screen_width, screen_height, render_screen, render_font, TTL_MAX):
  draw_background(bg_images)

  if current_level != "level_0":
    draw_balls(balls)

  draw_physics_flag(flag)

  if not (webcam_info.image is None):
    draw_webcam(current_level, webcam_info, render_position_rect)

  for line in level_lines:
    draw_physics_line(line)

  for line, ttl in game_limbs:
    if ttl == TTL_MAX:
      draw_physics_line(line)
  
  draw_heads(game_heads)

  draw_rectangles(webcam_info.pose_image_surface, grids, webcam_info.position)

  # Print level number text
  render_screen.blit(render_font.render(parse(current_level), True, (0, 0, 0)), (0, 0))

  # Print instruction text
  if webcam_info.position:
    render_screen.blit(render_font.render(text, True, (0, 0, 0)), (webcam_info.position[0] + webcam_info.width / 3, screen_height / 2.2))


# --- Main Game Loop ---
def start_game(get_pose_results_callback):

  # --- Generate First Level ---
  levels, current_level, balls, level_lines, flag, bg_images, grids, allow_head, text, is_main_game_loop_running, game_limbs, game_heads, head_width, head_height, head_pos = initialise_game()

  while is_main_game_loop_running:
    ### GET KEYBOARD EVENTS ###
    is_main_game_loop_running = get_events()

    ### GET WEBCAM STATE ###
    webcam_info, render_position_rect, head_width, head_height, head_pos, pose_lines, points_dict = get_webcam_and_pose_info(get_pose_results_callback, current_level)
    
    ### UPDATE GAME STATE ###
    if current_level != "level_0": balls = add_remove_balls(balls)
    game_limbs, game_heads = update_game_body(game_limbs, game_heads, current_level, pose_lines, grids, allow_head, head_width, head_height, head_pos, TTL_MAX, level_data)

    if is_touching_flag(flag, balls) or (current_level == "level_0" and are_arms_above_head(points_dict)):
      current_level = next(levels)
      balls, level_lines, flag, bg_images, grids, allow_head, text = change_level(current_level, balls, level_lines, flag)

    ### DRAW GAME ###
    draw_game(bg_images, current_level, balls, flag, webcam_info, render_position_rect, level_lines, game_limbs, game_heads, grids, text, screen_width, screen_height, render_screen, render_font, TTL_MAX)
    pygame.display.flip()

    ### CLOCK UPDATES ###
    render_clock.tick(60)
    physics_space.step(1 / 60.0)


if __name__ == "__main__":
  start_game()
