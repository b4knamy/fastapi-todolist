from secrets import token_hex
from datetime import timedelta

PAGINATION_PER_PAGE = 10

JWT_SECRET_KEY = token_hex(32)
JWT_HASH_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME = timedelta(hours=1)
