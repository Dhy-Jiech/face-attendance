import os
import cv2
import numpy as np

from app.recognition.embedding import FaceEmbedding
from app.database.database_manager import DatabaseManager


class EmbeddingRegistration:

    def __init__(self, database_manager):

        self.face_embedding = FaceEmbedding()

        self.database_manager = database_manager

    def create_embeddings(self, student_code):

        folder = os.path.join(
            "data",
            "registered_faces",
            student_code
        )

        if not os.path.exists(folder):

            print(
                "Không tìm thấy thư mục khuôn mặt:",
                folder
            )

            return False

        # =====================================
        # Lấy student_id từ MySQL
        # =====================================

        student_id = (
            self.database_manager
            .get_student_id_by_code(
                student_code
            )
        )

        if student_id is None:

            print(
                "Không tìm thấy sinh viên:",
                student_code
            )

            return False

        print(
            "Student ID:",
            student_id
        )

        # =====================================
        # Đọc ảnh
        # =====================================

        embeddings = []

        files = sorted(
            os.listdir(folder)
        )

        for filename in files:

            if not filename.lower().endswith(
                (".jpg", ".jpeg", ".png")
            ):
                continue

            file_path = os.path.join(
                folder,
                filename
            )

            image = cv2.imread(
                file_path
            )

            if image is None:

                print(
                    "Không thể đọc:",
                    filename
                )

                continue

            image = cv2.resize(
                image,
                (224, 224)
            )

            # =================================
            # FaceNet tạo embedding
            # =================================

            embedding = (
                self.face_embedding
                .extract(image)
            )

            embeddings.append(
                embedding
            )

            print(
                f"Đã tạo embedding: "
                f"{filename}"
            )

        # =====================================
        # Kiểm tra
        # =====================================

        if len(embeddings) == 0:

            print(
                "Không tạo được embedding."
            )

            return False

        embeddings = np.array(
            embeddings,
            dtype=np.float32
        )

        print()
        print(
            "Shape:",
            embeddings.shape
        )

        # =====================================
        # Kiểm tra số chiều
        # =====================================

        if embeddings.shape[1] != 512:

            print(
                "Embedding không có 512 chiều."
            )

            return False

        # =====================================
        # Lưu từng embedding vào MySQL
        # =====================================

        for index, embedding in enumerate(
            embeddings
        ):

            self.database_manager.save_embedding(
                student_id,
                embedding
            )

            print(
                f"Đã lưu MySQL "
                f"{index + 1}/{len(embeddings)}"
            )

        print()
        print(
            "===== LƯU EMBEDDING THÀNH CÔNG ====="
        )

        print(
            "Sinh viên:",
            student_code
        )

        print(
            "Student ID:",
            student_id
        )

        print(
            "Số embedding:",
            len(embeddings)
        )

        return True