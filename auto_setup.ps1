# اسکریپت نصب و راه‌اندازی خودکار سیستم VPN Bot برای Windows
# این اسکریپت تمام مراحل نصب و راه‌اندازی را به صورت خودکار انجام می‌دهد

$ErrorActionPreference = "Stop"

function Print-Message {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Print-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Print-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Print-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# بررسی Python
Print-Message "بررسی Python..."
try {
    $pythonVersion = python --version 2>&1
    Print-Success "Python پیدا شد: $pythonVersion"
} catch {
    Print-Error "Python نصب نیست! لطفا ابتدا Python را نصب کنید."
    exit 1
}

# بررسی pip
Print-Message "بررسی pip..."
try {
    $pipVersion = pip --version 2>&1
    Print-Success "pip پیدا شد: $pipVersion"
} catch {
    Print-Error "pip نصب نیست! لطفا ابتدا pip را نصب کنید."
    exit 1
}

# ایجاد محیط مجازی
Print-Message "ایجاد محیط مجازی..."
if (-not (Test-Path "venv")) {
    python -m venv venv
    Print-Success "محیط مجازی ایجاد شد"
} else {
    Print-Warning "محیط مجازی از قبل وجود دارد"
}

# فعال‌سازی محیط مجازی
Print-Message "فعال‌سازی محیط مجازی..."
& .\venv\Scripts\Activate.ps1
Print-Success "محیط مجازی فعال شد"

# به‌روزرسانی pip
Print-Message "به‌روزرسانی pip..."
python -m pip install --upgrade pip --quiet
Print-Success "pip به‌روزرسانی شد"

# نصب وابستگی‌ها
Print-Message "نصب وابستگی‌ها..."
pip install -r requirements.txt --quiet
Print-Success "وابستگی‌ها نصب شدند"

# ایجاد دایرکتوری‌های لازم
Print-Message "ایجاد دایرکتوری‌های لازم..."
@("static", "media", "logs", "backups") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}
Print-Success "دایرکتوری‌ها ایجاد شدند"

# اجرای migrations
Print-Message "اجرای migrations..."
python manage.py migrate --noinput
Print-Success "Migrations اجرا شدند"

# جمع‌آوری static files
Print-Message "جمع‌آوری static files..."
python manage.py collectstatic --noinput --clear
Print-Success "Static files جمع‌آوری شدند"

# بارگذاری داده‌های اولیه
Print-Message "بارگذاری داده‌های اولیه..."
python load_initial_data.py
Print-Success "داده‌های اولیه بارگذاری شدند"

# بررسی سیستم
Print-Message "بررسی سیستم..."
python manage.py check
Print-Success "بررسی سیستم بدون خطا انجام شد"

Write-Host ""
Write-Host "=" * 60
Print-Success "✅ نصب و راه‌اندازی با موفقیت انجام شد!"
Write-Host "=" * 60
Write-Host ""
Write-Host "📋 اطلاعات ورود به پنل ادمین:"
Write-Host "   URL: http://localhost:8000/admin/"
Write-Host "   Username: admin"
$adminPassword = (Get-Content config.env | Select-String "ADMIN_PASSWORD=").ToString().Split('=')[1]
Write-Host "   Password: $adminPassword"
Write-Host ""
Write-Host "🚀 برای اجرای سرور:"
Write-Host "   .\venv\Scripts\Activate.ps1"
Write-Host "   python manage.py runserver 0.0.0.0:8000"
Write-Host ""

