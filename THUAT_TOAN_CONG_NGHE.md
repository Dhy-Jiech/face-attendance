# BÁO CÁO THUẬT TOÁN, PHƯƠNG PHÁP, MÔ HÌNH VÀ CÔNG NGHỆ

## Hệ thống Điểm danh Sinh viên bằng Khuôn mặt (Face Attendance System)

---

### 1. Tổng quan Hệ thống

Hệ thống **Face Attendance System** là ứng dụng điểm danh sinh viên tự động sử dụng công nghệ xử lý ảnh và trí tuệ nhân tạo (AI/Computer Vision). Hệ thống không yêu cầu huấn luyện lại mô hình khi có sinh viên mới, hỗ trợ đăng ký mẫu khuôn mặt trực tiếp từ camera, trích xuất vector đặc trưng 512 chiều và lưu trữ trong CSDL MySQL.

---

### 2. Thuật toán Sử dụng (Algorithms)

#### 2.1. Thuật toán Phát hiện Khuôn mặt (Face Detection)

- **BlazeFace Algorithm**: Thuật toán phát hiện khuôn mặt thời gian thực (Real-time Face Detector) dựa trên mạng Nơ-ron Tích chập (CNN) nhỏ nhẹ, tối ưu hóa cho thiết bị di động và camera webcam.
- **Bounding Box Extraction & Clipping**: Xác định và cắt vùng ảnh chứa khuôn mặt dựa trên tọa độ $(x, y, \text{width}, \text{height})$ do MediaPipe trả về.

#### 2.2. Thuật toán Trích xuất Đặc trưng (Feature Extraction / Face Embedding)

- **FaceNet Deep Embedding Algorithm**: Chuyển đổi một hình ảnh khuôn mặt đã được căn chỉnh thành một **Vector đặc trưng 512 chiều** ($1 \times 512$).
- Vector này đại diện cho các đặc trưng hình học và biểu cảm của khuôn mặt trong không gian đặc trưng (Feature Space).

#### 2.3. Thuật toán So khớp & Nhận diện (Matching & Distance Metrics)

- **Khoảng cách Euclidean ($L_2$ Distance)**: Tính toán độ tương đồng giữa vector khuôn mặt hiện tại và các vector đã lưu trong cơ sở dữ liệu theo công thức:
  $$d(e_1, e_2) = \|e_1 - e_2\|_2 = \sqrt{\sum_{i=1}^{512} (e_{1,i} - e_{2,i})^2}$$
- **Nearest Neighbor Matching (1-NN)**: Tìm vector có khoảng cách nhỏ nhất ($\text{best\_distance}$) trong CSDL tương ứng với từng sinh viên.
- **Phân loại dựa trên Ngưỡng (Thresholding Decision)**:
  - Nếu $\text{best\_distance} \le \text{Threshold}$ (Mặc định: $0.65$): Xác định sinh viên thành công.
  - Nếu $\text{best\_distance} > \text{Threshold}$: Nhãn gán là `UNKNOWN`.

#### 2.4. Thuật toán Tiền xử lý Ảnh (Image Preprocessing)

- **Color Space Conversion**: Chuyển đổi màu từ BGR (OpenCV) sang RGB (MediaPipe / PyTorch).
- **Scaling & Rescaling**: Chuẩn hóa giá trị điểm ảnh từ $[0, 255]$ về khoảng $[-1, 1]$ theo công thức:
  $$\text{Pixel}_{\text{norm}} = \frac{\text{Pixel} - 127.5}{128.0}$$
- **Tensor Transposition**: Chuyển đổi định dạng mảng từ $(H, W, C)$ sang $(C, H, W)$ để tương thích với đầu vào của PyTorch Tensor $[1, 3, 160, 160]$.

#### 2.5. Thuật toán Xác thực Điểm danh (Consecutive Verification)

- Kiểm tra việc nhận diện liên tục một MSSV qua nhiều khung hình (frames) trước khi chốt dữ liệu vào CSDL, hạn chế tối đa điểm danh nhầm khi khuôn mặt quét qua nhanh.

---

### 3. Phương pháp Tiếp cận (Methods & Approaches)

1. **Phương pháp Metric Learning / Deep Embedding (Few-Shot Learning)**:
   - Chuyển bài toán Phân loại (Classification) sang bài toán Đo khoảng cách đặc trưng (Metric Distance).
   - **Ưu điểm vượt trội**: Không cần phải huấn luyện lại (re-train) mô hình AI mỗi khi thêm sinh viên mới. Chỉ cần thực hiện trích xuất vector đặc trưng 512D và lưu vào MySQL.
2. **Phương pháp Đăng ký Đa góc nhìn (Multi-angle Augmentation)**:
   - Khi đăng ký sinh viên mới, hệ thống tự động hướng dẫn người dùng nhìn theo 10 góc khác nhau (nhìn thẳng, biểu cảm tự nhiên, quay nhẹ trái/phải, nhìn lên/xuống). Việc này làm tăng tính đa dạng của tập vector mẫu, cải thiện độ chính xác thực tế.
3. **Cơ chế Rollback Giao dịch Dữ liệu (Transaction Rollback)**:
   - Đảm bảo tính toàn vẹn dữ liệu: Nếu quá trình chụp ảnh/tạo embedding bị lỗi (camera mất kết nối, người dùng hủy ngang), thông tin sinh viên vừa nạp vào CSDL MySQL sẽ tự động bị loại bỏ.

---

### 4. Mô hình AI / Deep Learning (AI & DL Models)

| Tên mô hình                | Kiến trúc                         | Dữ liệu Huấn luyện       | Mục đích                                                                                          |
| :------------------------- | :-------------------------------- | :----------------------- | :------------------------------------------------------------------------------------------------ |
| **MediaPipe FaceDetector** | BlazeFace Short Range (`.tflite`) | Google MediaPipe Dataset | Phát hiện vị trí khuôn mặt thời gian thực trên camera với ngưỡng `min_detection_confidence = 0.6` |
| **FaceNet**                | InceptionResNetV1                 | VGGFace2                 | Biến đổi ảnh khuôn mặt $160 \times 160$ thành Vector đặc trưng 512D                               |

---

### 5. Công nghệ & Thư viện (Technologies & Stack)

- **Ngôn ngữ lập trình**: Python 3.11+
- **Deep Learning Frameworks**:
  - **PyTorch & torchvision**: Nền tảng load và thực thi mô hình `InceptionResNetV1` (tự động phát hiện và tối ưu GPU với CUDA nếu có).
  - **facenet-pytorch**: Thư viện tích hợp sẵn mô hình FaceNet đã được pre-trained.
- **Computer Vision & Image Processing**:
  - **MediaPipe Tasks API**: Thư viện của Google phát hiện khuôn mặt cực nhanh.
  - **OpenCV (`opencv-python`)**: Xử lý camera, cắt ảnh, vẽ bounding box, hiển thị video stream.
  - **Pillow (PIL)**: Xử lý hình ảnh hiển thị trên giao diện Tkinter.
- **Toán học & Đại số**:
  - **NumPy**: Thư viện tính toán ma trận, xử lý vector 512D và tính khoảng cách Euclidean.
- **Cơ sở dữ liệu (Database)**:
  - **MySQL 8.x**: Lưu trữ thông tin sinh viên (`students`), vector embedding dạng JSON (`face_embeddings`), và nhật ký điểm danh (`attendance`).
  - **mysql-connector-python**: Driver kết nối giữa Python ứng dụng và MySQL server.
- **Giao diện người dùng (GUI)\*\***:
  - **Tkinter**: Xây dựng giao diện ứng dụng Desktop (Màn hình chính, Đăng ký sinh viên, Điểm danh).

---

### 6. Sơ đồ Luồng Xử lý Tổng quát

```
[ Camera Stream ]
       │
       ▼
[ MediaPipe Face Detector (BlazeFace) ] ──► (Phát hiện & Cắt khuôn mặt)
       │
       ▼
[ Face Processor (Resize 160x160 & Normalization) ]
       │
       ▼
[ FaceNet (InceptionResNetV1) ] ──► (Tạo Vector Embedding 512D)
       │
       ▼
[ Face Recognizer (Tính khoảng cách Euclidean với CSDL MySQL) ]
       │
       ├──► d <= 0.65 : Xác định sinh viên ──► Ghi nhận Điểm danh (MySQL)
       └──► d >  0.65 : UNKNOWN
```
