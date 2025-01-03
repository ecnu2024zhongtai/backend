
class RedisKey:
    # Trip
    RECENT_2MINS_TRIP_KEY_PREFIX = "recent_2mins_trips"
    RECENT_5MINS_TRIP_KEY_PREFIX = "recent_5mins_trips"
    RECENT_10MINS_TRIP_KEY_PREFIX = "recent_10mins_trips"
    RECENT_1HOUR_TRIP_KEY_PREFIX = "recent_1hour_trips"

    # Demand
    RECENT_10MINS_DEMANDS_KEY_PREFIX = "recent_10mins_demands"

    @staticmethod
    def recent_2mins_trip_key() -> str:
        return f"{RedisKey.RECENT_2MINS_TRIP_KEY_PREFIX}"
    
    @staticmethod
    def recent_5mins_trip_key() -> str:
        return f"{RedisKey.RECENT_5MINS_TRIP_KEY_PREFIX}"
    
    @staticmethod
    def recent_10mins_trip_key() -> str:
        return f"{RedisKey.RECENT_10MINS_TRIP_KEY_PREFIX}"
    
    @staticmethod
    def recent_1hour_trip_key() -> str:
        return f"{RedisKey.RECENT_1HOUR_TRIP_KEY_PREFIX}"
    
    @staticmethod
    def recent_10mins_demand_key() -> str:
        return f"{RedisKey.RECENT_10MINS_DEMANDS_KEY_PREFIX}"