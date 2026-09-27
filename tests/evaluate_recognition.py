from networkx.generators import spectral_graph_forge
import os
import cv2
import numpy as np
import sys


sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

from app.recognition.embedding import FaceEmbedding
from app.recognition.face_recognizer import FaceRecognizer
from app.database.database_manager import DatabaseManager
from app.face.face_detector import FaceDetector
from app.face.face_processor import FaceProcessor


class RecognitionEvaluator:

    def __init__(self, threshold=0.65):

        self.threshold = threshold

        self.database_manager = DatabaseManager()

        self.face_detector = FaceDetector()
        self.face_processor = FaceProcessor()

        self.face_embedding = FaceEmbedding()

        self.face_recognizer = FaceRecognizer(
            self.face_embedding,
            self.database_manager,
            threshold=self.threshold
        )
    def evaluate(self):

        test_root = "data/test_faces"

        if not os.path.exists(test_root):
            raise FileNotFoundError(
                f"Không tìm thấy thư mục test: {test_root}"
            )

        y_true = []
        y_pred = []

        total_images = 0

        print()
        print("========================================")
        print("       ĐÁNH GIÁ HỆ THỐNG NHẬN DIỆN")
        print("========================================")
        print()

        for student_code in sorted(os.listdir(test_root)):

            student_folder = os.path.join(
                test_root,
                student_code
            )

            if not os.path.isdir(student_folder):
                continue

            print(f"Sinh viên: {student_code}")

            for filename in sorted(
                os.listdir(student_folder)
            ):

                if not filename.lower().endswith(
                    (".jpg", ".jpeg", ".png")
                ):
                    continue

                image_path = os.path.join(
                    student_folder,
                    filename
                )

                image = cv2.imread(image_path)

                if image is None:
                    print(
                        f"  Không đọc được: {filename}"
                    )
                    continue

                # ==============================
                # 1. Phát hiện khuôn mặt
                # ==============================

                faces = self.face_detector.detect(image)

                if len(faces) == 0:

                    print(
                        f"  {filename} | "
                        f"Không phát hiện khuôn mặt"
                    )

                    continue


                # ==============================
                # 2. Lấy khuôn mặt đầu tiên
                # ==============================

                face = faces[0]


                # ==============================
                # 3. Crop + resize khuôn mặt
                # ==============================

                face_image = self.face_processor.crop_face(
                    image,
                    face
                )

                if face_image is None:

                    print(
                        f"  {filename} | "
                        f"Không crop được khuôn mặt"
                    )

                    continue


                # ==============================
                # 4. Nhận diện bằng FaceNet
                # ==============================

                total_images += 1

                predicted_student, distance = (
                    self.face_recognizer.recognize(
                        face_image
                    )
                )


                # ==============================
                # 5. Kiểm tra kết quả
                # ==============================

                if predicted_student is None:

                    predicted_student = "UNKNOWN"

                y_true.append(student_code)

                y_pred.append(predicted_student)

                result = (
                    "ĐÚNG"
                    if predicted_student == student_code
                    else "SAI"
                )

                print(
                    f"  {filename} | "
                    f"Dự đoán: {predicted_student} | "
                    f"Distance: {distance:.4f} | "
                    f"{result}"
                )

        if total_images == 0:
            raise ValueError(
                "Không tìm thấy ảnh test."
            )

        accuracy = accuracy_score(
            y_true,
            y_pred
        )

        precision = precision_score(
            y_true,
            y_pred,
            average="macro",
            zero_division=0
        )

        recall = recall_score(
            y_true,
            y_pred,
            average="macro",
            zero_division=0
        )

        f1 = f1_score(
            y_true,
            y_pred,
            average="macro",
            zero_division=0
        )

        correct = sum(
            true == pred
            for true, pred in zip(
                y_true,
                y_pred
            )
        )

        wrong = total_images - correct

        matrix_labels = sorted(
            set(y_true) | set(y_pred)
        )

        matrix = confusion_matrix(
            y_true,
            y_pred,
            labels=matrix_labels
        )

        print()
        print("========================================")
        print("             KẾT QUẢ")
        print("========================================")

        print(
            f"Tổng số ảnh test : {total_images}"
        )

        print(
            f"Nhận diện đúng   : {correct}"
        )

        print(
            f"Nhận diện sai    : {wrong}"
        )

        print(
            f"Accuracy         : {accuracy * 100:.2f}%"
        )

        print(
            f"Precision        : {precision * 100:.2f}%"
        )

        print(
            f"Recall           : {recall * 100:.2f}%"
        )

        print(
            f"F1-score         : {f1 * 100:.2f}%"
        )

        print()
        print("Confusion Matrix:")
        print(matrix)

        print("========================================")

        return {
            "total": total_images,
            "correct": correct,
            "wrong": wrong,
            "accuracy": accuracy * 100,
            "precision": precision * 100,
            "recall": recall * 100,
            "f1": f1 * 100,
            "labels": matrix_labels,
            "confusion_matrix": matrix
        }

    def close(self):

        self.database_manager.close()


if __name__ == "__main__":

    evaluator = RecognitionEvaluator(
        threshold=0.65
    )

    try:
        evaluator.evaluate()

    finally:
        evaluator.close()