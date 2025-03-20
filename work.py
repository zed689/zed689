import socket
import subprocess
import multiprocessing
import random
import os
import signal

MASTER_IP = "0.tcp.ap.ngrok.io"  
PORT = 19495

# Tentukan bagian tugas
PARTS = ["honey", "cipher"]
WORKER_ID = random.randint(0, 1)
MY_PART = PARTS[WORKER_ID]

def search_part():
    """Cari domain dengan multi-threading."""
    print(f"[+] Worker mencari: {MY_PART}")

    process = subprocess.Popen(
        ["mkp224o", "-t", str(multiprocessing.cpu_count()), MY_PART],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        if line.startswith(MY_PART):
            print(f"[✔] Ditemukan: {line.strip()}")
            process.terminate()
            return line.strip()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((MASTER_IP, PORT))

found_onion = search_part()
client.sendall(f"{MY_PART}|{found_onion}".encode())

# Tunggu perintah dari Master
while True:
    try:
        message = client.recv(1024).decode()
        if message.startswith("FOUND|"):
            print(f"[🔥] Domain lengkap diterima dari Master: {message[6:]}")
            os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)
            break
    except:
        pass
