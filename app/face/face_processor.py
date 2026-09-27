import cv2


class FaceProcessor:

    def __init__(
        self,
        image_size=(160, 160),
        margin=0.25
    ):
        self.image_size = image_size
        self.margin = margin

    def crop_face(self, frame, face):

        x, y, w, h = face

        height, width, _ = frame.shape

        # ==========================================
        # 1. Mở rộng bounding box
        # ==========================================

        margin_x = int(w * self.margin)
        margin_y = int(h * self.margin)

        x1 = max(
            0,
            x - margin_x
        )

        y1 = max(
            0,
            y - margin_y
        )

        x2 = min(
            width,
            x + w + margin_x
        )

        y2 = min(
            height,
            y + h + margin_y
        )

        # ==========================================
        # 2. Crop khuôn mặt
        # ==========================================

        face_image = frame[
            y1:y2,
            x1:x2
        ]

        if face_image.size == 0:
            return None

        # ==========================================
        # 3. Resize về 160 × 160
        # ==========================================

        face_image = cv2.resize(
            face_image,
            self.image_size,
            interpolation=cv2.INTER_AREA
        )

        return face_image