import dataclasses
import json

import pygame
import pymunk

pygame.init()
render_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

render_clock = pygame.time.Clock()

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

GAME_BODY_TTL_MAX = 1
WEBCAM_SIZE_SCALAR = 1/4

DEBUG_MODE = False

with open('main_game/levels.json', 'r') as file:
  level_data = json.load(file)

@dataclasses.dataclass
class WebcamInfo:
    webcam_surface_rescaled: pygame.Surface
    target_rect_ABS: pygame.Rect
    webcam_rect_rescaled_ABS: pygame.Rect
    webcam_to_target_rescale: float
    raw_image: any

def screen_REL_to_screen_POS_xy(position):
  position_x, position_y = position
  return position_x * screen_width, position_y * screen_height