import numpy as np

from app.database.database_manager import DatabaseManager


def main():

    print("===== TEST LƯU EMBEDDING =====")

    db = DatabaseManager()

    student_id = db.get_student_id_by_code("SV001")

    if student_id is None:

        print("Không tìm thấy SV001.")
        db.close()
        return

    print("Student ID:", student_id)

    # Tạo embedding giả gồm 512 số
    embedding = np.random.rand(512).astype(np.float32)

    print(
        "Kích thước embedding:",
        embedding.shape
    )

    db.save_embedding(
        student_id,
        embedding
    )

    db.close()


if __name__ == "__main__":
    main()