import posedetect
import cv2
import mediapipe as mp
import time
import screen_render.screen_render as screen_render
import threading
import numpy as np
from queue import Queue

def callback(result: mp.tasks.vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
  if result.pose_landmarks:

    annotated_frame = posedetect.draw_landmarks_on_image(output_image.numpy_view(), result)
    # Convert the frame back to BGR before displaying it.
    bgr_annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
    q.put(bgr_annotated_frame)
    #print('pose landmarker result: {}'.format(result))

def start_capture():
  # Open the webcam (default is usually 0, but it might be different depending on your system)
  cap = cv2.VideoCapture(0)
  with posedetect.PoseDetect(callback=callback) as landmarker:
    while True:
      # Read a frame from the webcam
      ret, frame = cap.read()

      # Display the frame
      # cv2.imshow('Webcam Feed', frame)
      # q.put(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

      mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
      timestamp = int(round(time.time()*1000))

      # Process the frame with MediaPipe Pose Landmark model.
      landmarker.detect_async(mp_image, timestamp)
      
      # Break the loop when 'q' key is pressed
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Release the webcam and close the OpenCV window
    cap.release()
    cv2.destroyAllWindows()

q = Queue()
def main():
  capture_thread = threading.Thread(target=start_capture)
  capture_thread.start()
  # Start the game in separate thread
  game_thread = threading.Thread(target=screen_render.start_game, args=(q,))
  game_thread.start()


if __name__ == "__main__":
  main()