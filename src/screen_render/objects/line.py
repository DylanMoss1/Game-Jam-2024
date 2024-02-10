from typing import Tuple
from overrides import override
import pymunk
import pygame
from screen_render.object_properties.renderable import Renderable
from screen_render.object_properties.physical import Physical


class Line(Renderable, Physical):
  def __init__(self, start_position: Tuple[int, int], end_position: Tuple[int, int]) -> None:
    self.start_position = start_position
    self.end_position = end_position
    self.colour = (0, 0, 0)

  @override
  def setup_physics(self, physics_engine) -> None:
    # Create a physics static body
    line_pymonk_static_body = physics_engine.static_body
    # ? line_pymonk_static_body.position = (400, 600)

    # Generate physics segment shape from static body
    line_pymonk_segment_shape = pymunk.Segment(line_pymonk_static_body, self.start_position, self.end_position, 15)
    line_pymonk_segment_shape.elasticity = 1.0
    line_pymonk_segment_shape.color = (100, 200, 0)

    # Add segment shape to pymonk physics engine
    physics_engine.add(line_pymonk_segment_shape)

  @override
  def render(self, render_screen, screen_width, screen_height) -> None:

    start_position_x, start_position_y = self.start_position
    end_position_x, end_position_y = self.end_position

    screen_start_position_x, screen_start_position_y = screen_width * start_position_x, screen_height * start_position_y
    screen_end_position_x, screen_end_position_y = screen_width * end_position_x, screen_height * end_position_y

    pygame.draw.line(render_screen, self.colour, (screen_start_position_x, screen_start_position_y), (screen_end_position_x, screen_end_position_y))
