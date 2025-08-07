#!/bin/bash

# اسکریپت نصب sudo
echo "🔧 نصب sudo..."

# بررسی نوع سیستم عامل
if command -v apt &> /dev/null; then
    echo "📦 سیستم مبتنی بر Debian/Ubuntu"
    apt update
    apt install -y sudo
elif command -v yum &> /dev/null; then
    echo "📦 سیستم مبتنی بر CentOS/RHEL"
    yum install -y sudo
elif command -v dnf &> /dev/null; then
    echo "📦 سیستم مبتنی بر Fedora"
    dnf install -y sudo
elif command -v apk &> /dev/null; then
    echo "📦 سیستم مبتنی بر Alpine"
    apk add sudo
else
    echo "❌ نوع سیستم عامل شناسایی نشد"
    exit 1
fi

echo "✅ sudo نصب شد"

# بررسی نصب
if command -v sudo &> /dev/null; then
    echo "✅ sudo با موفقیت نصب شد"
else
    echo "❌ خطا در نصب sudo"
fi
