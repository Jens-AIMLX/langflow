@echo off
setlocal

echo Testing log_cmd function...

:log_cmd
set cmd=%~1
set logfile=%~2
echo ^>^> Executing: %cmd%
echo. >> %logfile%
echo ^>^> Command: %cmd% >> %logfile%
echo. >> %logfile%
REM Run the command and capture output to a temporary file
%cmd% > temp_output.txt 2>&1
REM Display the output to console
type temp_output.txt
REM Append the output to the log file
type temp_output.txt >> %logfile%
REM Clean up
del temp_output.txt
exit /b

echo Creating test log file...
echo Test log file > test.log

echo Running test command...
call :log_cmd "dir" test.log

echo.
echo Test completed. Check test.log for results.
type test.log

endlocal
