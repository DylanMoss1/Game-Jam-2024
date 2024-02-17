
from typing import List, Tuple

import pygame
from pymunk import Body, Poly

from main_game.globals import (BALL_ELASTICITY, BALL_FRICTION, BALL_MASS,
                               BALL_RADIUS, DEBUG_MODE, FLAG_WIDTH,
                               FLAT_POLE_HEIGHT, GAME_BODY_TTL_MAX, WebcamInfo,
                               level_data, physics_space, render_screen,
                               screen_height, screen_REL_to_screen_POS_xy,
                               screen_width)
from main_game.webcam_and_pose_info import (FloatRect,
                                            cropped_webcam_REL_to_screen_ABS,
                                            screen_REL_to_screen_ABS,
                                            uncropped_webcam_REL_to_screen_ABS)


def draw_physics_ball(ball):
  ball_shape, ball_body = ball

  radius = ball_shape.radius
  position = ball_body.position

  pygame.draw.circle(render_screen, "blue", position, radius)


def draw_physics_ellipse(position, width, height):
  pygame.draw.ellipse(render_screen, "blue", pygame.Rect(position[0] - width / 2, position[1] - height / 2, width, height), 1)


def draw_physics_line(line):
  line_shape, _ = line

  start_position = (line_shape.a.x, line_shape.a.y)
  end_position = (line_shape.b.x, line_shape.b.y)

  pygame.draw.line(render_screen, "black", start_position, end_position)


def draw_physics_flag(flag):
  if flag:
    flag_shape, _ = flag

    position_x, position_y = flag_shape.a
    rect = pygame.Rect(position_x, position_y - FLAT_POLE_HEIGHT - FLAG_WIDTH, FLAG_WIDTH, FLAG_WIDTH)
  
    pygame.draw.rect(render_screen, "green", rect)
    pygame.draw.rect(render_screen, "black", rect, width=1)
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
    top_left_scaled = screen_REL_to_screen_POS_xy(top_left)
    bottom_right_scaled = screen_REL_to_screen_POS_xy(bottom_right)
    size_scaled = (bottom_right_scaled[0] - top_left_scaled[0], bottom_right_scaled[1] - top_left_scaled[1])
    image = pygame.transform.scale(image, size_scaled)
    images.append((image, top_left_scaled))
  return images

def draw_background_images(bg_images):
  for image, position in bg_images:
    render_screen.blit(image, position)


def draw_background(bg_images):
    render_screen.fill(color=(255, 255, 255))
    draw_background_images(bg_images)


def draw_balls(balls):
    # Draw any remaining balls
    for ball in balls:
        draw_physics_ball(ball)

def draw_heads(game_heads: List[Tuple[Poly, Body]]):
    for head in game_heads:
        phys_obj, new_head_pos, new_head_width, new_head_height, ttl = head
        # poly_obj, body_obj = head_line # Assuming the physics_object contains position and dimensions
        draw_physics_ellipse(new_head_pos, new_head_width, new_head_height)

def draw_rectangles(webcam_info: WebcamInfo, grids):
  if not (webcam_info.webcam_surface_rescaled is None):
      if DEBUG_MODE:
        test_full = uncropped_webcam_REL_to_screen_ABS(webcam_info, FloatRect().from_xywh(0, 0, 1, 1))
        pygame.draw.rect(render_screen, [255, 255, 0], pygame.Rect(test_full), 3)
      
      for grid in grids:
        gamegrid_rect_screen_REL, camgrid_rect_webcam_REL, colour = grid

        camgrid_rect_screen_ABS = uncropped_webcam_REL_to_screen_ABS(webcam_info, FloatRect().from_xywh(*camgrid_rect_webcam_REL))
        pygame.draw.rect(render_screen, colour, pygame.Rect(camgrid_rect_screen_ABS), 3)

        gamegrid_rect_screen_ABS = screen_REL_to_screen_ABS(FloatRect().from_xywh(*gamegrid_rect_screen_REL))
        pygame.draw.rect(render_screen, colour, pygame.Rect(gamegrid_rect_screen_ABS), 3)

def draw_webcam(current_level, wc: WebcamInfo, render_font):
    cropped_area = pygame.Rect(
        (wc.webcam_rect_rescaled_ABS.width - wc.target_rect_ABS.width) / 2,  # left
        (wc.webcam_rect_rescaled_ABS.height - wc.target_rect_ABS.height) / 2,  # top
        wc.target_rect_ABS.width,  # width
        wc.target_rect_ABS.height)  # height

    render_screen.blit(source=wc.webcam_surface_rescaled, dest=wc.target_rect_ABS, area=cropped_area)

    if DEBUG_MODE:
      pygame.draw.rect(render_screen, "red", wc.target_rect_ABS, 3)
      pygame.draw.rect(render_screen, "blue", wc.webcam_rect_rescaled_ABS, 3)
      pygame.draw.rect(render_screen, "green", cropped_area.move(wc.target_rect_ABS.topleft), 3)


def lvl_to_title(current_level):
  level_int = current_level[6:]
  return f"Level: {level_int}"

def draw_game(bg_images, current_level, balls, flag, webcam_info: WebcamInfo, level_lines, game_limbs, game_heads, grids, text, screen_width, screen_height, render_font):
  draw_background(bg_images)

  if not (webcam_info.raw_image is None):
    draw_webcam(current_level, webcam_info, render_font)

  if level_data[current_level]["spawn_balls"]:
    draw_balls(balls)

  draw_physics_flag(flag)

  for line in level_lines:
    draw_physics_line(line)

  for line, ttl in game_limbs:
    if ttl == GAME_BODY_TTL_MAX:
      draw_physics_line(line)
  
  draw_heads(game_heads)

  if not (webcam_info.webcam_surface_rescaled is None):
    draw_rectangles(webcam_info, grids)

  # Print level number text
  render_screen.blit(render_font.render(lvl_to_title(current_level), True, (0, 0, 0)), (0, 0))

  # Print instruction text
  if not (webcam_info.webcam_rect_rescaled_ABS is None):
    render_screen.blit(render_font.render(text, True, (0, 0, 0)), (webcam_info.target_rect_ABS.left + 20, webcam_info.target_rect_ABS.bottom + 20))