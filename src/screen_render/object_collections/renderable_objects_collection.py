from typing import List, Any
from object_properties.renderable import Renderable


class RenderableObjectsCollection():

  def __init__(self) -> None:
    self.renderable_object_collection: List[Renderable] = []

  def add(self, renderable_object: Renderable) -> None:
    self.renderable_object_collection.append(renderable_object)

  def render_all(self, render_screen, current_screen_width, current_screen_height) -> List[Any]:
    for renderable_object in self.renderable_object_collection:
      renderable_object.render(render_screen, current_screen_width, current_screen_height)
