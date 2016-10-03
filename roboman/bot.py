import traceback
import requests
from tornado.httputil import url_concat
from tornkts.handlers import BaseHandler
import random
import string
import logging
from .keyboard import Keyboard

try:
    import ujson as json
except:
    import json as json

__author__ = 'grigory51'


class BaseBot(object):
    MODE_HOOK = 'hook'
    MODE_GET_UPDATES = 'get_updates'

    name = None
    key = None
    access_key = None

    connection = requests.Session()

    def __init__(self):
        super().__init__()
        self.text = ''
        self.chat_id = None
        self.logger = logging.getLogger(self.name)

    def _before_hook(self, payload):
        pass

    def _on_hook(self, payload):
        raise NotImplemented

    def before_hook(self, data):
        self.text = data.get('text', '')
        self.chat_id = data.get('chat_id', None)
        self._before_hook(data)

    def on_hook(self, data):
        message = data.get('message')
        if not isinstance(message, dict):
            message = data.get('callback_query', {}).get('message')
            if isinstance(message, dict):
                user = data.get('callback_query', {}).get('from')
            else:
                user = {}
        else:
            user = message.get('from', {})

        if isinstance(message, dict):
            payload = {
                'text': message.get('text'),
                'date': message.get('date'),

                'chat_id': message.get('chat', {}).get('id', None),
                'chat_title': message.get('chat', {}).get('title', None),

                'from_id': user.get('id', None),
                'from_username': user.get('username', None),
                'from_first_name': user.get('first_name', None),
                'from_last_name': user.get('last_name', None),

                'location': message.get('location', None),
                'photo': message.get('photo', None),

                'callback_query': data.get('callback_query', {}).get('data', None),
                'callback_query_id': data.get('callback_query', {}).get('id', None)
            }

            try:
                updated_payload = self.before_hook(payload)
                if updated_payload:
                    payload = updated_payload
                self._on_hook(payload)
            except:
                traceback.print_exc()

    def match_command(self, command=None, text=None):
        if command is None:
            return False

        if text is None:
            text = self.text

        text = text.strip()
        if text.startswith(command):
            text = text[len(command):].strip()
            return {
                'result': True,
                'args': [i for i in text.split(' ')]
            }

        return False

    def send(self, text='', **params):
        if 'text' not in params:
            params['text'] = text
        if 'chat_id' not in params:
            params['chat_id'] = self.chat_id
        if 'reply_markup' in params and isinstance(params['reply_markup'], Keyboard):
            params['reply_markup'] = params['reply_markup'].to_json()

        res = self.connection.post(self.get_method_url('sendMessage'), params=params)
        if res.status_code != 200:
            self.logger.error(res.text)

    def answer_callback_query(self, **params):
        if 'chat_id' not in params:
            params['chat_id'] = self.chat_id

        res = self.connection.post(self.get_method_url('answerCallbackQuery'), params=params)
        if res.status_code != 200:
            self.logger.error(res.text)

    def send_photo(self, files, **params):
        if 'chat_id' not in params:
            params['chat_id'] = self.chat_id

        res = self.connection.post(self.get_method_url('sendPhoto'), files=files, params=params)
        if res.status_code != 200:
            self.logger.error(res.text)

    def send_location(self, **params):
        if 'chat_id' not in params:
            params['chat_id'] = self.chat_id

        res = self.connection.post(self.get_method_url('sendLocation'), params=params)
        if res.status_code != 200:
            self.logger.error(res.text)

    @classmethod
    def get_file_url(cls, path, params=None):
        return 'https://api.telegram.org/file/bot' + cls.key + '/' + path

    @classmethod
    def get_method_url(cls, method, params=None):
        url = 'https://api.telegram.org/bot' + cls.key + '/' + method
        if params is not None:
            url = url_concat(url, params)
        return url

    @classmethod
    def get_webhook_url(cls):
        cls.access_key = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(30)])
        return options.server_schema + '://' + options.server_name + '/telegram.' + cls.access_key
