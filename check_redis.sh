#!/bin/bash

# Threshold penggunaan Redis (dalam persentase)
THRESHOLD=80

# Fungsi untuk mendapatkan total memori sistem (dalam KB)
get_total_mem_kb() {
    grep MemTotal /proc/meminfo | awk '{print $2}'
}

# Fungsi untuk mendapatkan penggunaan Redis (dalam KB)
get_redis_usage_kb() {
    pid=$(pgrep redis-server)
    if [ -z "$pid" ]; then
        echo "Redis tidak berjalan."
        exit 1
    fi
    # Ambil RSS memory dari redis-server
    ps -o rss= -p "$pid"
}

# Fungsi untuk me-restart Conductor (ubah sesuai kebutuhan)
restart_conductor() {
    echo "🛑 Menggunakan memori terlalu tinggi. Restarting Conductor..."
    #systemctl restart conductor || docker restart conductor || echo "Gagal me-restart Conductor"
    docker compose down
}

# Main
total_mem_kb=$(get_total_mem_kb)
redis_usage_kb=$(get_redis_usage_kb)

# Hitung persentase
usage_percent=$((redis_usage_kb * 100 / total_mem_kb))

echo "Redis memory usage: ${usage_percent}%"

if [ "$usage_percent" -ge "$THRESHOLD" ]; then
    restart_conductor
else
    echo "✅ Penggunaan Redis masih aman."
fi
