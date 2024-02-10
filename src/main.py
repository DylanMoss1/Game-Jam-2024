from main_game.main_game import start_game
from pose_detection.pose_detection import start_pose_detection
import threading

webcam_pose_image = None


def set_webcam_pose_image_callback(new_webcam_pose_image):
  global webcam_pose_image
  webcam_pose_image = new_webcam_pose_image


def get_webcam_pose_image_callback():
  global webcam_pose_image
  return webcam_pose_image


def main():
  pose_detection_thread = threading.Thread(target=start_pose_detection, args=(set_webcam_pose_image_callback,))
  pose_detection_thread.start()

  game_thread = threading.Thread(target=start_game, args=(get_webcam_pose_image_callback,))
  game_thread.start()


if __name__ == "__main__":
  main()


# import pose_detection.posedetect as posedetect
# import cv2
# import mediapipe as mp
# import time
# import screen_render.screen_render as screen_render
# import threading
# import numpy as np
# from queue import Queue

# q = None


# def callback(result: mp.tasks.vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
#   global q

#   if result.pose_landmarks:

#     annotated_frame = posedetect.draw_landmarks_on_image(output_image.numpy_view(), result)
#     # Convert the frame back to BGR before displaying it.
#     bgr_annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
#     q = bgr_annotated_frame
#     # print('pose landmarker result: {}'.format(result))


# def start_capture():
#   # Open the webcam (default is usually 0, but it might be different depending on your system)
#   cap = cv2.VideoCapture(0)
#   with posedetect.PoseDetect(callback=callback) as landmarker:
#     while True:
#       # Read a frame from the webcam
#       ret, frame = cap.read()

#       # Display the frame
#       # cv2.imshow('Webcam Feed', frame)
#       # q.put(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

#       mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
#       timestamp = int(round(time.time()*1000))

#       # Process the frame with MediaPipe Pose Landmark model.
#       landmarker.detect_async(mp_image, timestamp)

#       # Break the loop when 'q' key is pressed
#       if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

#     # Release the webcam and close the OpenCV window
#     cap.release()
#     cv2.destroyAllWindows()


# def main():
#   capture_thread = threading.Thread(target=start_capture)
#   capture_thread.start()
#   # Start the game in separate thread
#   game_thread = threading.Thread(target=screen_render.start_game, args=(q,))
#   game_thread.start()


# if __name__ == "__main__":
#   main()
