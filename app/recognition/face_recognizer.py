import json
import numpy as np


class FaceRecognizer:

    def __init__(
        self,
        face_embedding,
        database_manager,
        threshold=0.65
    ):

        self.face_embedding = face_embedding
        self.database_manager = database_manager
        self.threshold = threshold

        self.database = {}

        self.load_embeddings()

    def load_embeddings(self):

        rows = self.database_manager.load_all_embeddings()

        self.database = {}

        for row in rows:

            student_code = row["student_code"]

            embedding = np.array(
                json.loads(row["embedding"]),
                dtype=np.float32
            )

            if student_code not in self.database:
                self.database[student_code] = []

            self.database[student_code].append(
                embedding
            )

        print(
            "Đã tải",
            len(self.database),
            "sinh viên từ MySQL."
        )

    def calculate_distance(
        self,
        embedding1,
        embedding2
    ):

        return np.linalg.norm(
            embedding1 - embedding2
        )

    def recognize(self, face_image):

        if len(self.database) == 0:
            return None, None

        embedding = self.face_embedding.extract(
            face_image
        )

        best_student = None
        best_distance = float("inf")

        for student_code, embeddings in self.database.items():

            for registered_embedding in embeddings:

                distance = self.calculate_distance(
                    embedding,
                    registered_embedding
                )

                if distance < best_distance:

                    best_distance = distance
                    best_student = student_code

        if best_distance <= self.threshold:

            return best_student, best_distance

        return None, best_distance