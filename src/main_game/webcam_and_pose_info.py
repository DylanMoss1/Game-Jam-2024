import math

import numpy as np
import pygame

from main_game.globals import (WebcamInfo, level_data, render_screen,
                               screen_height, screen_REL_to_screen_POS_xy,
                               screen_width)


class FloatRect:
    def from_xywh(self, x, y, width, height):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.topleft = (self.x, self.y)
        self.bottomright = (self.x + self.width, self.y + self.height)
        self.left = self.x
        self.top = self.y
        self.right = self.x + self.width
        self.bottom = self.y + self.height
        return self
    
    def from_tlbr(self, topleft, bottomright):
        self.x = float(topleft[0])
        self.y = float(topleft[1])
        self.width = float(bottomright[0] - topleft[0])
        self.height = float(bottomright[1] - topleft[1])
        self.topleft = topleft
        self.bottomright = bottomright
        self.left = self.x
        self.top = self.y
        self.right = self.x + self.width
        self.bottom = self.y + self.height
        return self
      

def get_webcam_and_pose_info(get_pose_results_callback, current_level):
    webcam_img, pose_lines = get_pose_results_callback()
    points_dict = get_xflipped_points_dict_from_lines(pose_lines)

    webcam_info = get_webcam_info(webcam_img, current_level)
    head_width, head_height, head_pos = get_head_info(points_dict)

    return webcam_info, head_width, head_height, head_pos, pose_lines, points_dict

def screen_REL_to_screen_ABS(rect_REL: FloatRect):
    target_top_left_ABS = screen_REL_to_screen_POS_xy(tuple(rect_REL.topleft))
    target_bottom_right_ABS = screen_REL_to_screen_POS_xy(tuple(rect_REL.bottomright))
    target_width_ABS = target_bottom_right_ABS[0] - target_top_left_ABS[0]
    target_height_ABS = target_bottom_right_ABS[1] - target_top_left_ABS[1]
    return pygame.Rect(target_top_left_ABS, (target_width_ABS, target_height_ABS))

def cropped_webcam_REL_to_screen_ABS(webcam_info: WebcamInfo, rect_REL: FloatRect):
    target_top_left_ABS = (webcam_info.target_rect_ABS.left + rect_REL.left * webcam_info.target_rect_ABS.width, webcam_info.target_rect_ABS.top + rect_REL.top * webcam_info.target_rect_ABS.height)
    target_width_ABS = rect_REL.width * webcam_info.target_rect_ABS.width
    target_height_ABS = rect_REL.height * webcam_info.target_rect_ABS.height
    return pygame.Rect(target_top_left_ABS, (target_width_ABS, target_height_ABS))

def uncropped_webcam_REL_to_screen_ABS(wc: WebcamInfo, rect_REL: FloatRect):
    uncropped_area_ABS = pygame.Rect(
        wc.webcam_rect_rescaled_ABS.left - (wc.webcam_rect_rescaled_ABS.width - wc.target_rect_ABS.width) / 2,
        wc.webcam_rect_rescaled_ABS.top - (wc.webcam_rect_rescaled_ABS.height - wc.target_rect_ABS.height) / 2,
        wc.webcam_rect_rescaled_ABS.width,
        wc.webcam_rect_rescaled_ABS.height)
    target_top_left_ABS = (uncropped_area_ABS.left + rect_REL.left * uncropped_area_ABS.width, uncropped_area_ABS.top + rect_REL.top * uncropped_area_ABS.height)
    target_width_ABS = rect_REL.width * uncropped_area_ABS.width
    target_height_ABS = rect_REL.height * uncropped_area_ABS.height
    return pygame.Rect(target_top_left_ABS, (target_width_ABS, target_height_ABS))

def get_webcam_info(webcam_img, current_level):
    if webcam_img is None: return WebcamInfo(None, None, None, None, None)

    webcam_pose_arr = np.array(webcam_img)
    # For some reason the image is rotated 90 degrees
    webcam_pose_arr = np.rot90(webcam_pose_arr)
    webcam_pose_image_surface = pygame.surfarray.make_surface(webcam_pose_arr)

    # Dynamically calculate the webcam position and size
    # Assumisition data from the JSON structure
    target_rect_REL = FloatRect().from_tlbr(level_data[current_level]["webcam_pos"]["start_pos"], level_data[current_level]["webcam_pos"]["end_pos"])

    target_rect_ABS = screen_REL_to_screen_ABS(target_rect_REL)

    # rescale to be no smaller than min(width, height)
    webcam_to_target_rescale = max(target_rect_ABS.width / webcam_pose_image_surface.get_width(), target_rect_ABS.height / webcam_pose_image_surface.get_height())
    webcam_pose_image_surface = pygame.transform.scale(webcam_pose_image_surface, (int(webcam_pose_image_surface.get_width() * webcam_to_target_rescale), int(webcam_pose_image_surface.get_height() * webcam_to_target_rescale)))

    target_width_scaled_ABS = webcam_pose_image_surface.get_width()
    target_height_scaled_ABS = webcam_pose_image_surface.get_height()

    target_rect_ABS = pygame.Rect(target_rect_ABS.topleft, (target_rect_ABS.width, target_rect_ABS.height))
    target_rect_scaled_ABS = pygame.Rect(target_rect_ABS.topleft, (target_width_scaled_ABS, target_height_scaled_ABS))

    webcam_info = WebcamInfo(webcam_pose_image_surface, target_rect_ABS, target_rect_scaled_ABS, webcam_to_target_rescale, webcam_img)

    return webcam_info

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

