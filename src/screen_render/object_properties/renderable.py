from abc import ABC


class Renderable(ABC):

  # Please override when implementing this class
  def render(self, render_screen, screen_width, screen_height) -> None:
    pass
