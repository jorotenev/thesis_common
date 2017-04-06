from .redis_adaptor import RedisAdapter


class StoredPredictionsAdapter(RedisAdapter):
    def __init__(self, *args, **kwargs):
        super(StoredPredictionsAdapter, self).__init__(*args, **kwargs)
