from abc import ABC


class Physical(ABC):

  # Please override when implementing this class
  def setup_physics(self, physics_engine) -> None:
    pass
