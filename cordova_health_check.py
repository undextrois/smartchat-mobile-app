#!/usr/bin/env python3
"""
Cordova Android Health Check Script v3
Enhanced with dynamic emulator detection and snapshot handling
"""

import subprocess
import sys
import os
import time
import re
from pathlib import Path

class CordovaHealthCheck:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.avd_name = "Pixel_4"
        self.cordova_project_dir = os.getcwd()
        self.emulator_process = None
        self.emulator_serial = None
        
    def run_command(self, cmd, capture_output=True, shell=True, timeout=60):
        """Execute a command and return result"""
        try:
            if capture_output:
                result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
                return result
            else:
                result = subprocess.run(cmd, shell=shell, text=True, timeout=timeout)
                return result
        except subprocess.TimeoutExpired:
            self.issues.append(f"Command timed out: {cmd}")
            return None
        except Exception as e:
            self.issues.append(f"Error executing command '{cmd}': {str(e)}")
            return None

    def get_active_emulator_serial(self):
        """Dynamically detect the active emulator serial"""
        result = self.run_command("adb devices")
        if result and result.stdout:
            # Look for emulator-XXXX in the output
            matches = re.findall(r'(emulator-\d+)\s+device', result.stdout)
            if matches:
                return matches[0]
        return None

    def wait_for_device_fully_ready(self, timeout=180):
        """Wait for device to be fully ready with dynamic serial detection"""
        print("⏳ Waiting for device to be fully ready...")
        
        start_time = time.time()
        steps_passed = 0
        total_steps = 5
        
        while time.time() - start_time < timeout:
            try:
                # Step 1: Detect emulator serial dynamically
                if not self.emulator_serial:
                    self.emulator_serial = self.get_active_emulator_serial()
                    if self.emulator_serial:
                        steps_passed = max(steps_passed, 1)
                        print(f"✅ Step 1/5: Emulator detected ({self.emulator_serial})")
                    else:
                        time.sleep(5)
                        continue
                
                # Step 2: Check if device is recognized and online
                devices_result = self.run_command("adb devices")
                if devices_result and self.emulator_serial in devices_result.stdout and "offline" not in devices_result.stdout:
                    steps_passed = max(steps_passed, 2)
                    if steps_passed == 2:
                        print("✅ Step 2/5: ADB device online")
                    
                    # Step 3: Check boot completion
                    boot_result = self.run_command(f"adb -s {self.emulator_serial} shell getprop sys.boot_completed", timeout=10)
                    if boot_result and "1" in boot_result.stdout.strip():
                        steps_passed = max(steps_passed, 3)
                        if steps_passed == 3:
                            print("✅ Step 3/5: System boot completed")
                        
                        # Step 4: Check package manager is ready
                        pm_result = self.run_command(f"adb -s {self.emulator_serial} shell pm path android", timeout=10)
                        if pm_result and pm_result.returncode == 0:
                            steps_passed = max(steps_passed, 4)
                            if steps_passed == 4:
                                print("✅ Step 4/5: Package manager ready")
                            
                            # Step 5: Check if system is fully responsive
                            service_result = self.run_command(f"adb -s {self.emulator_serial} shell service check package", timeout=10)
                            if service_result and "found" in service_result.stdout:
                                steps_passed = max(steps_passed, 5)
                                print("✅ Step 5/5: System services ready")
                                print("🎉 Device is fully ready!")
                                return True
                
                time.sleep(5)
                elapsed = int(time.time() - start_time)
                print(f"⏳ Device readiness: {steps_passed}/{total_steps} (elapsed: {elapsed}s/{timeout}s)")
                
            except Exception as e:
                print(f"⚠️ Check interrupted: {e}")
                time.sleep(5)
        
        print(f"❌ Device not fully ready within {timeout} seconds. Progress: {steps_passed}/{total_steps}")
        return False

    def force_adb_reconnection(self):
        """Force ADB reconnection and reset"""
        print("🔄 Performing aggressive ADB reset...")
        
        # Kill ADB server
        self.run_command("adb kill-server", capture_output=False)
        time.sleep(3)
        
        # Start ADB server
        self.run_command("adb start-server", capture_output=False)
        time.sleep(5)
        
        # List devices
        result = self.run_command("adb devices")
        if result:
            print(f"📱 Connected devices:\n{result.stdout}")
        
        # Detect emulator
        self.emulator_serial = self.get_active_emulator_serial()
        
        return self.emulator_serial is not None

    def clear_emulator_snapshots(self):
        """Clear potentially corrupted snapshots"""
        print("🗑️ Clearing emulator snapshots to avoid boot issues...")
        
        avd_dir = os.path.expanduser(f"~/.android/avd/{self.avd_name}.avd")
        if not os.path.exists(avd_dir):
            avd_dir = os.path.expanduser(f"~\\.android\\avd\\{self.avd_name}.avd")
        
        if os.path.exists(avd_dir):
            snapshot_dir = os.path.join(avd_dir, "snapshots")
            if os.path.exists(snapshot_dir):
                try:
                    import shutil
                    shutil.rmtree(snapshot_dir)
                    print("✅ Snapshots cleared")
                    return True
                except Exception as e:
                    print(f"⚠️ Could not clear snapshots: {e}")
                    self.warnings.append("Could not clear snapshots, may cause boot delays")
            else:
                print("ℹ️ No snapshots directory found")
        else:
            print(f"⚠️ AVD directory not found: {avd_dir}")
        
        return False

    def start_emulator_with_retry(self, max_retries=2):
        """Start emulator with retry logic and snapshot handling"""
        
        # Clear snapshots first to avoid corruption issues
        self.clear_emulator_snapshots()
        
        for attempt in range(max_retries):
            print(f"\n🚀 Starting emulator attempt {attempt + 1}/{max_retries}...")
            
            # Clean up any existing emulator processes
            self.run_command("taskkill /f /im emulator.exe 2>nul", capture_output=False)
            self.run_command("taskkill /f /im qemu-system-x86_64.exe 2>nul", capture_output=False)
            time.sleep(5)
            
            # Reset emulator serial
            self.emulator_serial = None
            
            # Start emulator with options to avoid snapshot issues
            emulator_cmd = f"emulator -avd {self.avd_name} -no-snapshot-load -no-snapshot-save -no-audio -gpu swiftshader_indirect"
            
            print(f"📝 Command: {emulator_cmd}")
            
            try:
                self.emulator_process = subprocess.Popen(
                    emulator_cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Wait for emulator to initialize
                print("⏳ Waiting for emulator to initialize (45 seconds)...")
                time.sleep(45)
                
                # Reset ADB connection
                if self.force_adb_reconnection():
                    print(f"✅ ADB connected to: {self.emulator_serial}")
                    
                    # Wait for device to be fully ready with longer timeout for cold boot
                    if self.wait_for_device_fully_ready(timeout=180):
                        # Extra stability wait
                        print("⏳ Final stability wait (10 seconds)...")
                        time.sleep(10)
                        return True
                
                # If we get here, this attempt failed
                print(f"❌ Emulator attempt {attempt + 1} failed")
                self.stop_emulator()
                time.sleep(10)
                
            except Exception as e:
                print(f"❌ Exception starting emulator: {e}")
                self.stop_emulator()
                time.sleep(10)
        
        return False

    def stop_emulator(self):
        """Stop the emulator"""
        if self.emulator_process:
            try:
                self.emulator_process.terminate()
                self.emulator_process.wait(timeout=10)
            except:
                try:
                    self.emulator_process.kill()
                except:
                    pass
            self.emulator_process = None
        
        # Also kill any orphaned emulator processes
        self.run_command("taskkill /f /im emulator.exe 2>nul", capture_output=False)
        self.run_command("taskkill /f /im qemu-system-x86_64.exe 2>nul", capture_output=False)

    def install_and_run_cordova(self):
        """Install and run Cordova app with dynamic serial"""
        if not self.emulator_serial:
            self.emulator_serial = self.get_active_emulator_serial()
            if not self.emulator_serial:
                self.issues.append("Could not detect emulator serial")
                return False
        
        print(f"\n📦 Building and installing Cordova app to {self.emulator_serial}...")
        
        # First, build the app
        print("🔨 Building app...")
        build_result = self.run_command("cordova build android", capture_output=False, timeout=120)
        if build_result and build_result.returncode != 0:
            self.issues.append("Cordova build failed")
            return False
        
        print("✅ Build successful")
        time.sleep(2)
        
        # Try Cordova run with detected emulator
        print(f"📲 Installing to {self.emulator_serial}...")
        install_result = self.run_command(f"cordova run android --nobuild --target={self.emulator_serial}", capture_output=False, timeout=120)
        
        if install_result and install_result.returncode == 0:
            print("✅ App installed and launched successfully")
            return True
        else:
            # Fallback: Try direct ADB installation
            print("🔄 Trying alternative installation method...")
            apk_path = self.find_apk_file()
            if apk_path:
                install_cmd = f'adb -s {self.emulator_serial} install -r "{apk_path}"'
                install_result = self.run_command(install_cmd, capture_output=False, timeout=60)
                if install_result and install_result.returncode == 0:
                    print("✅ App installed via ADB")
                    
                    # Launch the app
                    package_name = self.get_package_name()
                    if package_name:
                        launch_cmd = f'adb -s {self.emulator_serial} shell am start -n {package_name}/.MainActivity'
                        self.run_command(launch_cmd, capture_output=False)
                        print("✅ App launched")
                        return True
            
            self.issues.append("Failed to install and launch app")
            return False

    def find_apk_file(self):
        """Find the built APK file"""
        possible_paths = [
            "platforms/android/app/build/outputs/apk/debug/app-debug.apk",
            "platforms/android/app/build/outputs/apk/debug/app-debug-unaligned.apk", 
            "platforms/android/build/outputs/apk/debug/app-debug.apk",
        ]
        
        for path in possible_paths:
            full_path = os.path.join(self.cordova_project_dir, path)
            if os.path.exists(full_path):
                return full_path
        return None

    def get_package_name(self):
        """Extract package name from config.xml"""
        config_path = os.path.join(self.cordova_project_dir, "config.xml")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'<widget[^>]*id="([^"]+)"', content)
                if match:
                    return match.group(1)
        except Exception as e:
            print(f"⚠️ Could not read package name: {e}")
        
        return "com.example.hello"  # Fallback package name

    def perform_health_check(self):
        """Perform basic health checks"""
        print("🔍 Performing environment health checks...")
        
        checks = [
            ("Java", "java -version"),
            ("Node.js", "node --version"), 
            ("Cordova", "cordova --version"),
            ("ADB", "adb version")
        ]
        
        for check_name, cmd in checks:
            result = self.run_command(cmd)
            if result and result.returncode == 0:
                print(f"✅ {check_name} check passed")
            else:
                self.issues.append(f"{check_name} check failed")
                return False
        
        return True

    def generate_report(self):
        """Generate health report"""
        print("\n" + "="*60)
        print("CORDOVA HEALTH CHECK REPORT")
        print("="*60)
        
        if self.issues:
            print("❌ CRITICAL ISSUES:")
            for issue in self.issues:
                print(f"  • {issue}")
        else:
            print("✅ No critical issues found")
            
        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        print("="*60)

    def cleanup(self):
        """Cleanup resources"""
        self.stop_emulator()

def main():
    health_check = CordovaHealthCheck()
    
    try:
        # Perform basic health checks
        if not health_check.perform_health_check():
            health_check.generate_report()
            print("\n❌ Pre-requisites failed. Please fix issues above.")
            sys.exit(1)
        
        print("\n✅ Environment checks passed!")
        
        # Start emulator with retry logic
        if health_check.start_emulator_with_retry():
            print("\n🎉 Emulator is ready and stable!")
            
            # Install and run Cordova app
            if health_check.install_and_run_cordova():
                print("\n✨ SUCCESS! Your Cordova app should be running in the emulator.")
                print("\n📱 The app will stay open. Press Ctrl+C to stop the emulator when done.")
                
                # Keep the script running to maintain the emulator
                try:
                    health_check.emulator_process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping emulator...")
            else:
                health_check.generate_report()
                print("\n❌ Failed to install/run Cordova app")
        else:
            health_check.generate_report()
            print("\n❌ Failed to start emulator properly")
            
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        health_check.issues.append(f"Unexpected error: {e}")
        health_check.generate_report()
    
    finally:
        health_check.cleanup()

if __name__ == "__main__":
    main()