from app.attendance.attendance_manager import AttendanceManager


def main():

    attendance_manager = AttendanceManager()

    print("===== TEST ĐIỂM DANH =====")

    # Lần 1
    result = attendance_manager.mark_attendance("SV001")

    print(result["message"])

    # Lần 2
    result = attendance_manager.mark_attendance("SV001")

    print(result["message"])

    # Sinh viên khác
    result = attendance_manager.mark_attendance("SV002")

    print(result["message"])


if __name__ == "__main__":
    main()