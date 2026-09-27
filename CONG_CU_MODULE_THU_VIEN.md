# TÀI LIỆU CÔNG CỤ, MODULE VÀ THƯ VIỆN LẬP TRÌNH

## Hệ thống Điểm danh Sinh viên bằng Khuôn mặt (Face Attendance System)

---

### I. CÔNG CỤ & MÔI TRƯỜNG PHÁT TRIỂN (Tools & Environment)

1. **Python 3.11+**:
   - Ngôn ngữ lập trình chính được sử dụng để phát triển toàn bộ ứng dụng, từ xử lý ảnh, chạy mô hình AI đến giao diện người dùng và cơ sở dữ liệu.
2. **MySQL Server 8.x**:
   - Hệ quản trị cơ sở dữ liệu quan hệ dùng lưu trữ:
     - Thông tin sinh viên (`students`: `id`, `student_code`, `full_name`).
     - Vector đặc trưng 512D lưu dạng JSON (`face_embeddings`: `student_id`, `embedding`).
     - Nhật ký điểm danh (`attendance`: `student_id`, `attendance_date`, `attendance_time`, `status`).
3. **Tập file Trọng số Mô hình (Pre-trained Model Weights)**:
   - `blaze_face_short_range.tflite`: File trọng số của mô hình BlazeFace (phát triển bởi Google) dành cho MediaPipe để phát hiện vị trí khuôn mặt ở cự ly gần.
   - Trọng số `InceptionResNetV1` pretrained trên tập dữ liệu `VGGFace2`: Tự động nạp qua thư viện `facenet-pytorch` để trích xuất 512-dimensional vector.
4. **Webcam Hardware**:
   - Thiết bị thu nhận luồng video thời gian thực với độ phân giải tiêu chuẩn $640 \times 480$.

---

### II. CÁC THƯ VIỆN LẬP TRÌNH (Libraries & Frameworks)

| Thư viện / Framework                  | Phiên bản       | Vai trò & Mục đích trong Dự án                                                                                                                                                                    |
| :------------------------------------ | :-------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`opencv-python` (OpenCV)**          | `5.0.0` / `4.x` | Xử lý hình ảnh & Camera: Thu nhận khung hình từ Webcam (`cv2.VideoCapture`), cắt cúp khuôn mặt, chuyển đổi không gian màu BGR/RGB, vẽ khung Bounding Box và hiển thị text hướng dẫn lên màn hình. |
| **`mediapipe`**                       | Latest          | Phát hiện khuôn mặt thời gian thực từ Google MediaPipe Tasks API với độ chính xác cao và tối ưu hiệu năng phần cứng.                                                                              |
| **`torch` & `torchvision` (PyTorch)** | Latest          | Framework Deep Learning cốt lõi: Load mô hình `InceptionResNetV1`, biến đổi dữ liệu thành PyTorch Tensor, tính toán đặc trưng (tự động kích hoạt GPU CUDA nếu có).                                |
| **`facenet-pytorch`**                 | Latest          | Cung cấp sẵn mô hình FaceNet (`InceptionResNetV1`) đã được huấn luyện sẵn trên VGGFace2 để tạo vector đặc trưng 512 chiều từ ảnh khuôn mặt $160 \times 160$.                                      |
| **`numpy`**                           | `1.26.4`        | Xử lý mảng số học, đại số tuyến tính, biến đổi vector đặc trưng 512D và tính khoảng cách Euclidean ($L_2$ norm) giữa các vector.                                                                  |
| **`mysql-connector-python`**          | Latest          | Driver kết nối ứng dụng Python với CSDL MySQL (thực thi các câu lệnh SQL, commit hoặc rollback giao dịch).                                                                                        |
| **`tkinter`**                         | Built-in        | Thư viện thiết kế giao diện Desktop chuẩn của Python (Xây dựng màn hình chính, màn hình đăng ký và màn hình điểm danh).                                                                           |
| **`Pillow` (PIL)**                    | Latest          | Hỗ trợ chuyển đổi mảng ảnh OpenCV sang định dạng tương thích với canvas hiển thị giao diện Tkinter.                                                                                               |

---

### III. CHI TIẾT CÁC MODULE TRONG DỰ ÁN (Project Modules Architecture)

Dự án được cấu trúc theo mô hình **Modular Architecture**, giúp mã nguồn dễ bảo trì và mở rộng:

```
face_attendance/
│
├── app/
│   ├── face/               # Module xử lý khuôn mặt (Detect, Crop, Resize)
│   ├── recognition/        # Module trích xuất vector đặc trưng & So khớp
│   ├── registration/       # Module đăng ký sinh viên mới
│   ├── attendance/         # Module quản lý nghiệp vụ điểm danh
│   └── database/           # Module kết nối & thao tác CSDL MySQL
│
├── ui/                     # Module giao diện người dùng Tkinter
├── data/                   # Thư mục chứa dữ liệu tạm (Ảnh đăng ký)
├── main.py                 # File khởi chạy chính của ứng dụng
└── requirements.txt        # Danh sách các thư viện phụ thuộc
```

#### 1. Module Xử lý Khuôn mặt (`app/face/`)

- **`face_detector.py`** (`FaceDetector`):
  - Đọc mô hình `blaze_face_short_range.tflite` qua MediaPipe Vision API.
  - Nhận khung hình `frame` từ OpenCV và trả về danh sách vị trí bounding box $(x, y, w, h)$ của tất cả khuôn mặt.
- **`face_processor.py`** (`FaceProcessor`):
  - Cắt vùng chứa khuôn mặt từ khung hình gốc.
  - Giới hạn tọa độ để chống lỗi tràn viền ảnh (Image Boundary Clipping).
  - Resize ảnh khuôn mặt về chuẩn kích thước $160 \times 160$ pixel.

#### 2. Module Nhận diện & Embedding (`app/recognition/`)

- **`embedding.py`** (`FaceEmbedding`):
  - Khởi tạo mô hình FaceNet (`InceptionResNetV1(pretrained='vggface2')`).
  - Chuyển đổi định dạng màu sang RGB, chuẩn hóa pixel về khoảng $[-1, 1]$, chuyển đổi mảng sang PyTorch Tensor `[1, 3, 160, 160]` và trích xuất vector 512D.
- **`face_recognizer.py`** (`FaceRecognizer`):
  - Tải danh sách vector đặc trưng của tất cả sinh viên từ MySQL vào RAM.
  - Tính khoảng cách Euclidean giữa vector khuôn mặt hiện tại từ camera với các vector đã lưu.
  - So sánh khoảng cách nhỏ nhất với ngưỡng `threshold = 0.65` để nhận diện sinh viên.
- **`embedding_storage.py`**:
  - Đóng gói xử lý đệm và lưu trữ vector JSON.

#### 3. Module Đăng ký Sinh viên (`app/registration/`)

- **`registration.py`** (`StudentRegistration`):
  - Điều khiển camera chụp 10 ảnh khuôn mặt của sinh viên theo các hướng nhìn (thẳng, quay trái/phải, ngẩng/cúi, biểu cảm).
  - Lưu ảnh tạm vào thư mục `data/registered_faces/<MSSV>/`.
- **`embedding_registration.py`** (`EmbeddingRegistration`):
  - Đọc 10 ảnh vừa chụp, trích xuất 10 vector đặc trưng 512D tương ứng và lưu vào bảng `face_embeddings` trong MySQL.

#### 4. Module Nghiệp vụ Điểm danh (`app/attendance/`)

- **`attendance_manager.py`** (`AttendanceManager`):
  - Quản lý nghiệp vụ điểm danh: Kiểm tra sinh viên đã điểm danh trong ngày hay chưa, lưu mốc ngày giờ điểm danh thực tế.

#### 5. Module Cơ sở dữ liệu (`app/database/`)

- **`database_manager.py`** (`DatabaseManager`):
  - Khởi tạo kết nối MySQL.
  - Chứa các phương thức xử lý SQL:
    - `add_student()`: Thêm thông tin sinh viên mới.
    - `save_embedding()`: Lưu vector JSON vào DB.
    - `load_all_embeddings()`: Nạp dữ liệu đặc trưng phục vụ so khớp.
    - `mark_attendance()` & `has_attendance_today()`: Kiểm tra và ghi nhận điểm danh.
    - `delete_student()`: Hỗ trợ rollback khi quá trình đăng ký gặp sự cố.

#### 6. Module Giao diện Người dùng (`ui/`)

- **`main_window.py`**: Giao diện cửa sổ chính với các nút chức năng: **Đăng ký sinh viên**, **Điểm danh**, **Thoát**.
- **`registration_window.py`**: Giao diện form nhập MSSV, Họ tên và kích hoạt cửa sổ camera chụp ảnh mẫu.
- **`attendance_window.py`**: Giao diện màn hình điểm danh, hiển thị video camera thời gian thực, bounding box, thông tin sinh viên và trạng thái điểm danh.

#### 7. File Khởi chạy chính (`main.py`)

- Điểm vào (Entry Point) của phần mềm: Khởi tạo CSDL MySQL, nạp mô hình AI (`FaceDetector`, `FaceEmbedding`, `FaceRecognizer`) và khởi chạy giao diện GUI Tkinter.
