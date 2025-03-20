#!/bin/bash
echo "[+] Memulai instalasi mkp224o di Worker..."

# Update & install dependensi
sudo apt update && sudo apt install -y build-essential git

# Clone dan build mkp224o
git clone https://github.com/cathugger/mkp224o.git
cd mkp224o
./autogen.sh && ./configure
make
sudo cp mkp224o /usr/local/bin/
cd ..
rm -rf mkp224o

# Cek apakah mkp224o terinstall dengan benar
if command -v mkp224o &> /dev/null; then
    echo "[✅] Instalasi selesai! Jalankan Worker dengan: python3 worker.py"
else
    echo "[❌] Instalasi gagal. Periksa kembali dependensi!"
fi
