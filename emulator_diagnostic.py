#!/usr/bin/env python3
"""
Quick emulator diagnostic - helps identify why emulator isn't connecting to ADB
"""

import subprocess
import time
import sys

def run_cmd(cmd):
    """Run command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("🔍 EMULATOR DIAGNOSTIC TOOL")
    print("="*60)
    
    # 1. Check if emulator is in PATH
    print("\n1️⃣ Checking emulator installation...")
    result = run_cmd("where emulator")
    if result and result.returncode == 0:
        print(f"✅ Emulator found at: {result.stdout.strip()}")
    else:
        print("❌ Emulator not found in PATH")
        print("Fix: Add Android SDK emulator to PATH")
        print("Location: C:\\Users\\pc\\AppData\\Local\\Android\\Sdk\\emulator")
        sys.exit(1)
    
    # 2. List available AVDs
    print("\n2️⃣ Listing available AVDs...")
    result = run_cmd("emulator -list-avds")
    if result:
        avds = result.stdout.strip().split('\n')
        if avds and avds[0]:
            print("✅ Available AVDs:")
            for avd in avds:
                print(f"   • {avd}")
        else:
            print("❌ No AVDs found. Create one in Android Studio.")
            sys.exit(1)
    
    # 3. Check ADB
    print("\n3️⃣ Checking ADB...")
    result = run_cmd("adb version")
    if result and result.returncode == 0:
        version = result.stdout.split('\n')[0]
        print(f"✅ {version}")
    else:
        print("❌ ADB not found")
        sys.exit(1)
    
    # 4. Check current ADB devices
    print("\n4️⃣ Current ADB devices...")
    result = run_cmd("adb devices")
    if result:
        print(result.stdout)
    
    # 5. Start emulator with verbose output
    print("\n5️⃣ Starting emulator with diagnostics...")
    print("Command: emulator -avd Pixel_7 -no-snapshot-load -no-snapshot-save -verbose")
    print("\n⏳ Starting... (this will show emulator output for 90 seconds)")
    print("Watch for any ERROR or WARNING messages below:")
    print("-"*60)
    
    try:
        # Start emulator process
        proc = subprocess.Popen(
            "emulator -avd Pixel_7 -no-snapshot-load -no-snapshot-save -verbose",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Monitor output for 90 seconds
        start_time = time.time()
        emulator_found = False
        
        import threading
        import queue
        
        def read_output(proc, q):
            for line in iter(proc.stdout.readline, ''):
                q.put(line)
            q.put(None)
        
        q = queue.Queue()
        thread = threading.Thread(target=read_output, args=(proc, q))
        thread.daemon = True
        thread.start()
        
        print("\n📋 EMULATOR OUTPUT (first 90 seconds):\n")
        
        while time.time() - start_time < 90:
            try:
                line = q.get(timeout=1)
                if line is None:
                    break
                
                # Print line
                print(line.rstrip())
                
                # Check for key indicators
                if "INFO" in line and "boot completed" in line.lower():
                    print("\n✅ BOOT COMPLETED DETECTED!")
                    emulator_found = True
                
                if "ERROR" in line:
                    print(f"\n⚠️ ERROR DETECTED: {line.rstrip()}")
                    
            except queue.Empty:
                # Check ADB every few seconds
                if int(time.time() - start_time) % 15 == 0:
                    print(f"\n[{int(time.time() - start_time)}s] Checking ADB devices...")
                    result = run_cmd("adb devices")
                    if result and "emulator-" in result.stdout and "device" in result.stdout:
                        print("✅ EMULATOR APPEARED IN ADB!")
                        emulator_found = True
                        break
        
        print("\n" + "="*60)
        
        # Final check
        print("\n6️⃣ Final ADB device check...")
        result = run_cmd("adb devices")
        if result:
            print(result.stdout)
            if "emulator-" in result.stdout and "device" in result.stdout:
                print("\n✅ SUCCESS! Emulator is connected to ADB")
                print("\nYou can now run: cordova run android")
                print("\nPress Ctrl+C to stop the emulator...")
                
                try:
                    proc.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping emulator...")
                    proc.terminate()
            else:
                print("\n❌ Emulator still not visible in ADB")
                print("\nPossible issues:")
                print("  • Emulator is starting but ADB isn't detecting it")
                print("  • Try: adb kill-server && adb start-server")
                print("  • Check emulator output above for errors")
                print("  • Emulator might need more time (wait 2-3 minutes)")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
        proc.terminate()
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()