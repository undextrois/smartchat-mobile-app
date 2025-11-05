import os
import sys
import winreg
import subprocess
from pathlib import Path
'''
how to run the mobile app into the emulator
step 1: python setup_cordova_path.py
step 2: emulator -avd Pixel_7
step 3: cordova run android
step 4: open a chrome tab and run chrome://inspect/#devices

WARNING      | adb command 'C:\Users\pc\AppData\Local\Android\Sdk\platform-tools\adb.exe -s 
emulator-5554 shell am start-foreground-service -e meter on com.android.emulator.radio.config/.MeterService ' failed: 'adb.exe: device offline'
'''
class CordovaPathSetup:
    def __init__(self):
        self.android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
        self.required_paths = []
        self.missing_paths = []
        self.existing_paths = []
        
    def detect_android_sdk(self):
        """Detect Android SDK location"""
        if self.android_home and Path(self.android_home).exists():
            print(f"✓ Android SDK found at: {self.android_home}")
            return True
        
        # Common Android SDK locations
        possible_locations = [
            Path.home() / "AppData/Local/Android/Sdk",
            Path("C:/Android/Sdk"),
            Path("C:/Program Files/Android/Sdk"),
            Path("C:/Program Files (x86)/Android/Sdk"),
        ]
        
        for location in possible_locations:
            if location.exists():
                self.android_home = str(location)
                print(f"✓ Android SDK found at: {self.android_home}")
                return True
        
        print("✗ Android SDK not found!")
        print("Please install Android Studio or set ANDROID_HOME environment variable.")
        return False
    
    def get_required_paths(self):
        """Get list of required paths for Cordova development"""
        if not self.android_home:
            return []
        
        base = Path(self.android_home)
        
        paths = [
            base / "emulator",
            base / "platform-tools",
            base / "tools",
            base / "tools/bin",
            base / "cmdline-tools/latest/bin",
        ]
        
        # Filter only existing paths
        self.required_paths = [str(p) for p in paths if p.exists()]
        return self.required_paths
    
    def get_current_user_path(self):
        """Get current user PATH from registry"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_READ) as key:
                path_value, _ = winreg.QueryValueEx(key, 'Path')
                return path_value
        except WindowsError:
            return ""
    
    def check_paths(self):
        """Check which paths are missing from user PATH"""
        current_path = self.get_current_user_path()
        current_paths = [p.strip() for p in current_path.split(';') if p.strip()]
        
        print("\n" + "="*70)
        print("CHECKING REQUIRED PATHS")
        print("="*70)
        
        for required_path in self.required_paths:
            # Normalize paths for comparison
            normalized_required = os.path.normpath(required_path).lower()
            found = any(os.path.normpath(p).lower() == normalized_required for p in current_paths)
            
            if found:
                print(f"✓ {required_path}")
                self.existing_paths.append(required_path)
            else:
                print(f"✗ {required_path} (MISSING)")
                self.missing_paths.append(required_path)
        
        return len(self.missing_paths) == 0
    
    def add_paths_to_user_path(self):
        """Permanently add missing paths to user PATH"""
        if not self.missing_paths:
            print("\n✓ All required paths are already in your PATH!")
            return True
        
        print(f"\n{'='*70}")
        print(f"ADDING {len(self.missing_paths)} MISSING PATH(S)")
        print("="*70)
        
        try:
            current_path = self.get_current_user_path()
            new_paths = self.missing_paths
            
            # Combine existing and new paths
            if current_path:
                new_path_value = current_path.rstrip(';') + ';' + ';'.join(new_paths)
            else:
                new_path_value = ';'.join(new_paths)
            
            # Write to registry
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, 
                               winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path_value)
            
            # Broadcast environment change
            self.broadcast_environment_change()
            
            for path in new_paths:
                print(f"✓ Added: {path}")
            
            print("\n" + "="*70)
            print("SUCCESS!")
            print("="*70)
            print("\nPaths have been permanently added to your user PATH.")
            print("\nIMPORTANT: Please restart your terminal/PowerShell for changes to take effect!")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Error adding paths to PATH: {e}")
            print("\nYou may need to run this script as Administrator.")
            return False
    
    def broadcast_environment_change(self):
        """Notify Windows of environment variable changes"""
        try:
            import win32gui
            import win32con
            win32gui.SendMessageTimeout(
                win32con.HWND_BROADCAST,
                win32con.WM_SETTINGCHANGE,
                0,
                'Environment',
                win32con.SMTO_ABORTIFHUNG,
                5000
            )
        except ImportError:
            # win32gui not available, changes will apply after restart
            pass
    
    def verify_commands(self):
        """Verify that commands are accessible"""
        print("\n" + "="*70)
        print("VERIFYING COMMANDS")
        print("="*70)
        
        commands = ['adb', 'emulator', 'avdmanager', 'sdkmanager']
        
        for cmd in commands:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, 
                                      timeout=5,
                                      text=True)
                if result.returncode == 0 or 'version' in result.stdout.lower() or 'version' in result.stderr.lower():
                    print(f"✓ {cmd} is accessible")
                else:
                    print(f"⚠ {cmd} exists but may not be working properly")
            except FileNotFoundError:
                print(f"✗ {cmd} not found (restart terminal needed)")
            except subprocess.TimeoutExpired:
                print(f"⚠ {cmd} timed out")
            except Exception as e:
                print(f"✗ {cmd} error: {e}")
    
    def check_android_home_env(self):
        """Check and suggest ANDROID_HOME environment variable"""
        print("\n" + "="*70)
        print("CHECKING ENVIRONMENT VARIABLES")
        print("="*70)
        
        android_home = os.environ.get('ANDROID_HOME')
        android_sdk_root = os.environ.get('ANDROID_SDK_ROOT')
        
        if android_home:
            print(f"✓ ANDROID_HOME: {android_home}")
        else:
            print(f"✗ ANDROID_HOME not set")
            self.set_android_home_env()
        
        if android_sdk_root:
            print(f"⚠ ANDROID_SDK_ROOT: {android_sdk_root} (DEPRECATED)")
    
    def set_android_home_env(self):
        """Set ANDROID_HOME environment variable"""
        if not self.android_home:
            return
        
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, 
                               winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, 'ANDROID_HOME', 0, winreg.REG_SZ, self.android_home)
            print(f"✓ Set ANDROID_HOME to: {self.android_home}")
        except Exception as e:
            print(f"✗ Could not set ANDROID_HOME: {e}")
    
    def run(self):
        """Main execution flow"""
        print("="*70)
        print("CORDOVA ANDROID PATH SETUP HELPER")
        print("="*70)
        print("\nThis script will check and add required Android SDK paths")
        print("to your Windows user PATH environment variable.\n")
        
        # Step 1: Detect Android SDK
        if not self.detect_android_sdk():
            return False
        
        # Step 2: Check ANDROID_HOME
        self.check_android_home_env()
        
        # Step 3: Get required paths
        self.get_required_paths()
        
        if not self.required_paths:
            print("\n✗ No valid Android SDK paths found!")
            return False
        
        print(f"\nFound {len(self.required_paths)} required path(s)")
        
        # Step 4: Check which paths are missing
        all_present = self.check_paths()
        
        # Step 5: Add missing paths
        if not all_present:
            print(f"\nDo you want to add {len(self.missing_paths)} missing path(s) to your user PATH? (y/n): ", end='')
            response = input().strip().lower()
            
            if response == 'y':
                self.add_paths_to_user_path()
            else:
                print("\n✗ Aborted. No changes were made.")
                return False
        
        # Step 6: Verify commands (will fail if terminal not restarted)
        self.verify_commands()
        
        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("1. Restart your terminal/PowerShell/Command Prompt")
        print("2. Run 'emulator -list-avds' to list available emulators")
        print("3. Run 'cordova run android' to deploy your app")
        print("="*70)
        
        return True

if __name__ == "__main__":
    if sys.platform != "win32":
        print("This script is designed for Windows only.")
        sys.exit(1)
    
    setup = CordovaPathSetup()
    success = setup.run()
    
    sys.exit(0 if success else 1)