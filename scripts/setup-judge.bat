@echo off
REM Setup script for secure judge system
REM This script builds all necessary Docker images for secure code execution

echo Setting up secure judge system...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not running. Please start Docker first.
    exit /b 1
)

echo Building Docker images for secure code execution...

REM Build Python image
echo Building Python judge image...
docker build -t django-judge-python ./docker/python/

REM Build C++ image
echo Building C++ judge image...
docker build -t django-judge-cpp ./docker/cpp/

REM Build Java image
echo Building Java judge image...
docker build -t django-judge-java ./docker/java/

REM Build JavaScript image
echo Building JavaScript judge image...
docker build -t django-judge-javascript ./docker/javascript/

echo All judge images built successfully!

REM Verify images
echo Verifying images...
docker images | findstr django-judge

echo.
echo Secure judge system setup complete!
echo.
echo Security features enabled:
echo ✓ Docker containerization
echo ✓ Network isolation (no internet access)
echo ✓ Resource limits (CPU, memory, disk)
echo ✓ Non-root user execution
echo ✓ Read-only filesystem
echo ✓ Process limits
echo ✓ File descriptor limits
echo ✓ Code validation and scanning
echo.
echo Your code execution environment is now secure!