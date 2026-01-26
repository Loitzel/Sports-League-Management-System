import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL')
    FOOTBALL_DATA_API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
    LDAP_SERVER = os.getenv('LDAP_SERVER')
    LDAP_BASE_DN = os.getenv('LDAP_BASE_DN')
    LDAP_BIND_DN = os.getenv('LDAP_BIND_DN')
    LDAP_BIND_PASSWORD = os.getenv('LDAP_BIND_PASSWORD')
    LDAP_USER_SEARCH_FILTER = os.getenv('LDAP_USER_SEARCH_FILTER', '(uid={username})')
