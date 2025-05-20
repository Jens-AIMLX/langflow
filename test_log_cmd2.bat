@echo off
setlocal

echo Testing log_cmd function...

echo Creating test log file...
echo Test log file > test.log

echo Running test command...
call :run_and_log "dir" test.log

echo.
echo Test completed. Check test.log for results.
type test.log

goto :eof

:run_and_log
set cmd=%~1
set logfile=%~2
echo ^>^> Executing: %cmd%
echo. >> %logfile%
echo ^>^> Command: %cmd% >> %logfile%
echo. >> %logfile%
%cmd% | tee -a %logfile%
exit /b

endlocal
