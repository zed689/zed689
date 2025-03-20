import socket
import subprocess
import multiprocessing
import os
import signal

MASTER_IP = "0.tcp.ap.ngrok.io"
PORT = 19495
TARGET_PATTERN = "honeycipher"

def search_onion():
    """Cari domain dengan multi-threading."""
    print(f"[+] Worker mencari: {TARGET_PATTERN}")

    process = subprocess.Popen(
        ["mkp224o", "-t", str(multiprocessing.cpu_count()), TARGET_PATTERN],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        if line.startswith(TARGET_PATTERN):
            print(f"[✔] Ditemukan: {line.strip()}")
            process.terminate()
            return line.strip()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((MASTER_IP, PORT))

found_onion = search_onion()
client.sendall(found_onion.encode())

# Tunggu perintah dari Master untuk berhenti
while True:
    try:
        message = client.recv(1024).decode()
        if message.startswith("FOUND|"):
            print(f"[🔥] Domain lengkap diterima dari Master: {message[6:]}")
            os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)
            break
    except:
        pass
