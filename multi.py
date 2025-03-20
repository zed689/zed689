import os
import multiprocessing
import subprocess
import signal

# Tentukan jumlah CPU yang tersedia
cpu_count = multiprocessing.cpu_count()

# Jumlah proses yang akan dijalankan (1 per CPU)
num_processes = cpu_count

# Tentukan jumlah thread per proses (optimal: 2x jumlah CPU jika memungkinkan)
threads_per_process = max(1, cpu_count // num_processes)

# Nama prefix yang ingin dibuat
prefix = "honeycipher"

# Variabel global untuk menyimpan PID proses yang berjalan
processes = []

# Fungsi untuk menangani penghentian semua proses jika satu domain ditemukan
def stop_all_processes():
    print("[INFO] Domain ditemukan! Menghentikan semua proses...")
    for p in processes:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)  # Hentikan semua proses dalam grup
        except ProcessLookupError:
            pass  # Jika proses sudah mati, abaikan
    exit(0)

# Fungsi untuk menjalankan mkp224o dengan parameter optimal
def run_mkp224o(instance_id):
    cmd = [
        "nice", "-n", "-20",  # Prioritas tinggi
        "taskset", "-c", ",".join(map(str, range(cpu_count))),  # Gunakan semua CPU
        "mkp224o", "-t", str(threads_per_process), prefix  # Jalankan mkp224o
    ]
    print(f"[INFO] Menjalankan proses {instance_id+1} dengan: {' '.join(cmd)}")
    
    # Jalankan proses dan simpan output secara real-time
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, preexec_fn=os.setsid)
    processes.append(process)

    # Cek output secara langsung
    for line in process.stdout:
        print(line, end="")  # Cetak output secara langsung
        if prefix in line:  # Jika domain ditemukan, hentikan semua proses
            stop_all_processes()

# Gunakan multiprocessing untuk menjalankan banyak instance sekaligus
if __name__ == "__main__":
    with multiprocessing.Pool(processes=num_processes) as pool:
        try:
            pool.map(run_mkp224o, range(num_processes))
        except KeyboardInterrupt:
            print("\n[INFO] Dihentikan oleh pengguna.")
            stop_all_processes()
