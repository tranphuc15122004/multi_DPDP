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
    python_names = ['python3.12', 'python3', 'python']
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] in python_names and proc.info['pid'] != current_pid:
                cmdline = proc.info.get('cmdline', [])
                # Kiểm tra tiến trình có chạy đúng file main.py trong các DPDP không
                for main_path in main_paths:
                    if any(main_path in arg for arg in cmdline):
                        print(f"Killing process PID={proc.info['pid']} CMD={cmdline}")
                        proc.kill()
                        break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def run_all_mains_ver1(in_range=None):
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

def run_all_mains_ver2(in_range=None, threads_per_proc=None, affinity='inherit'):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    process_list = []
    if in_range is None:
        in_range = range(1, NUMBER_OF_SIMULATOR + 1)
    if not hasattr(in_range, '__iter__'):
        print('in_range phải là một iterable (list, range, set...)')
        return
    # Chuẩn bị danh sách các tiến trình sẽ chạy
    procs_to_launch = []
    for i in list(in_range):
        subfolder = f"DPDP{i}"
        main_path = os.path.join(base_dir, subfolder, "main.py")
        if os.path.exists(main_path):
            procs_to_launch.append((i, subfolder, main_path))
        else:
            print(f"Không tìm thấy: {main_path}")

    total_cpus = psutil.cpu_count(logical=True) or os.cpu_count() or 1

    # Thiết lập env để giới hạn thread cho các thư viện (MKL/BLAS/OMP...)
    base_env = os.environ.copy()
    if threads_per_proc is not None and threads_per_proc > 0:
        thread_vars = [
            "OMP_NUM_THREADS",
            "MKL_NUM_THREADS",
            "OPENBLAS_NUM_THREADS",
            "NUMEXPR_NUM_THREADS",
            "BLIS_NUM_THREADS",
            "VECLIB_MAXIMUM_THREADS",
        ]
        for var in thread_vars:
            base_env[var] = str(threads_per_proc)
        # Gợi ý ràng buộc vị trí cho OMP (nếu thư viện hỗ trợ)
        base_env.setdefault("OMP_PROC_BIND", "true")
        base_env.setdefault("OMP_PLACES", "cores")

    # Tính toán danh sách CPU cho từng tiến trình khi dùng 'distribute'
    cpu_lists = None
    if affinity == 'distribute' and len(procs_to_launch) > 0 and total_cpus > 0:
        cpu_indices = list(range(total_cpus))
        per = total_cpus // len(procs_to_launch)
        rem = total_cpus % len(procs_to_launch)
        start = 0
        cpu_lists = []
        for idx in range(len(procs_to_launch)):
            size = per + (1 if idx < rem else 0)
            if size <= 0:
                cpu_lists.append(cpu_indices)  # fallback: cho phép tất cả
            else:
                cpu_lists.append(cpu_indices[start:start+size])
                start += size

    # Khởi chạy các tiến trình
    for idx, (i, subfolder, main_path) in enumerate(procs_to_launch):
        env = base_env.copy()
        p = subprocess.Popen(["python3", main_path], cwd=os.path.join(base_dir, subfolder), env=env)
        process_list.append(p)
        # Thiết lập CPU affinity nếu cần
        if affinity in ('all', 'distribute'):
            try:
                proc_obj = psutil.Process(p.pid)
                if affinity == 'all':
                    proc_obj.cpu_affinity(list(range(total_cpus)))
                elif affinity == 'distribute' and cpu_lists is not None:
                    proc_obj.cpu_affinity(cpu_lists[idx])
            except Exception as e:
                print(f"Không thể đặt CPU affinity cho PID={p.pid}: {e}")
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
        new_val = [1]
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


def update_algorithm_entry_file_all(in_range ,  new_algorithm_name):
    """
    new_instances_dict: dict, ví dụ {1: [1,2,3], 2: [4,5], ...}
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Chỉ nhận giá trị là chuỗi tên file thuật toán
    if isinstance(new_algorithm_name, str):
        new_val = f'"{new_algorithm_name}"'
    else:
        new_val = '"main_algorithm"'
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
                    if line.strip().startswith('ALGORITHM_ENTRY_FILE_NAME'):
                        f.write(f'    ALGORITHM_ENTRY_FILE_NAME = {new_val}\n')
                    else:
                        f.write(line)
            print(f'Đã cập nhật: {config_path}')
        else:
            print(f'Không tìm thấy: {config_path}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quản lý và chạy các instance DPDP.")
    parser.add_argument('--mode', choices=['run', 'kill'], default='run', help='Chế độ: run hoặc kill')
    parser.add_argument('--start', type=int, default=1, help='Thư mục DPDP bắt đầu')
    parser.add_argument('--end', type=int, default=NUMBER_OF_SIMULATOR, help='Thư mục DPDP kết thúc')
    parser.add_argument('--selected', type=str, nargs='*', help='selected_instances cho các DPDP (danh sách số hoặc range(a,b))')
    parser.add_argument('--algorithm', type=str, choices=['main_algorithm', 'dpdp_main'], help='Tên file thuật toán entry')
    parser.add_argument('--auto-select', action='store_true', help='Tự động chia đều selected_instances cho 3 nhóm simulator')
    parser.add_argument('--threads-per-proc', type=int, help='Số thread mỗi tiến trình cho OMP/MKL/BLAS. Ví dụ: 1, 2, 4...')
    parser.add_argument('--affinity', choices=['inherit', 'all', 'distribute'], default='inherit',
                        help='CPU affinity: inherit=giữ nguyên, all=mở tất cả core, distribute=chia core đều giữa các tiến trình')
    args = parser.parse_args()

    in_range = range(args.start, args.end + 1)

    # Xử lý selected: nếu là kiểu range(a,b) thì chuyển thành danh sách số
    def parse_selected(selected_args):
        result = []
        for arg in selected_args:
            arg = arg.strip()
            if arg.startswith('range(') and arg.endswith(')'):
                try:
                    nums = arg[6:-1].split(',')
                    if len(nums) == 2:
                        start, end = int(nums[0]), int(nums[1])
                        result.extend(list(range(start, end)))
                except Exception:
                    print(f'Lỗi khi phân tích {arg}')
            else:
                try:
                    result.append(int(arg))
                except Exception:
                    print(f'Lỗi khi phân tích {arg}')
        return result

    selected_list = parse_selected(args.selected) if args.selected else None
    if selected_list:
        update_selected_instances_all(in_range, selected_list)

    # Nếu truyền algorithm thì cập nhật cho toàn bộ in_range
    if args.algorithm:
        update_algorithm_entry_file_all(in_range, args.algorithm)


    simulators_to_run = list(in_range)
    if args.auto_select:
        if not selected_list:
            print('Bạn phải nhập --selected để chia đều cho các simulator.')
            sys.exit(1)
        # Chia simulator thành 3 nhóm đều nhau
        total_sim = args.end - args.start + 1
        group_sim_size = total_sim // 3
        sim_remainder = total_sim % 3
        sim_ranges = []
        idx = args.start
        
        for i in range(3):
            size = group_sim_size + (1 if i < sim_remainder else 0)
            sim_ranges.append(list(range(idx, idx + size)))
            idx += size
        
        # Chia instance thành 3 phần đều nhau
        total_inst = len(selected_list)
        group_inst_size = total_inst // 3
        inst_remainder = total_inst % 3
        inst_ranges = []
        idx = 0
        for i in range(3):
            size = group_inst_size + (1 if i < inst_remainder else 0)
            inst_ranges.append(selected_list[idx:idx+size])
            idx += size
        
        # Gán từng phần instance cho từng nhóm simulator
        simulators_to_run = []
        for sim_group, inst_group in zip(sim_ranges, inst_ranges):
            for sim_idx in sim_group:
                update_selected_instances_all([sim_idx], inst_group)
                if inst_group:
                    simulators_to_run.append(sim_idx)
    

    if args.mode == 'run':
        if simulators_to_run:
            run_all_mains_ver2(simulators_to_run, threads_per_proc=args.threads_per_proc, affinity=args.affinity)
        else:
            print("Không có simulator nào có instance để chạy.")
    elif args.mode == 'kill':
        kill_python_processes(in_range)
    
