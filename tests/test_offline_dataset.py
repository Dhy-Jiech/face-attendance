import os
import cv2
import numpy as np
import sys
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Append root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.face.face_detector import FaceDetector
from app.face.face_processor import FaceProcessor
from app.recognition.embedding import FaceEmbedding


class OfflineDatasetEvaluator:
    def __init__(self, threshold=0.65):
        self.threshold = threshold
        print("Đang khởi tạo mô hình Face Detection & FaceNet Embedding...")
        self.face_detector = FaceDetector()
        self.face_processor = FaceProcessor()
        self.face_embedding = FaceEmbedding()
        
        # CSDL lưu tạm trong bộ nhớ RAM: { "SV001": [embedding1, embedding2, ...], ... }
        self.gallery_embeddings = {}

    def load_gallery_from_folders(self, gallery_root="data/registered_faces"):
        """Đọc ảnh từ thư mục đăng ký và tạo embedding lưu vào RAM."""
        print(f"\n[1/2] Đang nạp tập ảnh ĐĂNG KÝ từ: {gallery_root} ...")
        if not os.path.exists(gallery_root):
            print(f"LỖI: Không tìm thấy thư mục {gallery_root}")
            return False

        total_registered_images = 0
        for person_code in sorted(os.listdir(gallery_root)):
            person_folder = os.path.join(gallery_root, person_code)
            if not os.path.isdir(person_folder):
                continue

            self.gallery_embeddings[person_code] = []
            for filename in os.listdir(person_folder):
                if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue
                
                image_path = os.path.join(person_folder, filename)
                image = cv2.imread(image_path)
                if image is None:
                    continue
                
                # Detect & Crop face
                faces = self.face_detector.detect(image)
                if len(faces) == 0:
                    # Nếu không detect được, thử dùng nguyên ảnh (trường hợp ảnh đã crop sẵn)
                    face_image = cv2.resize(image, (160, 160))
                else:
                    face_image = self.face_processor.crop_face(image, faces[0])
                
                if face_image is not None:
                    face_image = cv2.resize(face_image, (160, 160))
                    emb = self.face_embedding.extract(face_image)
                    self.gallery_embeddings[person_code].append(emb)
                    total_registered_images += 1
        
        print(f"-> Đã nạp thành công {total_registered_images} ảnh đăng ký cho {len(self.gallery_embeddings)} đối tượng.")
        return total_registered_images > 0

    def recognize(self, face_image):
        """So sánh 1 khuôn mặt test với tập embedding trong RAM."""
        face_image = cv2.resize(face_image, (160, 160))
        test_emb = self.face_embedding.extract(face_image)
        
        best_person = None
        best_distance = float('inf')

        for person_code, embeddings in self.gallery_embeddings.items():
            for reg_emb in embeddings:
                dist = np.linalg.norm(test_emb - reg_emb)
                if dist < best_distance:
                    best_distance = dist
                    best_person = person_code

        if best_distance <= self.threshold:
            return best_person, best_distance
        return "UNKNOWN", best_distance

    def evaluate_test_folder(self, test_root="data/test_faces"):
        """Đánh giá tập kiểm thử."""
        print(f"\n[2/2] Đang chạy ĐÁNH GIÁ tập TEST từ: {test_root} ...")
        if not os.path.exists(test_root):
            print(f"LỖI: Không tìm thấy thư mục {test_root}")
            return

        y_true = []
        y_pred = []
        total_test_images = 0

        for person_code in sorted(os.listdir(test_root)):
            person_folder = os.path.join(test_root, person_code)
            if not os.path.isdir(person_folder):
                continue

            for filename in os.listdir(person_folder):
                if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue
                
                image_path = os.path.join(person_folder, filename)
                image = cv2.imread(image_path)
                if image is None:
                    continue

                faces = self.face_detector.detect(image)
                if len(faces) == 0:
                    face_image = image
                else:
                    face_image = self.face_processor.crop_face(image, faces[0])
                
                if face_image is None:
                    continue

                pred_person, dist = self.recognize(face_image)
                
                y_true.append(person_code)
                y_pred.append(pred_person)
                total_test_images += 1

                is_correct = "ĐÚNG" if pred_person == person_code else "SAI"
                print(f"  {filename} | Thực tế: {person_code} | Dự đoán: {pred_person} | Khoảng cách: {dist:.4f} | -> {is_correct}")

        if total_test_images == 0:
            print("Không tìm thấy ảnh test hợp lệ nào.")
            return

        # Tính toán các chỉ số
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, average="macro", zero_division=0)
        rec = recall_score(y_true, y_pred, average="macro", zero_division=0)
        f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)

        print("\n========================================")
        print("          KẾT QUẢ ĐÁNH GIÁ OFFLINE")
        print("========================================")
        print(f"Tổng số ảnh test : {total_test_images}")
        print(f"Accuracy         : {acc * 100:.2f}%")
        print(f"Precision        : {prec * 100:.2f}%")
        print(f"Recall           : {rec * 100:.2f}%")
        print(f"F1-Score         : {f1 * 100:.2f}%")
        print("========================================")


if __name__ == "__main__":
    evaluator = OfflineDatasetEvaluator(threshold=0.65)
    
    # 1. Đọc tập đăng ký
    if evaluator.load_gallery_from_folders("data/registered_faces"):
        # 2. Đánh giá tập test
        evaluator.evaluate_test_folder("data/test_faces")
