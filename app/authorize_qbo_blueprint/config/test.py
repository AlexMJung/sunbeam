import os

QBO_CLIENT_ID = os.environ.get('QBO_SANDBOX_CLIENT_ID', None)
QBO_CLIENT_SECRET = os.environ.get('QBO_SANDBOX_CLIENT_SECRET', None)
QBO_ACCOUNTING_API_BASE_URL = os.environ.get('QBO_SANDBOX_ACCOUNTING_API_BASE_URL', None)
QBO_PAYMENTS_API_BASE_URL = os.environ.get('QBO_SANDBOX_PAYMENTS_API_BASE_URL', None)
