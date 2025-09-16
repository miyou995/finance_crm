
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'octopus_crm',
        'USER': 'postgres',
        'PASSWORD': 'miyou0209',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']

# RECAPTCHA_PUBLIC_KEY = '6LdpPdYqAAAAAC55bTR23cNwmdYPXIhE9WY7QpnU'
# RECAPTCHA_PRIVATE_KEY = '6LdpPdYqAAAAAOE-AzA4m6gtPTG6rSWWVVC1CbIz'

MAIN_DOMAIN = 'octo-school.com'


META_ACCESS_TOKEN ="EAAIqOXH4PzUBO7IldYqk8iM8Etd9uF5ZB4EPalP1zA3Cap8XxrnNX09AzGgZBogTJZALMGwDBgGNLv46pRgjZCtdLQZAzXsYfdbq12GL0KF4KhdS54RgloS2Aktn5VhjjQNTRCGwc96bmYDZBzxY3C4KMBwIUCOsewQEd9eiRlxK6KN2KpdAhZBCpj2fFt6k6MRigZDZD"

TEST_EVENT_CODE = 'TEST88869'

# SECRET_KEY = 'kxoy1-gkc!h)(4@o6rzp(i*_a+8xrw1ew7w_n6$#c=-l-tu(m3'
# DEBUG = False

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'mail.octopus-consulting.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'contact@octopus-consulting.com'
EMAIL_HOST_PASSWORD = 'octopus2022@'
DEFAULT_FROM_EMAIL = 'contact@octopus-consulting.com'
EMAIL_SUBJECT_PREFIX = 'Octo School'

# GLOBAL_IP_ADRESS = '188.245.254.78'


# DEBUG_TOOLBAR_CONFIG = {
#     'SHOW_TOOLBAR_CALLBACK': lambda r: False,  # disables it
#     # '...
# }


# SG_PASS = "MI.you@20905991"

# ROSETTA_AUTO_COMPILE = True
# ROSETTA_ENABLE_TRANSLATION_SUGGESTIONS = True
# DEEPL_AUTH_KEY = "0ebd1e8e-e507-cbe1-a6b1-73db89f49b9d:fx"




# SESSION_COOKIE_SECURE = True  # Use cookies only over HTTPS
# SECURE_SSL_REDIRECT = True

# CSRF_COOKIE_SECURE = True  # Use CSRF cookies only over HTTPS

# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
