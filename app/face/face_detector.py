import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class FaceDetector:

    def __init__(
        self,
        model_path="app/face/models/blaze_face_short_range.tflite"
    ):

        # ==========================================
        # 1. Load BlazeFace model
        # ==========================================

        base_options = python.BaseOptions(
            model_asset_path=model_path
        )

        # ==========================================
        # 2. Cấu hình Face Detector
        # ==========================================

        options = vision.FaceDetectorOptions(
            base_options=base_options,

            # Chỉ lấy khuôn mặt có độ tin cậy >= 0.6
            min_detection_confidence=0.6
        )

        # ==========================================
        # 3. Khởi tạo detector
        # ==========================================

        self.detector = (
            vision.FaceDetector.create_from_options(
                options
            )
        )

    def detect(self, frame):

        # ==========================================
        # frame từ OpenCV là BGR
        # MediaPipe cần RGB
        # ==========================================

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # ==========================================
        # Detect khuôn mặt
        # ==========================================

        result = self.detector.detect(
            mp_image
        )

        faces = []

        for detection in result.detections:

            bbox = detection.bounding_box

            x = bbox.origin_x
            y = bbox.origin_y
            w = bbox.width
            h = bbox.height

            faces.append(
                (x, y, w, h)
            )

        return faces