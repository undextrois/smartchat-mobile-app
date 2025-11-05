@echo off
echo 🔍 TESTING NETWORK FROM EMULATOR

echo 1. Checking if emulator can resolve 10.0.2.2...
adb shell ping -c 2 10.0.2.2

echo.
echo 2. Testing if port 5000 is open from emulator...
adb shell nc -z -w 5 10.0.2.2 5000 && echo "✅ Port 5000 is open" || echo "❌ Port 5000 is closed"

echo.
echo 3. Checking active network connections in emulator...
adb shell netstat -an | findstr ":5000"

echo.
echo 4. Testing raw HTTP request from emulator...
adb shell "echo 'GET / HTTP/1.1\r\nHost: 10.0.2.2:5000\r\n\r\n' | nc 10.0.2.2 5000"