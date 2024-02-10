import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import cv2

MODEL_ASSET_PATH = "pose_detection/model/pose_landmarker.task"

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

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a pose landmarker instance with the live stream mode:
def print_result(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    # print('pose landmarker result: {}'.format(result))
    # Draw the pose landmarks on the frame.
    if result.pose_landmarks:
        annotated_frame = draw_landmarks_on_image(output_image.numpy_view(), result)
        # Convert the frame back to BGR before displaying it.
        bgr_annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
        save_path = f'images/output_{timestamp_ms}.jpg'
        cv2.imwrite(save_path, bgr_annotated_frame)
        #print(bgr_annotated_frame)
        #cv2.imshow('MediaPipe Pose Landmarks', bgr_annotated_frame)


    # Convert the frame received from OpenCV to a MediaPipe’s Image object.
    # mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_frame_from_opencv)
    # landmarker.detect_async(mp_image, frame_timestamp_ms)

class PoseDetect:
  def __init__(self, callback=print_result):

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_ASSET_PATH),
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=callback)

    self.landmarker = PoseLandmarker.create_from_options(options)

  def __enter__(self):
    return self.landmarker
  def __exit__(self, exc_type, exc_value, traceback):
    self.landmarker.__exit__(exc_type, exc_value, traceback)
