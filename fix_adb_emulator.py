#!/usr/bin/env python3
import subprocess
import time
import os

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result

print("🚀 Quick Fix: ADB & Emulator Reset")

# Kill everything
print("1. Killing existing processes...")
run_cmd("taskkill /f /im emulator.exe 2>nul")
run_cmd("taskkill /f /im adb.exe 2>nul")
time.sleep(3)

# Reset ADB
print("2. Resetting ADB...")
run_cmd("adb kill-server")
time.sleep(2)
run_cmd("adb start-server") 
time.sleep(2)

# Start emulator with clean state
print("3. Starting emulator with clean state...")
os.system("start cmd /k emulator -avd Pixel_7 -wipe-data -no-snapshot")

print("4. Waiting for boot...")
time.sleep(40)

# Final check
print("5. Checking device status...")
result = run_cmd("adb devices")
print(f"Devices: {result.stdout}")

print("✅ Ready! Now run: cordova run android")