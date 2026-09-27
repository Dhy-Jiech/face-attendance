import cv2
import os


class StudentRegistration:

    def __init__(self, face_detector, face_processor):

        self.face_detector = face_detector
        self.face_processor = face_processor

        self.base_path = "data/registered_faces"

    def register_student(self, student_code, student_name):

        student_folder = os.path.join(
            self.base_path,
            student_code
        )

        os.makedirs(
            student_folder,
            exist_ok=True
        )

        camera = cv2.VideoCapture(0)

        if not camera.isOpened():
            print("Không thể mở camera")
            return

        print()
        print("===== ĐĂNG KÝ SINH VIÊN =====")
        print("MSSV:", student_code)
        print("Họ tên:", student_name)
        print()
        print("Đưa khuôn mặt vào camera...")
        print("Nhấn Q để hủy đăng ký.")

        image_count = 0
        max_images = 10

        while image_count < max_images:

            ret, frame = camera.read()

            if not ret:
                print("Không thể đọc camera")
                break

            faces = self.face_detector.detect(frame)

            for face in faces:

                x, y, w, h = face

                # Vẽ khung khuôn mặt
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                face_image = self.face_processor.crop_face(
                    frame,
                    face
                )

                if face_image is not None:

                    image_count += 1

                    filename = os.path.join(
                        student_folder,
                        f"face_{image_count:02d}.jpg"
                    )

                    cv2.imwrite(
                        filename,
                        face_image
                    )

                    print(
                        f"Đã chụp ảnh {image_count}/{max_images}"
                    )

                    # Chỉ chụp một ảnh trong mỗi frame
                    break

            cv2.putText(
                frame,
                f"Images: {image_count}/{max_images}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            cv2.imshow(
                "Student Registration",
                frame
            )

            if cv2.waitKey(300) & 0xFF == ord("q"):
                break

        camera.release()
        cv2.destroyAllWindows()

        print()
        print("Đăng ký ảnh hoàn tất.")
        print("Ảnh được lưu tại:")
        print(student_folder)