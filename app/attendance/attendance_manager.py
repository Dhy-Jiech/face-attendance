from datetime import datetime


class AttendanceManager:

    def __init__(self):
        # Lưu danh sách sinh viên đã điểm danh
        self.attendance_records = {}

    def mark_attendance(self, student_code):

        today = datetime.now().date()

        # Tạo khóa gồm MSSV + ngày
        key = (
            student_code,
            today
        )

        # Kiểm tra đã điểm danh chưa
        if key in self.attendance_records:

            return {
                "success": False,
                "message": "Đã điểm danh hôm nay"
            }

        # Nếu chưa điểm danh → lưu lại
        self.attendance_records[key] = {
            "student_code": student_code,
            "date": today,
            "time": datetime.now().time()
        }

        return {
            "success": True,
            "message": "Điểm danh thành công"
        }