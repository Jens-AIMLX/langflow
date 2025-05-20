@echo off 
cd "D:\dev\Langflow\langflow\docker\frontend" 
echo. 
echo ---------------------------------------------------------------------------------- 
echo LangFlow Frontend started at 14:50:40,60 
echo ---------------------------------------------------------------------------------- 
call :log_cmd "npm start" ..\..\frontend.log 
goto :eof 
 
:log_cmd 
set cmd=%~1 
set logfile=%~2 
echo >> Executing: %cmd% 
echo. 
echo >> Command: %cmd% 
echo. 
 
REM Run the command and capture output to a temporary file 
%cmd% > temp_output.txt 2>&1 
 
REM Display the output to console 
type temp_output.txt 
 
REM Append the output to the log file 
type temp_output.txt >> %logfile% 
 
REM Clean up 
if exist temp_output.txt del temp_output.txt 
exit /b 
