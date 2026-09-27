import mysql.connector
import json
from datetime import datetime
class DatabaseManager:

    def __init__(self):

        self.connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="123456789",
            database="face_attendance"
        )

        print("Đã kết nối MySQL thành công.")
    def has_attendance_today(self, student_id):

        cursor = self.connection.cursor()

        sql = """
            SELECT COUNT(*)
            FROM attendance
            WHERE student_id = %s
            AND attendance_date = %s
        """

        today = datetime.now().date()

        cursor.execute(
            sql,
            (
                student_id,
                today
            )
        )

        result = cursor.fetchone()

        cursor.close()

        return result[0] > 0
    def mark_attendance(self, student_id):

        cursor = self.connection.cursor()

        now = datetime.now()

        sql = """
            INSERT INTO attendance (
                student_id,
                attendance_date,
                attendance_time,
                status
            )
            VALUES (%s, %s, %s, %s)
        """

        values = (
            student_id,
            now.date(),
            now.time(),
            "PRESENT"
        )

        try:

            cursor.execute(
                sql,
                values
            )

            self.connection.commit()

            cursor.close()

            return True

        except Exception as e:

            self.connection.rollback()

            cursor.close()

            print(
                "Lỗi lưu điểm danh:",
                e
            )

            return False
    def load_all_embeddings(self):

        cursor = self.connection.cursor(dictionary=True)

        sql = """
            SELECT
                s.student_code,
                fe.embedding
            FROM face_embeddings fe
            INNER JOIN students s
                ON fe.student_id = s.id
        """

        cursor.execute(sql)

        rows = cursor.fetchall()

        cursor.close()

        return rows
    def delete_student(self, student_code):

        cursor = self.connection.cursor()

        sql = """
            DELETE FROM students
            WHERE student_code = %s
        """

        cursor.execute(
            sql,
            (student_code,)
        )

        self.connection.commit()

        deleted_count = cursor.rowcount

        cursor.close()

        if deleted_count > 0:

            print(
                "Đã rollback sinh viên:",
                student_code
            )

            return True

        return False
    def add_student(self, student_code, full_name):

    # Kiểm tra MSSV đã tồn tại chưa
        existing_student = self.get_student_by_code(student_code)

        if existing_student is not None:

            print(
                "MSSV đã tồn tại:",
                student_code
            )

            return False

        cursor = self.connection.cursor()

        sql = """
            INSERT INTO students (
                student_code,
                full_name
            )
            VALUES (%s, %s)
        """

        values = (
            student_code,
            full_name
        )

        cursor.execute(sql, values)

        self.connection.commit()

        cursor.close()

        print(
            "Đã thêm sinh viên:",
            student_code
        )

        return True
    def get_student_by_code(self, student_code):

        cursor = self.connection.cursor(dictionary=True)

        sql = """
            SELECT
                id,
                student_code,
                full_name,
                created_at
            FROM students
            WHERE student_code = %s
        """

        cursor.execute(
            sql,
            (student_code,)
        )

        student = cursor.fetchone()

        cursor.close()

        return student
    def get_student_id_by_code(self, student_code):

        cursor = self.connection.cursor()

        sql = """
            SELECT id
            FROM students
            WHERE student_code = %s
        """

        cursor.execute(
            sql,
            (student_code,)
        )

        result = cursor.fetchone()

        cursor.close()

        if result is None:
            return None

        return result[0]
    def save_embedding(self, student_id, embedding):

        cursor = self.connection.cursor()

        sql = """
            INSERT INTO face_embeddings (
                student_id,
                embedding
            )
            VALUES (%s, %s)
        """

        embedding_json = json.dumps(
            embedding.tolist()
        )

        cursor.execute(
            sql,
            (
                student_id,
                embedding_json
            )
        )

        self.connection.commit()

        cursor.close()

        print(
            "Đã lưu embedding cho student_id:",
            student_id
        )
    def close(self):

        if self.connection.is_connected():
            self.connection.close()
            print("Đã đóng kết nối MySQL.")