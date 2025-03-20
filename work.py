import socket
import subprocess
import multiprocessing
import threading
import os
import signal

# Konfigurasi koneksi ke Master
MASTER_IP = "0.tcp.ap.ngrok.io"
PORT = 18008
TARGET_PATTERN = "honeycipher"
STOP_SIGNAL = multiprocessing.Event()  # Gunakan Event agar proses bisa dihentikan serentak

def search_onion():
    """Fungsi pencarian domain menggunakan multiprocessing & multithreading."""
    print(f"[+] Worker PID {os.getpid()} mencari: {TARGET_PATTERN}")

    process = subprocess.Popen(
        ["mkp224o", "-t", "4", TARGET_PATTERN],  # Maksimum 4 thread per proses
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        if STOP_SIGNAL.is_set():  # Jika sinyal stop diterima, hentikan proses
            process.terminate()
            return None
        if line.startswith(TARGET_PATTERN):
            found_onion = line.strip()
            print(f"[✔] Ditemukan: {found_onion}")
            STOP_SIGNAL.set()  # Set STOP_SIGNAL agar semua worker berhenti
            process.terminate()
            return found_onion

def listen_master(client):
    """Thread untuk mendengarkan perintah STOP dari Master."""
    while True:
        try:
            message = client.recv(1024).decode()
            if message.startswith("FOUND|"):
                print(f"[🔥] Domain diterima dari Master: {message[6:]}")
                STOP_SIGNAL.set()  # Set STOP_SIGNAL agar worker berhenti
                os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)  # Hentikan semua proses dalam grup
                break
        except:
            pass

def worker_task():
    """Fungsi utama untuk worker yang menjalankan banyak thread."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((MASTER_IP, PORT))

    # Jalankan thread untuk mendengarkan perintah dari Master
    listener_thread = threading.Thread(target=listen_master, args=(client,))
    listener_thread.daemon = True
    listener_thread.start()

    # Jalankan 4 thread pencarian per worker
    threads = []
    results = [None] * 4  # Tempat penyimpanan hasil pencarian tiap thread

    def thread_search(idx):
        """Fungsi pencarian di tiap thread."""
        if not STOP_SIGNAL.is_set():
            results[idx] = search_onion()

    for i in range(4):
        t = threading.Thread(target=thread_search, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    # Kirim hasil ke Master jika ditemukan
    found_onion = next((res for res in results if res), None)
    if found_onion:
        client.sendall(found_onion.encode())

if __name__ == "__main__":
    num_processes = multiprocessing.cpu_count()  # Maksimum sesuai jumlah CPU
    processes = []

    for _ in range(num_processes):
        p = multiprocessing.Process(target=worker_task)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
