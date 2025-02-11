import redis


class CacheManager:
    """
    A class that manages cache using Redis. It keeps track of orders in the current cycle and can
    remove old ones that are not relevant anymore.

    Example usage:

    >>> cache_manager = CacheManager("test")
    >>> for i in ["----", "1", "2", "3"]:
    ...     print(i, cache_manager.check(i))
    ---- False
    1 False
    2 False
    3 False

    >>> cache_manager.finalize_cycle()

    >>> for i in ["----", "1", "2", "3", "4"]:
    ...     print(i, cache_manager.check(i))
    ---- True
    1 True
    2 True
    3 True
    4 False

    >>> cache_manager.finalize_cycle()

    >>> for i in ["----", "5", "6", "3"]:
    ...     print(i, cache_manager.check(i))
    ---- True
    5 False
    6 False
    3 True

    >>> cache_manager.finalize_cycle()

    >>> for i in ["----", 2, 3, 4, 5, 6]:
    ...     print(str(i), cache_manager.check(i))
    ---- True
    2 False
    3 True
    4 False
    5 True
    6 True
    """

    def __init__(self, cache_key, redis_host="localhost", redis_port=6379, redis_db=0):
        self.redis_client = redis.StrictRedis(
            host=redis_host, port=redis_port, db=redis_db, decode_responses=True
        )
        self.cache_key = cache_key
        if cache_key == "test":
            cached_items = self.get_cache()
            if cached_items:
                self.redis_client.srem(self.cache_key, *cached_items)
        self.current_cycle_orders = set()

    def check(self, order_id):
        if self.redis_client.sismember(self.cache_key, order_id):
            self.redis_client.sadd(self.cache_key, order_id)
            self.current_cycle_orders.add(order_id)
            return True
        else:
            self.redis_client.sadd(self.cache_key, order_id)
            self.current_cycle_orders.add(order_id)
            return False

    def get_cache(self):
        return self.redis_client.smembers(self.cache_key)

    def end_cycle(self):
        """
        This function is called after the polling cycle completes.
        It removes cache entries that were present in the cache but did not appear in the current cycle.
        """
        cached_strings = self.redis_client.smembers(self.cache_key)
        strings_to_remove = set(cached_strings) - self.current_cycle_orders
        if strings_to_remove:
            self.redis_client.srem(self.cache_key, *strings_to_remove)
        self.current_cycle_orders.clear()


if __name__ == "__main__":
    import doctest

    doctest.testmod()
