from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Static
STATIC_URL = 'static/'
STATIC_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / '.static_root'

# Media
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': SECRET['DB']['NAME'],               # 데이터베이스 이름
        'USER': SECRET['DB']['USER'],               # 사용자 이름
        'PASSWORD': SECRET['DB']['PASSWORD'],       # 비밀번호
        'HOST': SECRET['DB']['HOST'],               # 데이터베이스 서버 주소
        'PORT': SECRET['DB']['PORT'],               # MySQL의 기본 포트
    }
}