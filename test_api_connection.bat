@echo off
echo ========================================
echo SMARTCHAT NETWORK DIAGNOSTICS
echo ========================================
echo.

echo Your Computer IP: 192.168.2.62
echo.

echo 1. Checking if Python/Flask is running on port 5000...
netstat -an | findstr ":5000"
echo.

echo 2. Testing local API access...
curl -s http://localhost:5000/api/test || echo "❌ Local API not accessible"
echo.

echo 3. Testing network API access...
curl -s http://192.168.2.62:5000/api/test || echo "❌ Network API not accessible"
echo.

echo 4. Windows Firewall status for port 5000...
netsh advfirewall firewall show rule name=all | findstr "5000" || echo "No specific firewall rules for port 5000 found"
echo.

echo ========================================
echo EMULATOR CONNECTION GUIDE:
echo - Android Emulator: http://10.0.2.2:5000/api
echo - Physical Device:  http://192.168.2.62:5000/api  
echo - Browser:          http://localhost:5000/api
echo ========================================
echo.

pause