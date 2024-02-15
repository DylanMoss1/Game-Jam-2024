import math

import numpy as np
import pygame

from main_game.globals import (WebcamInfo, level_data, render_screen,
                               scale_positions_to_screen_size, screen_height,
                               screen_width)


def get_webcam_and_pose_info(get_pose_results_callback, current_level):
    webcam_img, pose_lines = get_pose_results_callback()
    points_dict = get_xflipped_points_dict_from_lines(pose_lines)

    webcam_pose_image_surface, webcam_pos, webcam_width, webcam_height, render_position_rect = get_webcam_info(webcam_img, current_level)
    head_width, head_height, head_pos = get_head_info(points_dict)

    webcam_info = WebcamInfo(webcam_pose_image_surface, webcam_pos, webcam_width, webcam_height, webcam_img)

    return webcam_info, render_position_rect, head_width, head_height, head_pos, pose_lines, points_dict

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

