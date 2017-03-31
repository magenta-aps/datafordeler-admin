@echo off
call %~dp0%configure_environment.bat
start python manage.py runserver 0.0.0.0:8000
