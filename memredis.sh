docker exec sony-redis-1 redis-cli INFO memory | grep ^used_memory_human | cut -d':' -f2
