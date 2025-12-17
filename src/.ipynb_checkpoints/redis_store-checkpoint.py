import redis

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

def update_velocity(user_id):
    key_1h = f"txn_1h:{user_id}"
    key_24h = f"txn_24h:{user_id}"

    redis_client.incr(key_1h)
    redis_client.expire(key_1h, 3600)

    redis_client.incr(key_24h)
    redis_client.expire(key_24h, 86400)

def get_velocity(user_id):
    v1 = redis_client.get(f"txn_1h:{user_id}") or 0
    v24 = redis_client.get(f"txn_24h:{user_id}") or 0
    return int(v1), int(v24)



# -----------------------------
# Pre-fill for testing
# -----------------------------
def prefill_velocity(user_id, v1h=20, v24h=100):
    """
    Pre-fill Redis counters to simulate high transaction velocity.
    """
    key_1h = f"txn_1h:{user_id}"
    key_24h = f"txn_24h:{user_id}"

    redis_client.set(key_1h, v1h)
    redis_client.expire(key_1h, 3600)

    redis_client.set(key_24h, v24h)
    redis_client.expire(key_24h, 86400)

    print(f"✅ Redis pre-filled for user {user_id}: txn_velocity_1h={v1h}, txn_velocity_24h={v24h}")


