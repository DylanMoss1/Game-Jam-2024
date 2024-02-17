from typing import List, Tuple

from pymunk import Body, Poly, Segment

from main_game.globals import (BALL_ELASTICITY, BALL_FRICTION, BALL_MASS,
                               BALL_RADIUS, FLAG_WIDTH, FLAT_POLE_HEIGHT,
                               GAME_BODY_TTL_MAX, WebcamInfo, level_data,
                               physics_space, render_clock, render_font,
                               screen_height, screen_REL_to_screen_POS_xy,
                               screen_width)
from main_game.physics_objects import add_physics_ellipse, add_physics_line
from main_game.webcam_and_pose_info import (cropped_webcam_REL_to_screen_ABS,
                                            screen_REL_to_screen_ABS)
from utils.clip_lines_within_box import line_clip
from utils.scale_and_translate_ellipse import scale_and_translate_ellipse
from utils.scale_and_translate_lines import scale_and_translate_lines


def update_game_body(game_limbs, game_heads, current_level, pose_lines, grids, allow_head, head_width, head_height, head_pos, level_data):
    game_limbs = remove_dead_game_limbs(game_limbs)
    game_limbs = add_game_limbs(level_data, current_level, pose_lines, grids, game_limbs)

    game_heads = remove_dead_game_heads(game_heads)
    game_heads = add_heads(allow_head, head_width, head_height, head_pos, grids, game_heads)

    return game_limbs, game_heads

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

  for head, new_head_pos, new_head_width, new_head_height, ttl in game_heads:
    if ttl <= 0:
      physics_space.remove(*head)
    else:
      new_game_heads.append((head, new_head_pos, new_head_width, new_head_height, ttl - 1))

  return new_game_heads


def add_game_limbs(level_data, current_level, pose_lines, grids, game_limbs: List[Tuple[Tuple[Segment, Body], int]]):
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
          game_position, webcam_position, colour = grid

          left, top, width, height = webcam_position
          game_left, game_top, game_width, game_height = game_position

          clipped_line = line_clip(((1 - start_position_x, start_position_y), (1 - end_position_x, end_position_y)), ((left, top), (left + width, top + height)))
          if clipped_line:
            start_pos, end_pos = scale_and_translate_lines([clipped_line], ((left, top), (left + width, top + height)),
                                                           ((game_left, game_top), (game_left + game_width, game_top + game_height)))[0]

            line = add_physics_line(start_pos, end_pos)
            game_limbs.append((line, GAME_BODY_TTL_MAX))
    
    return game_limbs


def add_heads(allow_head, head_width, head_height, head_pos, grids, game_heads):
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
                new_head_pos = screen_REL_to_screen_POS_xy(new_head_pos)
                new_head_width, new_head_height = screen_REL_to_screen_POS_xy((new_head_width, new_head_height))

                # Add head to the physics space and keep the reference for drawing
                game_heads.append((add_physics_ellipse(new_head_pos, new_head_width, new_head_height), new_head_pos, new_head_width, new_head_height, GAME_BODY_TTL_MAX))
    return game_heads