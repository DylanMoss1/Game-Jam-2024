from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import mediapipe as mp
import cv2
import time

global set_pose_results_callback_global

POSE_DETECTION_MODEL_ASSET_PATH = "pose_detection/model/pose_landmarker.task"
previous_detection_results = None, []
results_validity_countdown = 5

connected_landmarks = [(20, 4), (19, 4), (4,10), (8,7), (8, 6), (6, 5), (5, 4), (4, 0), (0, 1), (1, 2), (2, 3), (3, 7), (10, 9), (18, 20), (20, 16), (16, 18), (16, 22), (16, 14), (14, 12), (19, 17), (17, 15), (
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
  global set_pose_results_callback_global

  if result.pose_landmarks:
    landmark_list = result.pose_landmarks[0]

    pose_line_list = []

    for connection1, connection2 in connected_landmarks:
      landmark1 = landmark_list[connection1]
      landmark2 = landmark_list[connection2]
      pose_line_list.append(((landmark1.x, landmark1.y, connection1), (landmark2.x, landmark2.y, connection2)))

    annotated_image = draw_landmarks_on_image(output_image.numpy_view(), result)
    # segmentation_mask = result.segmentation_masks[0].numpy_view()
    # visualized_mask = np.repeat(segmentation_mask[:, :, np.newaxis], 3, axis=2) * 255
    bgr_annotated_frame = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
    # bgr_annotated_frame = visualized_mask
    set_pose_results_callback_global((bgr_annotated_frame, pose_line_list))


BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=POSE_DETECTION_MODEL_ASSET_PATH),
    running_mode=VisionRunningMode.LIVE_STREAM,
    output_segmentation_masks=True,
    result_callback=detection_callback)


def start_pose_detection(set_pose_results_callback):

  global set_pose_results_callback_global

  set_pose_results_callback_global = set_pose_results_callback

  cap = cv2.VideoCapture(0)

  with PoseLandmarker.create_from_options(options) as detector:
    timestamp = 0
    while True:
      # Read a frame from the webcam
      ret, frame = cap.read()

      if not ret:
        continue

      mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

      # timestamp = int(time.time() * 1000)
      # timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC))
      timestamp += int(1000 / cap.get(cv2.CAP_PROP_FPS))

      # Process the frame with MediaPipe Pose Landmark model.
      detector.detect_async(mp_image, timestamp)

      if cv2.waitKey(1) & 0xFF == ord('q'):
        break

  # Release the webcam and close the OpenCV window
  cap.release()
  cv2.destroyAllWindows()
