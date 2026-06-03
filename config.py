import os
class Config:
    SECRET_KEY='dev-secret-key-2026'
    SQLALCHEMY_DATABASE_URI='sqlite:///taskflow.db'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    LANGUAGES=['ar', 'en']
    BABEL_DEFAULT_LOCAL='ar'