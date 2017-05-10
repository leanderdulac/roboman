from roboman.stores import BaseStore
import motor


class Store(BaseStore):
    def __init__(self, **kwargs):
        super().__init__()
        self._cache = {}

        self.client = motor.motor_tornado.MotorClient(kwargs['uri'])
        self.db = self.client[kwargs['db']]

    def __getattribute__(self, key):
        if key in ['db', 'client']:
            return super().__getattribute__(key)

        db = super().__getattribute__('db')
        return getattr(db, key)