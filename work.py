import socket
import subprocess
import random

MASTER_IP = "0.tcp.ap.ngrok.io"  # Ganti dengan IP server Master
PORT = 14161

# Masing-masing Worker mencari bagian yang berbeda
PARTS = ["ho", "ney", "ci", "ph", "er"]
WORKER_ID = random.randint(0, 4)  # Setiap Worker mencari bagian berbeda
MY_PART = PARTS[WORKER_ID]

def search_part():
    print(f"[+] Worker mencari: {MY_PART}")

    while True:
        result = subprocess.run(["mkp224o", MY_PART], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if line.startswith(MY_PART):
                return line.strip()  # Mengembalikan nama domain yang cocok

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((MASTER_IP, PORT))

found_onion = search_part()
client.sendall(f"{MY_PART}|{found_onion}".encode())

# Tunggu perintah STOP dari Master
while True:
    try:
        message = client.recv(1024).decode()
        if message == "STOP":
            print("[!] Proses dihentikan oleh Master")
            client.close()
            exit()
    except:
        pass
