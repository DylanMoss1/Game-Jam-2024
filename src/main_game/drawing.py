
import pygame

from main_game.globals import (BALL_ELASTICITY, BALL_FRICTION, BALL_MASS,
                               BALL_RADIUS, FLAG_WIDTH, FLAT_POLE_HEIGHT,
                               GAME_BODY_TTL_MAX, WebcamInfo, level_data,
                               physics_space, render_screen,
                               scale_positions_to_screen_size, screen_height,
                               screen_width)


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


def draw_background(bg_images):
    render_screen.fill(color=(255, 255, 255))
    #if current_level == "level_0":
    draw_background_images(bg_images)


def draw_balls(balls):
    # Draw any remaining balls
    for ball in balls:
        draw_physics_ball(ball)

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

def lvl_to_title(current_level):
  level_int = current_level[6:]
  return f"Level: {level_int}"

def draw_game(bg_images, current_level, balls, flag, webcam_info: WebcamInfo, render_position_rect, level_lines, game_limbs, game_heads, grids, text, screen_width, screen_height, render_font):
  draw_background(bg_images)

  if current_level != "level_0":
    draw_balls(balls)

  draw_physics_flag(flag)

  if not (webcam_info.image is None):
    draw_webcam(current_level, webcam_info, render_position_rect)

  for line in level_lines:
    draw_physics_line(line)

  for line, ttl in game_limbs:
    if ttl == GAME_BODY_TTL_MAX:
      draw_physics_line(line)
  
  draw_heads(game_heads)

  draw_rectangles(webcam_info.pose_image_surface, grids, webcam_info.position)

  # Print level number text
  render_screen.blit(render_font.render(lvl_to_title(current_level), True, (0, 0, 0)), (0, 0))

  # Print instruction text
  if webcam_info.position:
    render_screen.blit(render_font.render(text, True, (0, 0, 0)), (webcam_info.position[0] + webcam_info.width / 3, screen_height / 2.2))