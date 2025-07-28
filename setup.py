#!/usr/bin/env python3
"""
Setup configuration for Nomadly3 Platform
Clean Architecture Domain Registration System
"""

from setuptools import setup, find_packages

setup(
    name="nomadly3",
    version="1.4.0",
    description="Nomadly3 - Offshore Domain Registration Platform",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "python-telegram-bot>=20.7",
        "sqlalchemy>=2.0",
        "psycopg2-binary>=2.9",
        "aiohttp>=3.8",
        "requests>=2.31",
        "python-dotenv>=1.0",
        "flask>=2.3",
        "qrcode>=7.4",
        "pillow>=10.0",
        "python-dateutil>=2.8",
        "pymongo>=4.6",
        "sendgrid>=6.10",
        "urllib3>=2.0",
        "werkzeug>=2.3",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "httpx>=0.25.0",
        "pydantic[email]>=2.5.0"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)