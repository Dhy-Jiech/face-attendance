import os
import numpy as np

from app.database.database_manager import DatabaseManager


def main():

    print("===== IMPORT EMBEDDING VÀO MYSQL =====")

    student_code = "SV001"

    # Lấy thư mục gốc của project
    project_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )

    file_path = os.path.join(
        project_root,
        "data",
        "embeddings",
        f"{student_code}.npy"
    )

    print("Đường dẫn đang tìm:")
    print(file_path)

    if not os.path.exists(file_path):

        print("Không tìm thấy file.")

        return

    embeddings = np.load(file_path)

    print("Đã tìm thấy file.")
    print("Shape:", embeddings.shape)

    if embeddings.ndim != 2:

        print("Embedding không đúng định dạng.")
        return

    if embeddings.shape[1] != 512:

        print("Embedding không có 512 chiều.")
        return

    db = DatabaseManager()

    student_id = db.get_student_id_by_code(
        student_code
    )

    if student_id is None:

        print(
            "Không tìm thấy sinh viên:",
            student_code
        )

        db.close()
        return

    print("Student ID:", student_id)

    for index, embedding in enumerate(embeddings):

        db.save_embedding(
            student_id,
            embedding
        )

        print(
            f"Đã import embedding "
            f"{index + 1}/{len(embeddings)}"
        )

    db.close()

    print()
    print("===== IMPORT THÀNH CÔNG =====")


if __name__ == "__main__":
    main()