from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Rate Limiter Initialization
limiter = Limiter(key_func=get_remote_address)
