import cv2
import time
import tkinter as tk
from tkinter import messagebox

from app.face.face_detector import FaceDetector
from app.face.face_processor import FaceProcessor
from app.recognition.embedding import FaceEmbedding
from app.recognition.face_recognizer import FaceRecognizer
from app.attendance.realtime_metrics import RealtimeMetricsTracker


class AttendanceWindow:

    def __init__(self, parent, app):

        self.parent = parent
        self.app = app

        # Khởi tạo metrics_tracker nếu chưa có trên app
        if not hasattr(self.app, "metrics_tracker") or self.app.metrics_tracker is None:
            self.app.metrics_tracker = RealtimeMetricsTracker()

        self.window = tk.Toplevel(parent)

        self.window.title(
            "Điểm danh sinh viên & Đánh giá Real-Time"
        )

        self.window.geometry(
            "520x340"
        )

        self.window.resizable(
            False,
            False
        )

        self.running = False

        self.create_interface()

    def create_interface(self):

        title = tk.Label(
            self.window,
            text="ĐIỂM DANH SINH VIÊN",
            font=("Arial", 22, "bold")
        )

        title.pack(
            pady=(25, 15)
        )

        instruction = tk.Label(
            self.window,
            text=(
                "Nhấn BẮT ĐẦU để mở camera điểm danh\n"
                "Hệ thống sẽ tự động đo đạc 2 nhóm chỉ số:\n"
                "1. Hiệu năng Hệ thống Real-Time (FPS, Latency ms, Resource Usage)\n"
                "2. Nghiệp vụ Điểm danh (Time/Student, Transaction Reliability)"
            ),
            font=("Arial", 11),
            justify=tk.CENTER
        )

        instruction.pack(
            pady=10
        )

        start_button = tk.Button(
            self.window,
            text="BẮT ĐẦU ĐIỂM DANH",
            font=("Arial", 13, "bold"),
            bg="#4CAF50",
            fg="white",
            width=25,
            height=2,
            command=self.start_attendance
        )

        start_button.pack(
            pady=15
        )

        cancel_button = tk.Button(
            self.window,
            text="HỦY",
            font=("Arial", 12),
            width=15,
            command=self.cancel
        )

        cancel_button.pack()

    def start_attendance(self):

        if self.running:
            return

        self.running = True

        self.run_camera()

    def run_camera(self):

        face_detector = FaceDetector()
        face_processor = FaceProcessor()
        face_embedding = FaceEmbedding()

        face_recognizer = FaceRecognizer(
            face_embedding,
            self.app.database_manager
        )

        metrics_tracker = self.app.metrics_tracker

        camera = cv2.VideoCapture(0)

        if not camera.isOpened():

            messagebox.showerror(
                "Lỗi",
                "Không thể mở camera."
            )

            self.running = False

            return

        required_time = 1.5

        current_student = None
        recognition_start_time = None

        print()
        print(
            "===== ĐIỂM DANH & ĐÁNH GIÁ REAL-TIME ====="
        )

        while self.running:

            loop_start = time.perf_counter()
            metrics_tracker.tick_frame()

            ret, frame = camera.read()

            if not ret:
                break

            faces = face_detector.detect(
                frame
            )

            if len(faces) == 0:

                current_student = None
                recognition_start_time = None

            for face in faces:

                x, y, w, h = face

                face_image = (
                    face_processor.crop_face(
                        frame,
                        face
                    )
                )

                if face_image is None:
                    continue

                student_code, distance = (
                    face_recognizer.recognize(
                        face_image
                    )
                )

                if student_code is not None:

                    student = (
                        self.app.database_manager
                        .get_student_by_code(
                            student_code
                        )
                    )

                    if student is None:
                        continue

                    student_id = student["id"]
                    student_name = student["full_name"]

                    # Kiểm tra đã điểm danh hôm nay chưa

                    already_attended = (
                        self.app.database_manager
                        .has_attendance_today(
                            student_id
                        )
                    )

                    if already_attended:

                        text = (
                            f"{student_code} - "
                            f"{student_name} | "
                            "Đã điểm danh"
                        )

                        color = (
                            0,
                            255,
                            0
                        )

                        current_student = None
                        recognition_start_time = None

                    else:

                        if student_code != current_student:

                            current_student = student_code

                            recognition_start_time = (
                                time.time()
                            )

                        elapsed_time = (
                            time.time()
                            - recognition_start_time
                        )

                        if elapsed_time < required_time:

                            remaining = (
                                required_time
                                - elapsed_time
                            )

                            text = (
                                f"{student_code} - "
                                f"{student_name} | "
                                f"Xác nhận {remaining:.1f}s"
                            )

                            color = (
                                0,
                                255,
                                255
                            )

                        else:

                            success = (
                                self.app.database_manager
                                .mark_attendance(
                                    student_id
                                )
                            )

                            total_time_taken = time.time() - recognition_start_time
                            metrics_tracker.record_attendance_result(
                                success=success,
                                elapsed_time_sec=total_time_taken,
                                db_success=success
                            )

                            if success:

                                text = (
                                    f"{student_code} - "
                                    f"{student_name} | "
                                    "ĐIỂM DANH THÀNH CÔNG"
                                )

                                print(
                                    student_code,
                                    "-> Điểm danh thành công trong",
                                    f"{total_time_taken:.2f}s"
                                )

                            else:

                                text = (
                                    f"{student_code} | "
                                    "Lỗi lưu điểm danh"
                                )

                            color = (
                                0,
                                255,
                                0
                            )

                            current_student = None
                            recognition_start_time = None

                else:

                    text = "Không nhận diện được"

                    color = (
                        0,
                        0,
                        255
                    )

                    current_student = None
                    recognition_start_time = None

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    color,
                    2
                )

                cv2.putText(
                    frame,
                    text,
                    (
                        x,
                        max(y - 10, 20)
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    color,
                    2
                )

            loop_end = time.perf_counter()
            metrics_tracker.record_latency(loop_end - loop_start)

            # ==========================================
            # Vẽ OSD / HUD Dashboard các chỉ số Real-time
            # ==========================================
            m = metrics_tracker.get_summary_metrics()

            # Background semi-transparent overlay panel
            overlay = frame.copy()
            cv2.rectangle(overlay, (10, 10), (320, 140), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

            cv2.putText(frame, f"FPS: {m['fps']} | Latency: {m['last_latency_ms']} ms", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            cv2.putText(frame, f"CPU: {m['cpu_percent']}% | RAM: {m['ram_mb']} MB", (20, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            cv2.putText(frame, f"GPU: {m['gpu_info']}", (20, 74), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 255), 1)
            cv2.putText(frame, f"Success Rate: {m['attendance_success_rate']}%", (20, 96), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
            cv2.putText(frame, f"Avg Time/Student: {m['avg_time_per_student']}s", (20, 118), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 200, 100), 1)

            cv2.putText(
                frame,
                "Q: Thoat diem danh",
                (20, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "Face Attendance",
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):

                break

        camera.release()

        cv2.destroyAllWindows()

        self.running = False

    def cancel(self):

        self.running = False

        self.window.destroy()
