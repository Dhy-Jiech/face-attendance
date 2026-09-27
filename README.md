Face Attendance System

Hệ thống điểm danh sinh viên bằng khuôn mặt được xây dựng bằng Python, OpenCV, MediaPipe và FaceNet. Hệ thống cho phép sinh viên đăng ký thông tin và khuôn mặt trực tiếp thông qua camera, sau đó sử dụng nhận diện khuôn mặt để tự động điểm danh.

1. Giới thiệu

Face Attendance System là phần mềm hỗ trợ quản lý điểm danh sinh viên bằng công nghệ nhận diện khuôn mặt.

Hệ thống không yêu cầu cơ sở dữ liệu khuôn mặt có sẵn từ trước. Database ban đầu có thể hoàn toàn trống. Khi một sinh viên đăng ký, hệ thống sẽ:

Nhập MSSV và họ tên.
Mở camera.
Chụp nhiều ảnh khuôn mặt ở các góc khác nhau.
Sử dụng FaceNet để chuyển khuôn mặt thành vector embedding.
Lưu thông tin sinh viên và embedding vào MySQL.
Khi điểm danh, hệ thống nhận diện khuôn mặt từ camera.
So sánh embedding với dữ liệu đã đăng ký.
Nếu xác định được sinh viên, hệ thống ghi nhận điểm danh vào MySQL.
2. Chức năng chính
Đăng ký sinh viên
Nhập MSSV.
Nhập họ tên.
Kiểm tra MSSV đã tồn tại hay chưa.
Sử dụng camera để chụp khuôn mặt.
Chụp 10 ảnh với các hướng nhìn khác nhau.
Tạo face embedding bằng FaceNet.
Lưu embedding vào MySQL.
Nếu quá trình đăng ký thất bại, thông tin sinh viên được rollback.
Điểm danh
Mở camera.
Phát hiện khuôn mặt.
Tạo embedding từ khuôn mặt hiện tại.
So sánh với embedding đã đăng ký.
Hiển thị MSSV và họ tên.
Yêu cầu khuôn mặt được nhận diện liên tục trong một khoảng thời gian trước khi xác nhận.
Kiểm tra sinh viên đã điểm danh trong ngày hay chưa.
Lưu kết quả điểm danh vào MySQL.
Quản lý dữ liệu

Hệ thống sử dụng MySQL để lưu:

Thông tin sinh viên.
Face embedding.
Lịch sử điểm danh.

Dữ liệu không bị mất khi đóng chương trình.

3. Công nghệ sử dụng
Công nghệ	Mục đích
Python 3.11	Ngôn ngữ lập trình
Tkinter	Xây dựng giao diện desktop
OpenCV	Đọc camera và xử lý hình ảnh
MediaPipe	Phát hiện khuôn mặt
FaceNet / InceptionResnetV1	Trích xuất đặc trưng khuôn mặt
PyTorch	Framework chạy FaceNet
NumPy	Xử lý vector embedding
MySQL	Lưu trữ dữ liệu
mysql-connector-python	Kết nối Python với MySQL
4. Kiến trúc hệ thống

Hệ thống được chia thành các module chính:

face_attendance/
│
├── app/
│   │
│   ├── camera/
│   │
│   ├── face/
│   │   ├── face_detector.py
│   │   └── face_processor.py
│   │
│   ├── recognition/
│   │   ├── embedding.py
│   │   ├── embedding_storage.py
│   │   ├── face_recognizer.py
│   │   └── test_recognition.py
│   │
│   ├── registration/
│   │   ├── registration.py
│   │   └── embedding_registration.py
│   │
│   ├── attendance/
│   │   ├── attendance_manager.py
│   │   └── test_attendance.py
│   │
│   └── database/
│       ├── database_manager.py
│       ├── test_database.py
│       └── import_embeddings.py
│
├── ui/
│   ├── main_window.py
│   ├── registration_window.py
│   └── attendance_window.py
│
├── data/
│   ├── registered_faces/
│   └── embeddings/
│
├── models/
│
├── tests/
│
├── main.py
├── requirements.txt
└── README.md
5. Vai trò của từng module
app/face/

Xử lý khuôn mặt.

face_detector.py

Sử dụng MediaPipe để phát hiện khuôn mặt trong hình ảnh hoặc camera.

Kết quả trả về bounding box:

(x, y, width, height)
face_processor.py

Thực hiện:

Cắt khuôn mặt.
Giới hạn tọa độ khuôn mặt trong phạm vi ảnh.
Resize ảnh về kích thước phù hợp với mô hình.
app/recognition/

Xử lý nhận diện khuôn mặt.

embedding.py

Sử dụng:

InceptionResnetV1

được pretrained trên VGGFace2.

Mỗi khuôn mặt được chuyển thành một vector:

512 dimensions

Ví dụ:

[0.012, -0.034, 0.087, ...]

Vector này được gọi là face embedding.

face_recognizer.py

So sánh embedding của khuôn mặt hiện tại với các embedding đã lưu trong database.

Khoảng cách được tính bằng Euclidean distance:

distance = ||embedding1 - embedding2||

Nếu khoảng cách nhỏ hơn ngưỡng được cấu hình, hệ thống xác định khuôn mặt tương ứng với sinh viên.

app/registration/

Xử lý đăng ký sinh viên.

registration.py

Quản lý quá trình:

Mở camera
    ↓
Phát hiện khuôn mặt
    ↓
Chụp 10 ảnh
    ↓
Lưu ảnh

Ảnh được lưu tạm tại:

data/registered_faces/<MSSV>/

Ví dụ:

data/
└── registered_faces/
    └── SV001/
        ├── face_01.jpg
        ├── face_02.jpg
        ├── face_03.jpg
        ├── ...
        └── face_10.jpg
embedding_registration.py

Đọc các ảnh khuôn mặt đã đăng ký và sử dụng FaceNet để tạo embedding.

Sau đó lưu embedding vào MySQL.

app/database/

Quản lý MySQL.

database_manager.py

Chịu trách nhiệm:

Kết nối MySQL.
Thêm sinh viên.
Tìm sinh viên.
Lưu embedding.
Đọc embedding.
Kiểm tra điểm danh.
Lưu điểm danh.
Xóa sinh viên khi rollback.
app/attendance/

Xử lý nghiệp vụ điểm danh.

Module này quản lý logic liên quan đến việc xác định sinh viên đã điểm danh hay chưa và kết quả điểm danh.

ui/

Chứa giao diện người dùng bằng Tkinter.

main_window.py

Màn hình chính:

┌─────────────────────────────┐
│     HỆ THỐNG ĐIỂM DANH      │
│                             │
│  [ ĐĂNG KÝ SINH VIÊN ]      │
│                             │
│  [ ĐIỂM DANH ]              │
│                             │
│  [ THOÁT ]                  │
└─────────────────────────────┘
registration_window.py

Giao diện nhập:

MSSV
Họ tên
Đăng ký khuôn mặt
Hủy
attendance_window.py

Giao diện điểm danh và điều khiển camera.

6. Cơ sở dữ liệu

Database sử dụng:

MySQL

Tên database:

face_attendance
Bảng students

Lưu thông tin sinh viên.

CREATE TABLE students (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_code VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
Bảng face_embeddings

Lưu các vector embedding của sinh viên.

CREATE TABLE face_embeddings (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id BIGINT NOT NULL,
    embedding JSON NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_embedding_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE
);

Một sinh viên có thể có nhiều embedding.

Ví dụ:

SV001
 ├── embedding 1
 ├── embedding 2
 ├── embedding 3
 ├── ...
 └── embedding 10
Bảng attendance

Lưu lịch sử điểm danh.

CREATE TABLE attendance (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id BIGINT NOT NULL,
    attendance_date DATE NOT NULL,
    attendance_time TIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PRESENT',
    CONSTRAINT fk_attendance_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,
    CONSTRAINT uk_student_attendance
        UNIQUE (student_id, attendance_date)
);

Ràng buộc:

(student_id, attenda nce_date)

đảm bảo một sinh viên chỉ được ghi nhận điểm danh một lần trong ngày.

7. Yêu cầu môi trường

Khuyến nghị:

Python 3.11.x
MySQL 8.x
Webcam
Windows

Kiểm tra Python:

python --version

Kiểm tra pip:

pip --version
8. Cài đặt project
Bước 1: Clone project
git clone <repository-url>

Đi vào thư mục project:

cd face_attendance
Bước 2: Tạo virtual environment

Windows:

python -m venv venv

Kích hoạt:

venv\Scripts\activate

Sau khi kích hoạt thành công:

(venv)

sẽ xuất hiện ở đầu Terminal.

Bước 3: Cài đặt thư viện
pip install -r requirements.txt
9. Cấu hình MySQL

Tạo database:

CREATE DATABASE face_attendance
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

Sau đó chạy các câu lệnh CREATE TABLE trong phần cơ sở dữ liệu ở trên.

Mở:

app/database/database_manager.py

Cấu hình:

self.connection = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="YOUR_PASSWORD",
    database="face_attendance"
)

Thay:

YOUR_PASSWORD

bằng mật khẩu MySQL trên máy.

10. Chạy chương trình

Sau khi cài đặt và cấu hình database:

python main.py

Màn hình chính sẽ xuất hiện.

11. Quy trình đăng ký sinh viên

Chọn:

ĐĂNG KÝ SINH VIÊN

Nhập:

MSSV: SV001
Họ tên: Nguyễn Văn A

Sau đó chọn:

ĐĂNG KÝ KHUÔN MẶT

Camera sẽ được mở.

Hệ thống yêu cầu người dùng thay đổi hướng nhìn:

Nhin thang camera
Nhin thang - bieu cam tu nhien
Quay mat nhe sang TRAI
Quay mat nhe sang PHAI
Nhin hoi len
Nhin hoi xuong
...

Hệ thống chụp tổng cộng 10 ảnh.

Sau đó:

10 ảnh
   ↓
FaceNet
   ↓
10 embedding
   ↓
MySQL
12. Quy trình điểm danh

Chọn:

ĐIỂM DANH

Camera được mở.

Hệ thống thực hiện:

Camera
   ↓
MediaPipe
   ↓
Phát hiện khuôn mặt
   ↓
Face Processor
   ↓
FaceNet
   ↓
512-dimensional embedding
   ↓
Face Recognizer
   ↓
So sánh MySQL
   ↓
Xác định sinh viên
   ↓
Kiểm tra attendance
   ↓
Lưu kết quả

Ví dụ khi nhận diện:

SV001 - Nguyễn Văn A

Nếu sinh viên chưa điểm danh:

SV001 - Nguyễn Văn A | Xác nhận...

Sau khi xác nhận:

SV001 - Nguyễn Văn A | ĐIỂM DANH THÀNH CÔNG

Nếu sinh viên đã điểm danh:

SV001 - Nguyễn Văn A | Đã điểm danh
13. Mô hình nhận diện khuôn mặt

Hệ thống sử dụng FaceNet thông qua:

InceptionResnetV1(
    pretrained="vggface2"
)

FaceNet không trực tiếp trả về:

SV001
SV002
SV003

Thay vào đó, mô hình chuyển khuôn mặt thành một vector đặc trưng 512 chiều.

Ví dụ:

Face Image
     ↓
   FaceNet
     ↓
Embedding
[0.12, -0.03, 0.08, ...]

Khi điểm danh:

Camera Face
     ↓
   FaceNet
     ↓
Current Embedding
     ↓
Distance
     ↓
Registered Embeddings
     ↓
Student

Cách tiếp cận này cho phép hệ thống thêm sinh viên mới mà không cần huấn luyện lại một mô hình classifier riêng cho từng sinh viên.

14. Ngưỡng nhận diện

Hệ thống hiện sử dụng khoảng cách Euclidean để so sánh embedding.

Ngưỡng hiện tại được cấu hình trong:

app/recognition/face_recognizer.py

Ví dụ:

threshold=0.5

Logic:

distance <= threshold
        ↓
    Recognized

distance > threshold
        ↓
     Unknown

Ngưỡng 0.5 chỉ là giá trị cấu hình ban đầu. Khi triển khai thực tế cần kiểm thử với:

nhiều ảnh của cùng một người;
ảnh của những người khác nhau;
nhiều điều kiện ánh sáng;
khoảng cách khác nhau với camera;
các góc mặt khác nhau.

Từ kết quả kiểm thử có thể điều chỉnh ngưỡng phù hợp.

15. Cấu trúc dữ liệu khuôn mặt

Ảnh khuôn mặt được lưu trong:

data/registered_faces/

Ví dụ:

data/
└── registered_faces/
    ├── SV001/
    │   ├── face_01.jpg
    │   ├── face_02.jpg
    │   ├── ...
    │   └── face_10.jpg
    │
    └── SV002/
        ├── face_01.jpg
        ├── face_02.jpg
        ├── ...
        └── face_10.jpg

Các ảnh này được sử dụng để tạo embedding.

Embedding chính thức được lưu trong MySQL.

16. Xử lý lỗi đăng ký

Quá trình đăng ký gồm nhiều bước:

Nhập thông tin
      ↓
Thêm sinh viên
      ↓
Chụp khuôn mặt
      ↓
Tạo embedding
      ↓
Lưu embedding

Nếu một bước quan trọng thất bại, hệ thống có cơ chế rollback thông tin sinh viên.

Ví dụ:

Thêm SV001 vào MySQL
        ↓
Camera lỗi
        ↓
Xóa SV001

Điều này hạn chế trường hợp database chứa sinh viên nhưng không có dữ liệu khuôn mặt tương ứng.

17. Kiểm tra hệ thống

Có thể chạy các module kiểm thử riêng:

python -m app.database.test_database

Kiểm tra embedding:

python -m app.recognition.test_mysql_embeddings

Các test khác có thể được đặt trong:

tests/
18. Một số lưu ý
Camera

Nếu camera không mở được:

Kiểm tra webcam có hoạt động không.
Kiểm tra ứng dụng khác có đang sử dụng camera không.
Kiểm tra quyền Camera của Windows.
Có thể thử thay đổi:
cv2.VideoCapture(0)

thành:

cv2.VideoCapture(1)

nếu máy có nhiều camera.

MySQL

Đảm bảo MySQL Server đang chạy trước khi khởi động chương trình.

Kiểm tra lại:

host
port
user
password
database

trong database_manager.py.

FaceNet

Lần đầu chạy FaceNet có thể mất thời gian tải model pretrained.

Sau khi model được tải, hệ thống sử dụng model để tạo embedding cho khuôn mặt.

19. Hướng phát triển

Các chức năng có thể phát triển thêm:

Quản lý danh sách sinh viên.
Thêm/xóa/cập nhật sinh viên.
Quản lý nhiều lớp học.
Quản lý nhiều buổi học.
Điểm danh theo lớp.
Thống kê số lượng sinh viên đã điểm danh.
Xuất danh sách điểm danh Excel.
Xuất báo cáo PDF.
Lưu thời gian điểm danh chính xác.
Phân quyền người dùng.
Đăng nhập quản trị viên.
Cải thiện giao diện.
Chuyển xử lý camera sang background thread.
Cải thiện tốc độ nhận diện.
Cache embedding để giảm số lần truy vấn database.
Thử nghiệm và tối ưu threshold.
Bổ sung kiểm tra chống giả mạo khuôn mặt (liveness detection).
20. Sơ đồ tổng quát
                 FACE ATTENDANCE SYSTEM
                         │
          ┌──────────────┴──────────────┐
          │                             │
      ĐĂNG KÝ                        ĐIỂM DANH
          │                             │
     Nhập MSSV                      Mở Camera
     Nhập họ tên                        │
          │                        MediaPipe
     Mở Camera                          │
          │                        Detect Face
     Chụp 10 ảnh                        │
          │                         FaceNet
       FaceNet                           │
          │                         Embedding
      Embedding                          │
          │                              │
          └──────────┐          ┌────────┘
                     ↓          ↓
                  MySQL Database
                       │
             ┌─────────┼─────────┐
             │         │         │
          Students  Embeddings Attendance
21. Tác giả

Project được xây dựng phục vụ mục đích học tập môn Trí tuệ nhân tạo (AI).

Công nghệ chính:

Python
OpenCV
MediaPipe
FaceNet
PyTorch
MySQL
Tkinter
22. License

Project được sử dụng cho mục đích học tập và nghiên cứu.