# Prompt: Xây dựng hệ thống Validation OCR System

## Tổng quan
Xây dựng hệ thống **Validation OCR System** — một nền tảng web full-stack cho phép tạo dự án, thêm giấy tờ, import file OCR và thực hiện xác thực dữ liệu.

## 🧩 Công nghệ sử dụng

### Backend
- **FastAPI**
- **Python 3.8**
- **MongoDB** (database)
- **Docker** (containerization)

### Frontend
- **Vue.js** (framework)
- **npm 18.17.0** (quản lý qua nvm)

### Infrastructure
- **Docker Compose** để orchestrate toàn bộ hệ thống

## ⚙️ Các chức năng chính

### 1. Quản lý dự án (Project Management)
- Người dùng có thể **tạo mới dự án** (Project)
- Mỗi dự án có thể chứa nhiều giấy tờ (Document)

### 2. Quản lý giấy tờ trong dự án (Document Management)
- Mỗi dự án có thể chứa nhiều **giấy tờ (Document)**
- Khi tạo giấy tờ, người dùng nhập:
  - **Tên giấy tờ**
  - **URL request OCR** (ví dụ: `http://10.30.153.132:8084/cv/api/v1/ocr/tckt/muasamvattu/contract`)
  
- **Import file JSON mẫu OCR** để định nghĩa cấu trúc dữ liệu OCR trả về
  - File mẫu có cấu trúc như sau:
    ```json
    {
    "information": [
        {
            "contract_no": {
                "confidence": 1.0,
                "value": "01/VIETTEL-ZTE/2024",
                "type": "text",
                "bbox_ids": [],
                "available": 1
            },
            "contract_date": {
                "confidence": 1.0,
                "value": "27/09/2024",
                "type": "text",
                "bbox_ids": [],
                "available": 1
            },
            "project_name": {
                "confidence": 1.0,
                "value": "Project of investing to expand DWDM/Microwave network 2023",
                "type": "text",
                "bbox_ids": [],
                "available": 1
            },
            "bidding_pack": {
                "confidence": 1.0,
                "value": "04/2024-MTD: Upgradding ZTE DWDM transmission networks and related service",
                "type": "text",
                "bbox_ids": [],
                "available": 1
            },
            "party_a_name": {
                "confidence": 1.0,
                "value": "VIETTEL GROUP",
                "type": "text",
                "bbox_ids": [],
                "available": 1
            }
        }
    ],
    "processing_time": 18.5174,
    "core_id": "",
    "request_id": "b945a31a-ba2d-11f0-81f0-0242ac110002",
    "version": "v0.0.9",
    "errorCode": 2000,
    "errorMessage": "Success"
}
    ```
  - Hệ thống chỉ quan tâm đến các trường có `"type": "text"` trong `information[0]`, những type khác ko liên quan
  - Các trường có type khác sẽ được bỏ qua

### 3. Import dữ liệu người dùng
Sau khi giấy tờ được tạo, người dùng sẽ import 2 loại dữ liệu:

#### a. File PDF hoặc Image (đầu vào OCR)
- Upload file PDF hoặc Image
- File sẽ được lưu trên server để sử dụng khi chạy validation

#### b. Form kết quả nhập tay
- Hệ thống tự động generate form dựa trên file JSON mẫu đã import
- Chỉ hiển thị các trường có `type = "text"` trong `information[0]`
- Ví dụ: với file mẫu trên, form sẽ yêu cầu nhập:
  - `contract_no`
  - `contract_date`
  - `project_name`
  - `bidding_pack`
  - `party_a_name`
- Người dùng nhập giá trị cho từng trường

### 4. Chức năng Validation
- Trong trang chi tiết giấy tờ, có nút **"Validation"**
- Khi bấm nút Validation:
  1. Hệ thống thực hiện curl request đến URL đã cấu hình:
     ```bash
     curl --location --request POST 'http://10.30.153.132:8084/cv/api/v1/ocr/tckt/muasamvattu/contract' \
     --form 'file=@"<đường_dẫn_file_đã_upload>"
     ```
  2. Lấy response từ OCR service (có cấu trúc giống file JSON mẫu)
  3. So sánh response OCR với dữ liệu người dùng đã nhập
  4. Tính tỉ lệ chính xác cho từng trường và tổng thể giấy tờ

### 5. Kết quả chi tiết
Sau khi validation hoàn tất, giao diện hiển thị:
- **Giá trị người dùng nhập** (user input)
- **Giá trị trích xuất từ OCR** (OCR extracted value)
- **Tỉ lệ đúng (%)** cho từng trường
- **Tỉ lệ đúng tổng thể** của giấy tờ

## 🧱 Yêu cầu triển khai

### Cấu trúc project
- Cấu trúc dạng microservice (hoặc monolithic module hóa tốt)
- Sử dụng REST API giữa backend và frontend
- Sử dụng Docker Compose để orchestrate các service (backend, frontend, database)

### Database
- Sử dụng PostgreSQL
- Có bảng logs và kết quả validation lưu trong database
- Bảng `validation_results` lưu kết quả so sánh:
  - Tên trường (field_name)
  - Giá trị nhập (user_value)
  - Giá trị OCR (ocr_value)
  - Tỉ lệ đúng (accuracy)
  - Timestamp

### File Storage
- Upload file (PDF/Image) sẽ lưu trên server
- Tổ chức thư mục hợp lý để quản lý file

## 📦 Output mong muốn

### Khởi chạy hệ thống
- Hệ thống có thể khởi chạy bằng lệnh:
  ```bash
  docker-compose up --build
  ```

### Giao diện web Vue
- Quản lý dự án, giấy tờ
- Import file và form
- Chạy validation và xem kết quả chi tiết trực quan
- UI/UX hiện đại, dễ sử dụng

## 📝 Lưu ý kỹ thuật

1. **Chỉ validate type = "text"**: Hệ thống chỉ xử lý và validate các trường có `type = "text"` trong JSON response. Các type khác (nếu có) sẽ được bỏ qua hoàn toàn.

2. **Cấu trúc JSON**: Response từ OCR service sẽ có cấu trúc:
   - `information[0]` chứa object với các field
   - Mỗi field có `type`, `value`, `confidence`, etc.
   - Chỉ lấy `value` của các field có `type = "text"`

3. **Validation Logic**: 
   - So sánh giá trị người dùng nhập với giá trị OCR trích xuất
   - Tính toán độ chính xác (có thể dùng string similarity, exact match, hoặc fuzzy matching)
   - Hiển thị kết quả chi tiết cho từng trường

4. **Error Handling**: 
   - Xử lý lỗi khi OCR service không phản hồi
   - Xử lý lỗi khi file không tồn tại
   - Xử lý lỗi khi JSON không đúng format

5. **Logging**: 
   - Log các hoạt động quan trọng (tạo dự án, tạo giấy tờ, chạy validation)
   - Lưu logs vào database để theo dõi

## 🎯 Deliverables

1. **Backend (Spring Boot)**
   - RESTful API đầy đủ
   - Database schema và migrations
   - Service layer xử lý OCR và validation
   - File upload handling

2. **Frontend (Vue.js)**
   - UI cho quản lý dự án
   - UI cho quản lý giấy tờ
   - Form động generate từ JSON mẫu
   - Hiển thị kết quả validation

3. **Docker Configuration**
   - Dockerfile cho backend
   - Dockerfile cho frontend
   - docker-compose.yml orchestrate toàn bộ

4. **Documentation**
   - README với hướng dẫn setup và chạy
   - API documentation

