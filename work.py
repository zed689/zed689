import socket
import subprocess
import multiprocessing
import os
import signal
import threading

MASTER_IP = "0.tcp.ap.ngrok.io"
PORT = 18008
TARGET_PATTERN = "honeycipher"
STOP_SIGNAL = False

def search_onion():
    """Fungsi pencarian domain dengan multi-threading."""
    global STOP_SIGNAL
    print(f"[+] Worker mencari: {TARGET_PATTERN}")

    process = subprocess.Popen(
        ["mkp224o", "-t", str(multiprocessing.cpu_count()), TARGET_PATTERN],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        if STOP_SIGNAL:
            process.terminate()
            break
        if line.startswith(TARGET_PATTERN):
            print(f"[✔] Ditemukan: {line.strip()}")
            STOP_SIGNAL = True
            process.terminate()
            return line.strip()

def listen_master(client):
    """Thread untuk mendengarkan perintah STOP dari Master."""
    global STOP_SIGNAL
    while True:
        try:
            message = client.recv(1024).decode()
            if message.startswith("FOUND|"):
                print(f"[🔥] Domain diterima dari Master: {message[6:]}")
                STOP_SIGNAL = True
                os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)
                break
        except:
            pass

def worker_process():
    """Fungsi utama untuk tiap proses worker."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((MASTER_IP, PORT))

    # Jalankan thread untuk mendengarkan Master
    thread = threading.Thread(target=listen_master, args=(client,))
    thread.start()

    # Mulai pencarian domain
    found_onion = search_onion()
    if found_onion:
        client.sendall(found_onion.encode())

if __name__ == "__main__":
    num_processes = multiprocessing.cpu_count()
    processes = []

    for _ in range(num_processes):
        p = multiprocessing.Process(target=worker_process)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
