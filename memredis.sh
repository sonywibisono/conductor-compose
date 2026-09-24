docker exec redis-master redis-cli -a SandiMasterRedis INFO memory 2>/dev/null | grep ^used_memory_human | cut -d':' -f2
