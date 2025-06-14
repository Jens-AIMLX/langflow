@echo off
cd /d C:\nginx\nginx-1.26.0
nginx.exe -c conf\nginx.conf

REM Show nginx error log if nginx exits
if exist logs\error.log (
    echo.
    echo --- NGINX ERROR LOG ---
    type logs\error.log
    echo --- END OF ERROR LOG ---
) else (
    echo No error log found.
)

pause 