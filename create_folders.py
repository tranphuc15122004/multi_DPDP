import os
import shutil

def create_dpdp_folders(n, base_dir=None, copy_from='DPDP1'):
    """
    Tạo n thư mục DPDP1, DPDP2, ..., DPDPn trong base_dir (mặc định là thư mục hiện tại).
    Các thư mục DPDP2...DPDPn sẽ sao chép toàn bộ nội dung từ copy_from (mặc định là DPDP1).
    """
    if base_dir is None:
        base_dir = os.getcwd()
    src_path = os.path.join(base_dir, copy_from)
    if not os.path.exists(src_path):
        print(f"Không tìm thấy thư mục nguồn: {src_path}")
        return
    for i in range(2, n+1):
        folder_name = f"DPDP{i}"
        folder_path = os.path.join(base_dir, folder_name)
        if i == 1:
            os.makedirs(folder_path, exist_ok=True)
            print(f"Đã tạo: {folder_path}")
        else:
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
            shutil.copytree(src_path, folder_path)
            print(f"Đã tạo và sao chép từ {copy_from}: {folder_path}")

def remove_dpdp_folders(start, end, base_dir=None):
    """
    Xóa các thư mục DPDPx với x trong khoảng [start, end] trong base_dir (mặc định là thư mục hiện tại).
    """
    if start <= 1: start = 2
    if base_dir is None:
        base_dir = os.getcwd()
    for i in range(start, end+1):
        folder_name = f"DPDP{i}"
        folder_path = os.path.join(base_dir, folder_name)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"Đã xóa: {folder_path}")
        else:
            print(f"Không tồn tại: {folder_path}")

# Ví dụ sử dụng:
create_dpdp_folders(30)
#remove_dpdp_folders(1, 30)
