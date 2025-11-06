#!/usr/bin/env python3
"""
SmartChat System Audit v1.0
Comprehensive system requirements audit for mobile development environment
# Basic audit
python smartchat_audit.py

# Verbose mode with debug info
python smartchat_audit.py --verbose

# Custom report filename
python smartchat_audit.py --output my_audit.txt

# Show help
python smartchat_audit.py --help
"""

import subprocess
import sys
import os
import platform
import re
import threading
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    @staticmethod
    def disable():
        """Disable colors for non-supporting terminals"""
        Colors.GREEN = ''
        Colors.RED = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''
        Colors.CYAN = ''
        Colors.BOLD = ''
        Colors.RESET = ''

# Check if terminal supports colors
if platform.system() == 'Windows':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        Colors.disable()

class ProgressSpinner:
    """Animated progress spinner for long-running operations"""
    def __init__(self, message="Processing"):
        self.spinner = ['|', '/', '-', '\\']
        self.idx = 0
        self.message = message
        self.running = False
        self.thread = None
        
    def spin(self):
        while self.running:
            sys.stdout.write(f'\r{Colors.CYAN}[{self.spinner[self.idx]}]{Colors.RESET} {self.message}...')
            sys.stdout.flush()
            self.idx = (self.idx + 1) % len(self.spinner)
            time.sleep(0.1)
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

class AuditResult:
    """Store result of a single audit check"""
    def __init__(self, name: str, passed: bool, details: str = "", 
                 warning: bool = False, fix_suggestion: str = ""):
        self.name = name
        self.passed = passed
        self.details = details
        self.warning = warning
        self.fix_suggestion = fix_suggestion
    
    def status_symbol(self) -> str:
        if self.warning:
            return f"{Colors.YELLOW}⚠{Colors.RESET}"
        return f"{Colors.GREEN}✓{Colors.RESET}" if self.passed else f"{Colors.RED}✗{Colors.RESET}"
    
    def status_text(self) -> str:
        if self.warning:
            return f"{Colors.YELLOW}WARNING{Colors.RESET}"
        return f"{Colors.GREEN}PASS{Colors.RESET}" if self.passed else f"{Colors.RED}FAIL{Colors.RESET}"

class SystemAuditor:
    """Main audit system for checking development environment"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[AuditResult] = []
        self.start_time = time.time()
        self.system_info = {
            'os': platform.system(),
            'os_version': platform.version(),
            'architecture': platform.machine(),
            'python_version': platform.python_version()
        }
    
    def log(self, message: str):
        """Log verbose messages"""
        if self.verbose:
            print(f"{Colors.BLUE}[DEBUG]{Colors.RESET} {message}")
    
    def run_command(self, cmd: List[str], timeout: int = 10) -> Tuple[bool, str, str]:
        """Execute system command and return success status and output"""
        try:
            self.log(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False
            )
            return (result.returncode == 0, result.stdout.strip(), result.stderr.strip())
        except subprocess.TimeoutExpired:
            return (False, "", f"Command timed out after {timeout} seconds")
        except FileNotFoundError:
            return (False, "", "Command not found")
        except Exception as e:
            return (False, "", str(e))
    
    def check_java(self) -> AuditResult:
        """Check OpenJDK 17.0.17 installation"""
        spinner = ProgressSpinner("Checking Java Development Kit")
        spinner.start()
        
        success, stdout, stderr = self.run_command(['java', '-version'])
        spinner.stop()
        
        if not success:
            return AuditResult(
                "OpenJDK 17.0.17",
                False,
                "Not installed",
                fix_suggestion="Download and install OpenJDK 17.0.17 from https://adoptium.net/"
            )
        
        # Parse Java version from stderr (Java outputs version to stderr)
        version_output = stderr if stderr else stdout
        version_match = re.search(r'version "(\d+\.\d+\.\d+)', version_output)
        
        if version_match:
            version = version_match.group(1)
            major_version = int(version.split('.')[0])
            
            if major_version == 17:
                return AuditResult("OpenJDK 17.0.17", True, version)
            else:
                return AuditResult(
                    "OpenJDK 17.0.17",
                    False,
                    f"Found version {version}, requires 17.x.x",
                    warning=(major_version >= 17),
                    fix_suggestion="Install OpenJDK 17.0.17 from https://adoptium.net/"
                )
        
        return AuditResult("OpenJDK 17.0.17", False, "Version could not be determined")
    
    def check_cordova(self) -> AuditResult:
        """Check Cordova installation"""
        spinner = ProgressSpinner("Checking Cordova")
        spinner.start()
        
        success, stdout, stderr = self.run_command(['cordova', '--version'])
        spinner.stop()
        
        if not success:
            return AuditResult(
                "Cordova (latest)",
                False,
                "Not installed",
                fix_suggestion="Install Cordova: npm install -g cordova"
            )
        
        version = stdout.strip()
        return AuditResult("Cordova (latest)", True, version)
    
    def check_android_studio(self) -> AuditResult:
        """Detect Android Studio installation"""
        spinner = ProgressSpinner("Checking Android Studio")
        spinner.start()
        
        # Common Android Studio paths
        if platform.system() == 'Windows':
            common_paths = [
                Path(os.environ.get('ProgramFiles', 'C:\\Program Files')) / 'Android' / 'Android Studio',
                Path(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')) / 'Android' / 'Android Studio',
                Path(os.environ.get('LOCALAPPDATA', '')) / 'Android' / 'Sdk'
            ]
        else:
            common_paths = [
                Path.home() / 'Android' / 'Sdk',
                Path('/usr/local/android-studio'),
                Path('/opt/android-studio')
            ]
        
        spinner.stop()
        
        for path in common_paths:
            if path.exists():
                return AuditResult("Android Studio", True, str(path))
        
        return AuditResult(
            "Android Studio",
            False,
            "Not found in common locations",
            fix_suggestion="Download and install Android Studio from https://developer.android.com/studio"
        )
    
    def check_android_sdk(self) -> Tuple[AuditResult, Optional[Path]]:
        """Locate Android SDK installation"""
        spinner = ProgressSpinner("Checking Android SDK")
        spinner.start()
        
        # Check ANDROID_HOME or ANDROID_SDK_ROOT
        sdk_path = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
        
        if sdk_path and Path(sdk_path).exists():
            spinner.stop()
            return (AuditResult("Android SDK", True, sdk_path), Path(sdk_path))
        
        # Check common locations
        if platform.system() == 'Windows':
            common_paths = [
                Path(os.environ.get('LOCALAPPDATA', '')) / 'Android' / 'Sdk',
                Path(os.environ.get('USERPROFILE', '')) / 'AppData' / 'Local' / 'Android' / 'Sdk',
            ]
        else:
            common_paths = [
                Path.home() / 'Android' / 'Sdk',
                Path.home() / 'Library' / 'Android' / 'sdk',
            ]
        
        for path in common_paths:
            if path.exists():
                spinner.stop()
                return (AuditResult("Android SDK", True, str(path)), path)
        
        spinner.stop()
        return (AuditResult(
            "Android SDK",
            False,
            "Not found",
            fix_suggestion="Set ANDROID_HOME environment variable or install Android SDK"
        ), None)
    
    def check_path_component(self, sdk_path: Path, component: str) -> AuditResult:
        """Check if SDK component is in PATH"""
        component_path = sdk_path / component
        
        if not component_path.exists():
            return AuditResult(
                f"PATH - {component}",
                False,
                "Component directory not found",
                fix_suggestion=f"Install missing SDK component: {component}"
            )
        
        path_env = os.environ.get('PATH', '')
        path_str = str(component_path)
        
        if path_str in path_env or str(component_path).lower() in path_env.lower():
            return AuditResult(f"PATH - {component}", True, "Found in PATH")
        
        return AuditResult(
            f"PATH - {component}",
            False,
            "Not in PATH",
            fix_suggestion=f"Add to PATH: {component_path}"
        )
    
    def check_emulator(self, sdk_path: Path) -> AuditResult:
        """Check if Pixel_4 emulator exists"""
        spinner = ProgressSpinner("Checking Pixel_4 Emulator")
        spinner.start()
        
        avdmanager = sdk_path / 'cmdline-tools' / 'latest' / 'bin' / 'avdmanager'
        if platform.system() == 'Windows':
            avdmanager = Path(str(avdmanager) + '.bat')
        
        if not avdmanager.exists():
            # Try alternative path
            avdmanager = sdk_path / 'tools' / 'bin' / 'avdmanager'
            if platform.system() == 'Windows':
                avdmanager = Path(str(avdmanager) + '.bat')
        
        if not avdmanager.exists():
            spinner.stop()
            return AuditResult(
                "Pixel_4 Emulator",
                False,
                "avdmanager not found",
                fix_suggestion="Install Android SDK Command-line Tools"
            )
        
        success, stdout, stderr = self.run_command([str(avdmanager), 'list', 'avd'])
        spinner.stop()
        
        if success and 'Pixel_4' in stdout:
            return AuditResult("Pixel_4 Emulator", True, "Device configured")
        
        return AuditResult(
            "Pixel_4 Emulator",
            False,
            "Not found",
            fix_suggestion="Create AVD: avdmanager create avd -n Pixel_4 -k \"system-images;android-30;google_apis;x86\""
        )
    
    def check_gradle(self, sdk_path: Path) -> AuditResult:
        """Check Gradle version"""
        spinner = ProgressSpinner("Checking Gradle")
        spinner.start()
        
        success, stdout, stderr = self.run_command(['gradle', '--version'])
        spinner.stop()
        
        if not success:
            return AuditResult(
                "Gradle 8.13+",
                False,
                "Not installed or not in PATH",
                warning=True,
                fix_suggestion="Install Gradle 8.13+ or add to PATH"
            )
        
        version_match = re.search(r'Gradle (\d+\.\d+)', stdout)
        if version_match:
            version = version_match.group(1)
            version_num = float(version)
            
            if version_num >= 8.13:
                return AuditResult("Gradle 8.13+", True, f"Version {version}")
            else:
                return AuditResult(
                    "Gradle 8.13+",
                    False,
                    f"Version {version} is below minimum (8.13)",
                    fix_suggestion="Update Gradle to version 8.13 or higher"
                )
        
        return AuditResult("Gradle 8.13+", False, "Version could not be determined", warning=True)
    
    def check_sdk_version_config(self) -> AuditResult:
        """Check SDK version configuration requirements"""
        # This is informational since we can't check without a project
        return AuditResult(
            "SDK Version Config",
            True,
            "Min SDK: 24, Max SDK: 35",
            warning=True,
            fix_suggestion="Ensure build.gradle has minSdkVersion 24 and targetSdkVersion 35"
        )
    
    def check_nodejs(self) -> AuditResult:
        """Check Node.js installation"""
        spinner = ProgressSpinner("Checking Node.js")
        spinner.start()
        
        success, stdout, stderr = self.run_command(['node', '--version'])
        spinner.stop()
        
        if not success:
            return AuditResult(
                "Node.js",
                False,
                "Not installed",
                fix_suggestion="Download and install Node.js from https://nodejs.org/"
            )
        
        version = stdout.strip()
        return AuditResult("Node.js", True, version)
    
    def check_python(self) -> AuditResult:
        """Check Python 3.x installation"""
        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        if sys.version_info.major >= 3:
            return AuditResult("Python 3.x", True, f"Version {version}")
        
        return AuditResult(
            "Python 3.x",
            False,
            f"Found Python {version}",
            fix_suggestion="Install Python 3.x from https://www.python.org/"
        )
    
    def run_audit(self) -> List[AuditResult]:
        """Run all audit checks"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}SmartChat System Audit v1.0{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}\n")
        
        # Java check
        self.results.append(self.check_java())
        
        # Cordova check
        self.results.append(self.check_cordova())
        
        # Android Studio check
        self.results.append(self.check_android_studio())
        
        # Android SDK check
        sdk_result, sdk_path = self.check_android_sdk()
        self.results.append(sdk_result)
        
        # PATH and emulator checks (only if SDK found)
        if sdk_path:
            path_components = [
                'emulator',
                'platform-tools',
                'tools',
                'tools/bin',
                'cmdline-tools/latest/bin'
            ]
            
            for component in path_components:
                self.results.append(self.check_path_component(sdk_path, component))
            
            self.results.append(self.check_emulator(sdk_path))
            self.results.append(self.check_gradle(sdk_path))
        else:
            # Mark PATH checks as failed if no SDK
            for component in ['emulator', 'platform-tools', 'tools', 'tools/bin', 'cmdline-tools/latest/bin']:
                self.results.append(AuditResult(
                    f"PATH - {component}",
                    False,
                    "SDK not found"
                ))
        
        # SDK version config info
        self.results.append(self.check_sdk_version_config())
        
        # Node.js check
        self.results.append(self.check_nodejs())
        
        # Python check
        self.results.append(self.check_python())
        
        return self.results
    
    def print_results(self):
        """Print formatted audit results"""
        print(f"\n{Colors.BOLD}AUDIT RESULTS{Colors.RESET}")
        print(f"{Colors.CYAN}{'-' * 80}{Colors.RESET}")
        print(f"{Colors.BOLD}{'REQUIREMENT':<30} {'STATUS':<15} {'DETAILS':<35}{Colors.RESET}")
        print(f"{Colors.CYAN}{'-' * 80}{Colors.RESET}")
        
        for result in self.results:
            status = result.status_symbol()
            details = result.details[:35] + '...' if len(result.details) > 35 else result.details
            print(f"{result.name:<30} {status:<20} {details:<35}")
        
        print(f"{Colors.CYAN}{'-' * 80}{Colors.RESET}")
        
        # Summary
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        warnings = sum(1 for r in self.results if r.warning)
        
        elapsed_time = time.time() - self.start_time
        
        summary_color = Colors.GREEN if passed == total else Colors.YELLOW if passed > total / 2 else Colors.RED
        print(f"\n{Colors.BOLD}SUMMARY:{Colors.RESET} {summary_color}{passed}/{total} checks passed{Colors.RESET}")
        if warnings > 0:
            print(f"{Colors.YELLOW}Warnings: {warnings}{Colors.RESET}")
        print(f"{Colors.BLUE}Execution time: {elapsed_time:.2f} seconds{Colors.RESET}")
    
    def generate_report(self, filename: str = "system_audit_report.txt"):
        """Generate detailed audit report file"""
        spinner = ProgressSpinner("Generating report")
        spinner.start()
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("SmartChat System Audit v1.0 - Detailed Report\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Audit Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("SYSTEM INFORMATION:\n")
                f.write("-" * 80 + "\n")
                f.write(f"Operating System: {self.system_info['os']} {self.system_info['os_version']}\n")
                f.write(f"Architecture: {self.system_info['architecture']}\n")
                f.write(f"Python Version: {self.system_info['python_version']}\n\n")
                
                f.write("AUDIT RESULTS:\n")
                f.write("-" * 80 + "\n\n")
                
                for result in self.results:
                    status = "PASS" if result.passed else "WARNING" if result.warning else "FAIL"
                    f.write(f"Requirement: {result.name}\n")
                    f.write(f"Status: {status}\n")
                    f.write(f"Details: {result.details}\n")
                    
                    if result.fix_suggestion:
                        f.write(f"Fix Suggestion: {result.fix_suggestion}\n")
                    
                    f.write("\n")
                
                f.write("=" * 80 + "\n")
                f.write("ENVIRONMENT VARIABLES:\n")
                f.write("-" * 80 + "\n")
                relevant_vars = ['ANDROID_HOME', 'ANDROID_SDK_ROOT', 'JAVA_HOME', 'PATH']
                for var in relevant_vars:
                    value = os.environ.get(var, 'Not set')
                    f.write(f"{var}: {value}\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("SUMMARY:\n")
                f.write("-" * 80 + "\n")
                passed = sum(1 for r in self.results if r.passed)
                total = len(self.results)
                f.write(f"Checks Passed: {passed}/{total}\n")
                f.write(f"Warnings: {sum(1 for r in self.results if r.warning)}\n")
                f.write(f"Execution Time: {time.time() - self.start_time:.2f} seconds\n")
            
            spinner.stop()
            print(f"\n{Colors.GREEN}✓{Colors.RESET} Report saved to: {Colors.BOLD}{filename}{Colors.RESET}")
            
        except Exception as e:
            spinner.stop()
            print(f"\n{Colors.RED}✗{Colors.RESET} Failed to generate report: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='SmartChat System Audit v1.0 - Mobile Development Environment Checker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    Run standard audit
  %(prog)s --verbose          Run with detailed debug output
  %(prog)s --output report.txt  Save report to custom filename
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose debug output'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='system_audit_report.txt',
        help='Output report filename (default: system_audit_report.txt)'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    args = parser.parse_args()
    
    if args.no_color:
        Colors.disable()
    
    try:
        auditor = SystemAuditor(verbose=args.verbose)
        auditor.run_audit()
        auditor.print_results()
        auditor.generate_report(args.output)
        
        # Exit with appropriate code
        passed = sum(1 for r in auditor.results if r.passed)
        total = len(auditor.results)
        
        if passed == total:
            print(f"\n{Colors.GREEN}✓ All checks passed! Your environment is ready.{Colors.RESET}\n")
            sys.exit(0)
        else:
            print(f"\n{Colors.YELLOW}⚠ Some checks failed. Review the report for details.{Colors.RESET}\n")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Audit interrupted by user.{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
