
class RedisKey:
    RECENT_2MINS_TRIP_KEY_PREFIX = "recent_2mins_trips"
    RECENT_1HOUR_TRIP_KEY_PREFIX = "recent_1hour_trips"


    @staticmethod
    def recent_2mins_trip_key() -> str:
        return f"{RedisKey.RECENT_2MINS_TRIP_KEY_PREFIX}"
    
    @staticmethod
    def recent_1hour_trip_key() -> str:
        return f"{RedisKey.RECENT_1HOUR_TRIP_KEY_PREFIX}"