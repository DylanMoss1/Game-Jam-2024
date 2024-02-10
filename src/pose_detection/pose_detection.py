from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import mediapipe as mp
import cv2
import time

POSE_DETECTION_MODEL_ASSET_PATH = "pose_detection/model/pose_landmarker.task"
previous_detection_results = None, []
results_validity_countdown = 5

connected_landmarks = [(8, 6), (6, 5), (5, 4), (4, 0), (0, 1), (1, 2), (2, 3), (3, 7), (10, 9), (18, 20), (20, 16), (16, 18), (16, 22), (16, 14), (14, 12), (19, 17), (17, 15), (
    15, 19), (15, 21), (15, 13), (13, 11), (12, 11), (12, 24), (11, 23), (24, 23), (24, 26), (26, 28), (28, 32), (32, 30), (30, 28), (23, 25), (25, 27), (27, 29), (29, 31), (31, 27)]


def draw_landmarks_on_image(rgb_image, detection_result):
  pose_landmarks_list = detection_result.pose_landmarks
  annotated_image = np.copy(rgb_image)

  # Loop through the detected poses to visualize.
  for idx in range(len(pose_landmarks_list)):
    pose_landmarks = pose_landmarks_list[idx]

    # Draw the pose landmarks.
    pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    pose_landmarks_proto.landmark.extend([
        landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
        annotated_image,
        pose_landmarks_proto,
        solutions.pose.POSE_CONNECTIONS,
        solutions.drawing_styles.get_default_pose_landmarks_style())

  return annotated_image


def detection_callback(result: mp.tasks.vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
  global previous_detection_results
  global results_validity_countdown

  if result.pose_landmarks:
    results_validity_countdown = 5

    landmark_list = result.pose_landmarks[0]

    pose_line_list = []

    for connection1, connection2 in connected_landmarks:
      landmark1 = landmark_list[connection1]
      landmark2 = landmark_list[connection2]
      pose_line_list.append(((landmark1.x, landmark1.y), (landmark2.x, landmark2.y)))

    previous_detection_results = result, pose_line_list

  else:
    previous_detection_results = None, []


BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=POSE_DETECTION_MODEL_ASSET_PATH),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=detection_callback)


def start_pose_detection(set_pose_results_callback):

  global previous_detection_results
  global results_validity_countdown

  cap = cv2.VideoCapture(0)

  with PoseLandmarker.create_from_options(options) as detector:
    while True:
      # Read a frame from the webcam
      ret, frame = cap.read()

      if not ret:
        continue

      mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

      timestamp = int(round(time.time()*1000))

      # Process the frame with MediaPipe Pose Landmark model.
      detector.detect_async(mp_image, timestamp)
      time.sleep(0.035)

      previous_pose_results, previous_lines_results = previous_detection_results

      if previous_pose_results and results_validity_countdown > 0:

        annotated_image = draw_landmarks_on_image(mp_image.numpy_view(), previous_pose_results)

        bgr_annotated_frame = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
        set_pose_results_callback((bgr_annotated_frame, previous_lines_results))

        results_validity_countdown -= 1
      else:
        set_pose_results_callback((cv2.cvtColor(frame, cv2.COLOR_RGB2BGR), previous_lines_results))

      # Break the loop when 'q' key is pressed
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break

  # Release the webcam and close the OpenCV window
  cap.release()
  cv2.destroyAllWindows()


# import mediapipe as mp
# from mediapipe import solutions
# from mediapipe.framework.formats import landmark_pb2
# import numpy as np
# import cv2
# import pose_detection.pose_detection as posedetect
# import time


# # set_webcam_pose_image_callback_fn = None


# # def callback(result: mp.tasks.vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
# #   # global set_webcam_pose_image_callback_fn

# #   # if result.pose_landmarks:

# #     annotated_frame = posedetect.draw_landmarks_on_image(output_image.numpy_view(), result)
# #     # Convert the frame back to BGR before displaying it.
# #     bgr_annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
# #     set_webcam_pose_image_callback_fn(bgr_annotated_frame)
# #     # print('pose landmarker result: {}'.format(result))


# def start_capture(set_webcam_pose_image_callback):
#   # Open the webcam (default is usually 0, but it might be different depending on your system)

#   # global set_webcam_pose_image_callback_fn

#   # set_webcam_pose_image_callback_fn = set_webcam_pose_image_callback

#   cap = cv2.VideoCapture(0)

#   with posedetect.PoseDetect as landmarker:
#     while True:
#       # Read a frame from the webcam
#       ret, frame = cap.read()

#       # Display the frame
#       # cv2.imshow('Webcam Feed', frame)
#       # q.put(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

#       mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
#       timestamp = int(round(time.time()*1000))

#       # Process the frame with MediaPipe Pose Landmark model.
#       landmarker.detect(mp_image, timestamp)

#       bgr_annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
#       set_webcam_pose_image_callback_fn(bgr_annotated_frame)

#       # Break the loop when 'q' key is pressed
#       if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

#     # Release the webcam and close the OpenCV window
#     cap.release()
#     cv2.destroyAllWindows()


# def draw_landmarks_on_image(rgb_image, detection_result):
#   pose_landmarks_list = detection_result.pose_landmarks
#   annotated_image = np.copy(rgb_image)

#   # Loop through the detected poses to visualize.
#   for idx in range(len(pose_landmarks_list)):
#     pose_landmarks = pose_landmarks_list[idx]

#     # Draw the pose landmarks.
#     pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
#     pose_landmarks_proto.landmark.extend([
#         landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
#     ])
#     solutions.drawing_utils.draw_landmarks(
#         annotated_image,
#         pose_landmarks_proto,
#         solutions.pose.POSE_CONNECTIONS,
#         solutions.drawing_styles.get_default_pose_landmarks_style())
#   return annotated_image


# BaseOptions = mp.tasks.BaseOptions
# PoseLandmarker = mp.tasks.vision.PoseLandmarker
# PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
# PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
# VisionRunningMode = mp.tasks.vision.RunningMode

# # Create a pose landmarker instance with the live stream mode:


# def print_result(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
#     # print('pose landmarker result: {}'.format(result))
#     # Draw the pose landmarks on the frame.
#   if result.pose_landmarks:
#     annotated_frame = draw_landmarks_on_image(output_image.numpy_view(), result)
#     # Convert the frame back to BGR before displaying it.
#     bgr_annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
#     save_path = f'images/output_{timestamp_ms}.jpg'
#     cv2.imwrite(save_path, bgr_annotated_frame)
#     # print(bgr_annotated_frame)
#     # cv2.imshow('MediaPipe Pose Landmarks', bgr_annotated_frame)

#   # Convert the frame received from OpenCV to a MediaPipe’s Image object.
#   # mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_frame_from_opencv)
#   # landmarker.detect_async(mp_image, frame_timestamp_ms)


# class PoseDetect:
#   def __init__(self, callback=print_result):

#     options = PoseLandmarkerOptions(
#         base_options=BaseOptions(model_asset_path=POSE_DETECTION_MODEL_ASSET_PATH),
#         running_mode=VisionRunningMode.LIVE_STREAM,
#         result_callback=callback)

#     self.landmarker = PoseLandmarker.create_from_options(options)

#   def __enter__(self):
#     return self.landmarker

#   def __exit__(self, exc_type, exc_value, traceback):
#     self.landmarker.__exit__(exc_type, exc_value, traceback)
