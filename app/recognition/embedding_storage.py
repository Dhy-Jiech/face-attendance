import os
import numpy as np


class EmbeddingStorage:

    def __init__(self):

        self.base_path = "data/embeddings"

        os.makedirs(
            self.base_path,
            exist_ok=True
        )

    def save(self, student_code, embeddings):

        file_path = os.path.join(
            self.base_path,
            f"{student_code}.npy"
        )

        np.save(
            file_path,
            embeddings
        )

        print("Đã lưu embedding:")
        print(file_path)

    def load(self, student_code):

        file_path = os.path.join(
            self.base_path,
            f"{student_code}.npy"
        )

        if not os.path.exists(file_path):
            return None

        return np.load(file_path)