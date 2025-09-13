# multi_thread_DPDP

## Cấu trúc thư mục
- `main.py`: Chạy và quản lý các instance DPDP.
- `DPDP1/` đến `DPDP30/`: Mỗi thư mục chứa một instance DPDP riêng biệt.
    - `main.py`: File chính của từng instance.
    - `algorithm/`, `benchmark/`, `simpy/`, `src/`: Các module/phần phụ trợ cho từng instance.
- `benchmark/`: Chứa dữ liệu đầu vào (csv, instance).
- `venv/`: Môi trường ảo Python.

## Hướng dẫn sử dụng
### 1. Cài đặt môi trường
```bash
source venv/bin/activate
```

### 2. Chạy tất cả các instance DPDP

Chạy toàn bộ các simulator:
```bash
python main.py --mode run
```

### 3. Cập nhật selected_instances cho các instance
Hàm `update_selected_instances_all` sẽ tự động cập nhật cấu hình cho các instance trong khoảng bạn chọn.

### 4. Kill các tiến trình DPDP

Kill các tiến trình Python chạy file main.py trong các thư mục DPDP bạn chọn.

Hoặc kill toàn bộ các tiến trình 
```bash
python main.py --mode kill 
```