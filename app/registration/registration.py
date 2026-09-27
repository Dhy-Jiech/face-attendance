import cv2
import os


class StudentRegistration:

    def __init__(self, face_detector, face_processor):

        self.face_detector = face_detector
        self.face_processor = face_processor

        self.base_path = "data/registered_faces"

        self.instructions = [
            "Nhin thang camera",
            "Nhin thang - bieu cam tu nhien",
            "Quay mat nhe sang TRAI",
            "Quay mat nhe sang PHAI",
            "Nhin hoi len",
            "Nhin hoi xuong",
            "Quay nhe sang TRAI",
            "Quay nhe sang PHAI",
            "Tu nhien",
            "Nhin thang camera"
        ]

    def register_student(
        self,
        student_code,
        student_name
    ):

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

            print("Khong the mo camera")

            return False

        print()
        print("===== DANG KY KHUON MAT =====")
        print("MSSV:", student_code)
        print("Ho ten:", student_name)
        print()
        print("SPACE : chup anh")
        print("Q     : huy dang ky")
        print()

        image_count = 0
        max_images = 10

        while image_count < max_images:

            ret, frame = camera.read()

            if not ret:

                print("Khong the doc camera")

                camera.release()
                cv2.destroyAllWindows()

                return False

            faces = self.face_detector.detect(frame)

            if len(faces) == 1:

                face = faces[0]

                x, y, w, h = face

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                face_image = (
                    self.face_processor.crop_face(
                        frame,
                        face
                    )
                )

                instruction = (
                    self.instructions[image_count]
                )

                cv2.putText(
                    frame,
                    f"Anh {image_count + 1}/{max_images}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    instruction,
                    (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    "SPACE: Chup | Q: Huy",
                    (20, 110),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                cv2.imshow(
                    "Student Registration",
                    frame
                )

                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):

                    camera.release()
                    cv2.destroyAllWindows()

                    print("Da huy dang ky.")

                    return False

                if key == 32:

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
                            f"Da chup anh "
                            f"{image_count}/{max_images}"
                        )

            else:

                cv2.putText(
                    frame,
                    "Can co dung 1 khuon mat",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

                cv2.imshow(
                    "Student Registration",
                    frame
                )

                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):

                    camera.release()
                    cv2.destroyAllWindows()

                    print("Da huy dang ky.")

                    return False

        camera.release()
        cv2.destroyAllWindows()

        print()
        print("===== DANG KY KHUON MAT THANH CONG =====")
        print("Da chup:", image_count, "anh")

        return True