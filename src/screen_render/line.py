from typing import Tuple
import pymunk


class Line():
  def __init__(self, start_position: Tuple[int, int], end_position: Tuple[int, int], pymonk_physics_space) -> None:
    
    # Create a physics static body 
    line_pymonk_static_body = pymonk_physics_space.static_body
    #? line_pymonk_static_body.position = (400, 600)

    # Generate physics segment shape from static body 
    line_pymonk_segment_shape = pymunk.Segment(line_pymonk_static_body, start_position, end_position, 15)
    line_pymonk_segment_shape.elasticity = 1.0
    line_pymonk_segment_shape.color = (100, 200, 0)

    # Add segment shape to pymonk physics engine 
    pymonk_physics_space.add(line_pymonk_segment_shape)

    # Return segment shape 
    return line_pymonk_segment_shape
