"""
Django project configuration module.
Installs PyMySQL as MySQLdb fallback for robust Windows / Python 3.13 MySQL connectivity.
"""
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
