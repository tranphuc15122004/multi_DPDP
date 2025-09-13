import subprocess
import os
import argparse
import sys
import psutil
import os

NUMBER_OF_SIMULATOR = 30

def kill_python_processes(in_range=None):
    current_pid = os.getpid()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if in_range is None:
        in_range = range(1, NUMBER_OF_SIMULATOR + 1)
    # Tạo danh sách các đường dẫn main.py cần kiểm tra
    main_paths = [os.path.join(base_dir, f'DPDP{i}', 'main.py') for i in list(in_range)]
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python3' and proc.info['pid'] != current_pid:
                cmdline = proc.info.get('cmdline', [])
                # Kiểm tra tiến trình có chạy đúng file main.py trong các DPDP không
                for main_path in main_paths:
                    if any(main_path in arg for arg in cmdline):
                        print(f"Killing process PID={proc.info['pid']} CMD={cmdline}")
                        proc.kill()
                        break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def run_all_mains(in_range=None):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    process_list = []
    if in_range is None:
        in_range = range(1, NUMBER_OF_SIMULATOR + 1)
    if not hasattr(in_range, '__iter__'):
        print('in_range phải là một iterable (list, range, set...)')
        return
    for i in list(in_range):
        subfolder = f"DPDP{i}"
        main_path = os.path.join(base_dir, subfolder, "main.py")
        if os.path.exists(main_path):
            # Sử dụng python để chạy file main.py
            p = subprocess.Popen(["python3", main_path], cwd=os.path.join(base_dir, subfolder))
            process_list.append(p)
        else:
            print(f"Không tìm thấy: {main_path}")
    print(f"Đã khởi động {len(process_list)} tiến trình.")
    # Nếu muốn chờ tất cả tiến trình kết thúc thì bỏ comment dòng dưới
    # for p in process_list:
    #     p.wait()
 
def update_selected_instances_all(in_range ,  new_instances_dict):
    """
    new_instances_dict: dict, ví dụ {1: [1,2,3], 2: [4,5], ...}
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Nếu truyền vào là list thì áp dụng cho tất cả, nếu là dict thì lấy value đầu tiên hoặc []
    if isinstance(new_instances_dict, list):
        new_val = new_instances_dict
    elif isinstance(new_instances_dict, dict) and new_instances_dict:
        new_val = list(new_instances_dict.values())[0]
    else:
        new_val = []
    # in_range có thể là list, range hoặc set các số thứ tự DPDP muốn thay đổi
    if not hasattr(in_range, '__iter__'):
        print('in_range phải là một iterable (list, range, set...)')
        return
    for i in list(in_range):
        config_path = os.path.join(base_dir, f'DPDP{i}', 'src', 'conf', 'configs.py')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(config_path, 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.strip().startswith('selected_instances'):
                        f.write(f'    selected_instances = {new_val}\n')
                    else:
                        f.write(line)
            print(f'Đã cập nhật: {config_path}')
        else:
            print(f'Không tìm thấy: {config_path}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chọn chế độ chạy hoặc kill tiến trình.")
    parser.add_argument('--mode', choices=['run', 'kill'], default='run', help='Chế độ: run hoặc kill')
    args = parser.parse_args()

    update_selected_instances_all(range(1 , 11), [1])
    update_selected_instances_all(range(11 , 21), [1])
    update_selected_instances_all(range(21 , 31), [1])
    

    if args.mode == 'run':
        run_all_mains()
    elif args.mode == 'kill':
        kill_python_processes()
    
