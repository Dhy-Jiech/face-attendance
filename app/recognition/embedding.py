import numpy as np
import torch
import cv2
from facenet_pytorch import InceptionResnetV1


class FaceEmbedding:

    def __init__(self):

        print("Đang tải FaceNet...")

        # Chọn GPU nếu có, nếu không dùng CPU
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        # FaceNet - InceptionResnetV1
        self.model = InceptionResnetV1(
            pretrained="vggface2"
        ).eval().to(self.device)

        print("FaceNet đã sẵn sàng.")
        print("Device:", self.device)

    def extract(self, face_image):

        # ==========================================
        # 1. BGR → RGB
        # ==========================================

        face_image = cv2.cvtColor(
            face_image,
            cv2.COLOR_BGR2RGB
        )

        # ==========================================
        # 2. Chuyển sang float32
        # ==========================================

        image = face_image.astype(
            np.float32
        )

        # ==========================================
        # 3. Normalize theo FaceNet
        # Pixel [0, 255]
        #       ↓
        # khoảng [-1, 1]
        # ==========================================

        image = (
            image - 127.5
        ) / 128.0

        # ==========================================
        # 4. HWC → CHW
        #
        # OpenCV:
        # (height, width, channel)
        #
        # PyTorch:
        # (channel, height, width)
        # ==========================================

        image = np.transpose(
            image,
            (2, 0, 1)
        )

        # ==========================================
        # 5. NumPy → PyTorch Tensor
        # ==========================================

        image = torch.from_numpy(
            image
        ).unsqueeze(0)

        # Shape:
        # (1, 3, 160, 160)

        image = image.to(
            self.device
        )

        # ==========================================
        # 6. FaceNet tạo embedding
        # ==========================================

        with torch.no_grad():

            embedding = self.model(
                image
            )

        # ==========================================
        # 7. Tensor → NumPy
        # ==========================================

        return embedding.cpu().numpy()[0]