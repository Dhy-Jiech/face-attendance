from app.face.face_detector import FaceDetector
from app.face.face_processor import FaceProcessor
from app.registration.registration import StudentRegistration
from app.registration.embedding_registration import EmbeddingRegistration
from app.database.database_manager import DatabaseManager
import tkinter as tk

from ui.main_window import MainWindow

class FaceAttendanceApp:

    def __init__(self):

        print("Đang khởi tạo hệ thống...")

        self.database_manager = DatabaseManager()

        self.face_detector = FaceDetector()

        self.face_processor = FaceProcessor()

        self.registration = StudentRegistration(
            self.face_detector,
            self.face_processor
        )

        self.embedding_registration = (
            EmbeddingRegistration(
                self.database_manager
            )
        )

        print("Hệ thống đã sẵn sàng.")

    def register_student(
        self,
        student_code,
        student_name
    ):

        print()
        print("===== ĐĂNG KÝ SINH VIÊN =====")

        # ==============================
        # 1. Kiểm tra dữ liệu đầu vào
        # ==============================

        student_code = student_code.strip()
        student_name = student_name.strip()

        if not student_code:

            return {
                "success": False,
                "message": "MSSV không được để trống."
            }

        if not student_name:

            return {
                "success": False,
                "message": "Họ tên không được để trống."
            }

        print("MSSV:", student_code)
        print("Họ tên:", student_name)

        # ==============================
        # 2. Kiểm tra MSSV đã tồn tại
        # ==============================

        existing_student = (
            self.database_manager
            .get_student_by_code(student_code)
        )

        if existing_student is not None:

            print()
            print("MSSV đã tồn tại.")
            print(
                "Sinh viên:",
                existing_student["full_name"]
            )

            return {
                "success": False,
                "message": (
                    f"MSSV {student_code} đã tồn tại."
                )
            }

        print("MSSV chưa tồn tại.")

        # ==============================
        # 3. Thêm sinh viên vào MySQL
        # ==============================

        student_created = (
            self.database_manager
            .add_student(
                student_code,
                student_name
            )
        )

        if not student_created:

            return {
                "success": False,
                "message": "Không thể thêm sinh viên vào MySQL."
            }

        print("Đã thêm sinh viên vào MySQL.")

        # ==============================
        # 4. Chụp khuôn mặt
        # ==============================

        print()
        print("Bắt đầu đăng ký khuôn mặt...")

        self.registration.register_student(
            student_code,
            student_name
        )

        # ==============================
        # 5. Tạo embedding
        # ==============================

        print()
        print("Đang tạo embedding...")

        self.embedding_registration.create_embeddings(
            student_code
        )

        print()
        print("===== ĐĂNG KÝ HOÀN TẤT =====")

        return {
            "success": True,
            "message": (
                f"Đăng ký sinh viên {student_code} "
                "thành công."
            )
        }

    def close(self):

        self.database_manager.close()


def main():

    app = FaceAttendanceApp()

    root = tk.Tk()

    MainWindow(
        root,
        app
    )

    root.mainloop()

    app.close()


if __name__ == "__main__":
    main()