#!/usr/bin/env python3
"""
Test script to verify the admin panel fix for UsersModel
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/opt/vpn-service/services')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import UsersModel
from accounts.admin import CustomUserAdmin

def test_admin_configuration():
    """Test that the admin configuration is working correctly"""
    print("🔍 Testing admin configuration...")
    
    try:
        # Test that the admin is registered
        admin_site = admin.site
        model_admin = admin_site._registry.get(UsersModel)
        
        if model_admin is None:
            print("❌ UsersModel is not registered in admin")
            return False
        
        print("✅ UsersModel is registered in admin")
        
        # Test that readonly_fields are set correctly
        readonly_fields = getattr(model_admin, 'readonly_fields', ())
        if 'created_at' in readonly_fields and 'updated_at' in readonly_fields:
            print("✅ readonly_fields are set correctly")
        else:
            print("❌ readonly_fields are not set correctly")
            print(f"Current readonly_fields: {readonly_fields}")
            return False
        
        # Test that fieldsets are configured correctly
        fieldsets = getattr(model_admin, 'fieldsets', ())
        if fieldsets:
            print("✅ fieldsets are configured")
            
            # Check if created_at and updated_at are in the Important dates section
            for section_name, section_data in fieldsets:
                if section_name == 'Important dates':
                    fields = section_data.get('fields', ())
                    if 'created_at' in fields and 'updated_at' in fields:
                        print("✅ created_at and updated_at are in Important dates section")
                    else:
                        print("❌ created_at and updated_at are not in Important dates section")
                        return False
                    break
            else:
                print("❌ Important dates section not found in fieldsets")
                return False
        else:
            print("❌ fieldsets are not configured")
            return False
        
        print("🎉 All admin configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing admin configuration: {e}")
        return False

def test_model_fields():
    """Test that the model fields are configured correctly"""
    print("\n🔍 Testing model fields...")
    
    try:
        # Get the model fields
        fields = UsersModel._meta.get_fields()
        
        # Check created_at field
        created_at_field = UsersModel._meta.get_field('created_at')
        if created_at_field.auto_now_add:
            print("✅ created_at field has auto_now_add=True")
        else:
            print("❌ created_at field does not have auto_now_add=True")
            return False
        
        # Check updated_at field
        updated_at_field = UsersModel._meta.get_field('updated_at')
        if updated_at_field.auto_now:
            print("✅ updated_at field has auto_now=True")
        else:
            print("❌ updated_at field does not have auto_now=True")
            return False
        
        print("🎉 All model field tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing model fields: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting admin panel fix verification...\n")
    
    admin_ok = test_admin_configuration()
    model_ok = test_model_fields()
    
    print(f"\n📊 Test Results:")
    print(f"Admin Configuration: {'✅ PASS' if admin_ok else '❌ FAIL'}")
    print(f"Model Fields: {'✅ PASS' if model_ok else '❌ FAIL'}")
    
    if admin_ok and model_ok:
        print("\n🎉 All tests passed! The FieldError should be fixed.")
        print("You can now access the admin panel without the FieldError.")
    else:
        print("\n❌ Some tests failed. Please check the configuration.") 