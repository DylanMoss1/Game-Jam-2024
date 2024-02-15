import json
import math
import random
from dataclasses import dataclass

import numpy as np
import pygame
import pymunk
import pymunk.pygame_util
from pygame.locals import *

from main_game.drawing import draw_game, load_and_scale_background_images
from main_game.game_body import update_game_body
from main_game.globals import (WebcamInfo, level_data, physics_space,
                               render_clock, render_font, screen_height,
                               screen_width)
from main_game.physics_objects import (add_physics_ball, add_physics_flag,
                                       add_physics_lines_from_position_list,
                                       add_remove_balls, is_touching_flag,
                                       remove_dead_balls)
from main_game.webcam_and_pose_info import (are_arms_above_head,
                                            get_webcam_and_pose_info)

# --- Load level data from JSON ---

def level_generator():
  levels_list = list(level_data.keys())
  n = 0
  while True:
    yield levels_list[n]
    n = (n + 1) % len(levels_list)
    if n == 0:
      n = 1

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

  balls = [add_physics_ball(tuple(level_info["ball_pos"]))]
  level_lines = add_physics_lines_from_position_list(level_info["line_pos"])
  flag = add_physics_flag(tuple(level_info["flag_pos"]))
  bg_images = load_and_scale_background_images(current_level)
  grids = parse_grids(level_info["grids"])
  text = level_info["instruction"]
  allow_head = level_info["allow_head"]

  return balls, level_lines, flag, bg_images, grids, allow_head, text

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

    head_width = None
    head_height = None
    head_pos = None

    return levels, current_level, balls, level_lines, flag, bg_images, grids, allow_head, text, is_main_game_loop_running, game_limbs, game_heads, head_width, head_height, head_pos

def get_events():
  is_main_game_loop_running = True
  for event in pygame.event.get():
        if event.type == pygame.QUIT:
          is_main_game_loop_running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          is_main_game_loop_running = False
  return is_main_game_loop_running


# --- Main Game Loop ---
def start_game(get_pose_results_callback):

  levels, current_level, balls, level_lines, flag, bg_images, grids, allow_head, text, is_main_game_loop_running, game_limbs, game_heads, head_width, head_height, head_pos = initialise_game()

  while is_main_game_loop_running:
    ### GET KEYBOARD EVENTS ###
    is_main_game_loop_running = get_events()

    ### GET WEBCAM STATE ###
    webcam_info, render_position_rect, head_width, head_height, head_pos, pose_lines, points_dict = get_webcam_and_pose_info(get_pose_results_callback, current_level)
    
    ### UPDATE GAME STATE ###
    if current_level != "level_0": balls = add_remove_balls(balls)
    game_limbs, game_heads = update_game_body(game_limbs, game_heads, current_level, pose_lines, grids, allow_head, head_width, head_height, head_pos, level_data)

    if is_touching_flag(flag, balls) or (current_level == "level_0" and are_arms_above_head(points_dict)):
      current_level = next(levels)
      balls, level_lines, flag, bg_images, grids, allow_head, text = change_level(current_level, balls, level_lines, flag)

    ### DRAW GAME ###
    draw_game(bg_images, current_level, balls, flag, webcam_info, render_position_rect, level_lines, game_limbs, game_heads, grids, text, screen_width, screen_height, render_font)
    pygame.display.flip()

    ### CLOCK UPDATES ###
    render_clock.tick(60)
    physics_space.step(1 / 60.0)


if __name__ == "__main__":
  start_game()
