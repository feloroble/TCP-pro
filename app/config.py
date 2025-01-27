import os
from itsdangerous import URLSafeTimedSerializer


SECRET_KEY = 'fgdsgdfgdfgdf7567ñk7m56km757585648564864856484868*/8*66658665'
SECURITY_PASSWORD_SALT = 'qC£!mH&q7_A0hr43b£-xQ/944G8vN8ek`U\~}HZt'
DATABASE = {
        'name': 'tcp_db',
        'engine': 'peewee.MySQLDatabase',
        'user': 'tactil',
        'password': 'Charlotte2024*',
        'host': 'localhost',
        'port': 3306,
    }

MAIL = {
    'mail_server':'smtp.tecnotactil.com',
    'mail_port': 587,
    'mail_use_TLS': True,
    'mail_usename':'tcp@tecnotactil.com',
    'mail_password':'[6yo13}HtQU8',
    'mail_default_sender':'tcp@tecnotactil.com'
}



UPLOAD_FOLDER = os.path.join('/static', 'uploads', 'products')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}



def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SECURITY_PASSWORD_SALT)

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(token, salt=SECURITY_PASSWORD_SALT, max_age=expiration)
    except Exception:
        return False
    return email