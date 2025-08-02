#!/usr/bin/env python3
"""
Deployment script for fixing the Django admin panel FieldError
"""

import os
import sys
import subprocess
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def check_service_status(service_name):
    """Check if a systemd service is running"""
    print(f"🔍 Checking {service_name} status...")
    result = subprocess.run(f"systemctl is-active {service_name}", shell=True, capture_output=True, text=True)
    return result.returncode == 0

def main():
    print("🚀 Starting admin panel fix deployment...\n")
    
    # Step 1: Navigate to the project directory
    project_dir = "/opt/vpn-service/services"
    if not os.path.exists(project_dir):
        print(f"❌ Project directory not found: {project_dir}")
        return False
    
    os.chdir(project_dir)
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Step 2: Check Django configuration
    print("\n🔍 Checking Django configuration...")
    if not run_command("python manage.py check", "Django configuration check"):
        print("❌ Django configuration has errors")
        return False
    
    # Step 3: Test the admin fix
    print("\n🧪 Testing admin panel fix...")
    if not run_command("python test_admin_fix.py", "Admin panel fix test"):
        print("❌ Admin panel fix test failed")
        return False
    
    # Step 4: Check if Django service is running
    django_service = "vpn-django"
    if check_service_status(django_service):
        print(f"✅ {django_service} is running")
        
        # Step 5: Restart Django service
        print(f"\n🔄 Restarting {django_service}...")
        if not run_command(f"systemctl restart {django_service}", f"Restart {django_service}"):
            print(f"❌ Failed to restart {django_service}")
            return False
        
        # Step 6: Wait a moment and check service status
        time.sleep(3)
        if check_service_status(django_service):
            print(f"✅ {django_service} is running after restart")
        else:
            print(f"❌ {django_service} is not running after restart")
            return False
    else:
        print(f"⚠️ {django_service} is not running, starting it...")
        if not run_command(f"systemctl start {django_service}", f"Start {django_service}"):
            print(f"❌ Failed to start {django_service}")
            return False
    
    # Step 7: Test admin panel access
    print("\n🌐 Testing admin panel access...")
    print("You can now test the admin panel by visiting:")
    print("http://YOUR-SERVER-IP:8000/admin/")
    print("The FieldError should be fixed!")
    
    print("\n🎉 Admin panel fix deployment completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Deployment failed!")
        sys.exit(1)
    else:
        print("\n✅ Deployment completed successfully!") 