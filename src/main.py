import posedetect
import cv2
import mediapipe as mp
import time

def callback(result: mp.tasks.vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
  if result.pose_landmarks:
    print('pose landmarker result: {}'.format(result))

def start_capture():
  # Open the webcam (default is usually 0, but it might be different depending on your system)
  cap = cv2.VideoCapture(0)
  with posedetect.PoseDetect(callback=callback) as landmarker:
    while True:
      # Read a frame from the webcam
      ret, frame = cap.read()

      # Display the frame
      #cv2.imshow('Webcam Feed', frame)

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

def main():
  start_capture()

if __name__ == "__main__":
  main()