import time
import os
import collections
import torch

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class RealtimeMetricsTracker:
    """
    Bộ theo dõi và đo đạc các chỉ số Real-Time:
    1. Hiệu năng Hệ thống Real-Time (FPS, Latency ms, Resource Usage CPU/RAM/GPU)
    2. Nghiệp vụ Điểm danh (Attendance Success Rate, Time-per-Student, Transaction Reliability)
    """

    def __init__(self, fps_window=30):
        # FPS Tracking
        self.fps_window = fps_window
        self.frame_timestamps = collections.deque(maxlen=fps_window)
        self.current_fps = 0.0

        # Latency Tracking (ms)
        self.latency_history = collections.deque(maxlen=100)
        self.last_latency_ms = 0.0
        self.avg_latency_ms = 0.0

        # Business Metrics
        self.total_attendance_attempts = 0
        self.successful_attendances = 0
        self.failed_attendances = 0

        self.student_times = []  # Danh sách thời gian điểm danh (giây) từng SV
        self.db_transactions_attempted = 0
        self.db_transactions_successful = 0

        # Current process handle for psutil
        if HAS_PSUTIL:
            self.process = psutil.Process(os.getpid())
        else:
            self.process = None

    def tick_frame(self):
        """Gọi ở đầu mỗi vòng lặp frame camera để tính FPS."""
        now = time.perf_counter()
        self.frame_timestamps.append(now)

        if len(self.frame_timestamps) > 1:
            time_diff = self.frame_timestamps[-1] - self.frame_timestamps[0]
            if time_diff > 0:
                self.current_fps = (len(self.frame_timestamps) - 1) / time_diff
            else:
                self.current_fps = 0.0
        else:
            self.current_fps = 0.0

    def record_latency(self, latency_seconds):
        """Ghi nhận độ trễ xử lý (Inference Latency) của 1 frame theo miligiây."""
        latency_ms = latency_seconds * 1000.0
        self.last_latency_ms = latency_ms
        self.latency_history.append(latency_ms)
        if len(self.latency_history) > 0:
            self.avg_latency_ms = sum(self.latency_history) / len(self.latency_history)

    def get_resource_usage(self):
        """Lấy thông tin tiêu thụ tài nguyên CPU, RAM và GPU."""
        cpu_usage = 0.0
        ram_usage_mb = 0.0
        ram_percent = 0.0

        if HAS_PSUTIL and self.process is not None:
            try:
                cpu_usage = psutil.cpu_percent(interval=None)
                mem_info = self.process.memory_info()
                ram_usage_mb = mem_info.rss / (1024 * 1024)
                ram_percent = psutil.virtual_memory().percent
            except Exception:
                pass

        gpu_info = "N/A (CPU Mode)"
        gpu_usage_pct = 0.0
        if torch.cuda.is_available():
            try:
                allocated = torch.cuda.memory_allocated(0) / (1024 * 1024)
                total = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
                gpu_usage_pct = (allocated / total) * 100.0 if total > 0 else 0.0
                gpu_info = f"{allocated:.1f} MB / {total:.0f} MB ({gpu_usage_pct:.1f}%)"
            except Exception:
                gpu_info = "GPU Available"

        return {
            "cpu_percent": cpu_usage,
            "ram_mb": ram_usage_mb,
            "ram_percent": ram_percent,
            "gpu_info": gpu_info,
            "gpu_percent": gpu_usage_pct
        }

    def record_attendance_result(self, success, elapsed_time_sec=None, db_success=True):
        """
        Ghi nhận kết quả 1 lượt điểm danh:
        - success: Bool (Điểm danh thành công hay thất bại)
        - elapsed_time_sec: Thời gian từ lúc nhận diện đến khi ghi nhận xong (giây)
        - db_success: Bool (Giao dịch CSDL MySQL thành công hay lỗi)
        """
        self.total_attendance_attempts += 1
        self.db_transactions_attempted += 1

        if db_success:
            self.db_transactions_successful += 1

        if success:
            self.successful_attendances += 1
            if elapsed_time_sec is not None and elapsed_time_sec > 0:
                self.student_times.append(elapsed_time_sec)
        else:
            self.failed_attendances += 1

    def get_summary_metrics(self):
        """Trả về dictionary chứa đầy đủ các chỉ số thống kê."""
        res_usage = self.get_resource_usage()

        # Business Metrics calculation
        if self.total_attendance_attempts > 0:
            attendance_success_rate = (self.successful_attendances / self.total_attendance_attempts) * 100.0
        else:
            attendance_success_rate = 100.0 if self.successful_attendances > 0 else 0.0

        if len(self.student_times) > 0:
            avg_time_per_student = sum(self.student_times) / len(self.student_times)
        else:
            avg_time_per_student = 0.0

        if self.db_transactions_attempted > 0:
            transaction_reliability = (self.db_transactions_successful / self.db_transactions_attempted) * 100.0
        else:
            transaction_reliability = 100.0

        return {
            # Real-time System Performance
            "fps": round(self.current_fps, 2),
            "last_latency_ms": round(self.last_latency_ms, 2),
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "cpu_percent": round(res_usage["cpu_percent"], 1),
            "ram_mb": round(res_usage["ram_mb"], 1),
            "ram_percent": round(res_usage["ram_percent"], 1),
            "gpu_info": res_usage["gpu_info"],

            # Attendance Business Metrics
            "total_attempts": self.total_attendance_attempts,
            "successful_attendances": self.successful_attendances,
            "failed_attendances": self.failed_attendances,
            "attendance_success_rate": round(attendance_success_rate, 2),
            "avg_time_per_student": round(avg_time_per_student, 2),
            "db_transactions_attempted": self.db_transactions_attempted,
            "db_transactions_successful": self.db_transactions_successful,
            "transaction_reliability": round(transaction_reliability, 2)
        }

    def generate_report_text(self):
        """Tạo báo cáo dạng văn bản Markdown/Text."""
        m = self.get_summary_metrics()
        report = []
        report.append("==================================================")
        report.append("     BÁO CÁO ĐÁNH GIÁ HIỆU NĂNG REAL-TIME & NGHIỆP VỤ")
        report.append("==================================================")
        report.append("")
        report.append("1. NHÓM CHỈ SỐ HỆ THỐNG THỜI GIAN THỰC (REAL-TIME PERFORMANCE)")
        report.append(f"   • Tốc độ khung hình (FPS)        : {m['fps']} FPS")
        report.append(f"   • Độ trễ xử lý (Inference Latency): {m['last_latency_ms']} ms (Trung bình: {m['avg_latency_ms']} ms)")
        report.append(f"   • Mức tiêu thụ CPU               : {m['cpu_percent']}%")
        report.append(f"   • Mức tiêu thụ RAM               : {m['ram_mb']} MB ({m['ram_percent']}%)")
        report.append(f"   • Mức tiêu thụ GPU               : {m['gpu_info']}")
        report.append("")
        report.append("2. NHÓM CHỈ SỐ NGHIỆP VỤ ĐIỂM DANH (ATTENDANCE BUSINESS METRICS)")
        report.append(f"   • Tổng số lượt xác thực          : {m['total_attempts']}")
        report.append(f"   • Số lượt điểm danh thành công    : {m['successful_attendances']}")
        report.append(f"   • Tỉ lệ điểm danh thành công     : {m['attendance_success_rate']}%")
        report.append(f"   • Thời gian điểm danh TB / sinh viên: {m['avg_time_per_student']} giây/người")
        report.append(f"   • Độ ổn định giao dịch CSDL MySQL: {m['transaction_reliability']}% ({m['db_transactions_successful']}/{m['db_transactions_attempted']} thành công)")
        report.append("==================================================")
        return "\n".join(report)
