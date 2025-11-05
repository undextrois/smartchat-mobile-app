@echo off
echo Finding your IP address...
ipconfig | findstr "IPv4"
echo.
echo Testing common emulator URLs...
echo 1. 10.0.2.2:5000 - Android Emulator to Host
echo 2. 192.168.1.100:5000 - Physical Device to Host (change IP as needed)
echo 3. localhost:5000 - Browser development
echo.
pause