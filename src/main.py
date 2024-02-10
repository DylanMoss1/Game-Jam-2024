from main_game.main_game import start_game
from pose_detection.pose_detection import start_pose_detection
import threading

pose_results = None, []


def set_pose_results_callback(new_pose_results):
  global pose_results
  pose_results = new_pose_results


def get_pose_results_callback():
  global pose_results
  return pose_results


def main():
  pose_detection_thread = threading.Thread(daemon=True, target=start_pose_detection, args=(set_pose_results_callback,))
  pose_detection_thread.start()

  start_game(get_pose_results_callback)


if __name__ == "__main__":
  main()
