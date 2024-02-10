from typing import List, Any
from screen_render.object_properties.physical import Physical


class PhysicalObjectsCollection():

  def __init__(self) -> None:
    self.physical_object_collection: List[Physical] = []

  def add(self, physical_object: Physical) -> None:
    self.physical_object_collection.append(physical_object)

  def setup_physics_on_all(self, physics_engine) -> List[Any]:
    for physical_object in self.physical_object_collection:
      physical_object.setup_physics(physics_engine)
