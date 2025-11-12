import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 使用 SQL Server 身份验证
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',
        'mssql+pyodbc://sa:123456@localhost/BookCollectionDB?driver=ODBC+Driver+17+for+SQL+Server')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')