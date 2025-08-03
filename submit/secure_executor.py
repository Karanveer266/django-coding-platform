"""
Secure code execution system using Docker containers
Implements proper sandboxing, resource limits, and security measures
"""
import docker
import tempfile
import os
import time
import threading
import tarfile
import io
from typing import Tuple, Optional, Dict
import logging
from .config import JudgeConfig

logger = logging.getLogger(__name__)

class SecureExecutor:
    """Secure code executor using Docker containers"""
    
    def __init__(self):
        self.config = JudgeConfig()
        try:
            self.docker_client = docker.from_env()
            # Test Docker connection
            self.docker_client.ping()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise Exception("Docker is required for secure code execution")
        
        # Language to Docker image mapping
        self.language_images = {
            'python': 'django-judge-python',
            'py': 'django-judge-python',
            'cpp': 'django-judge-cpp',
            'c': 'django-judge-cpp',
            'java': 'django-judge-java',
            'javascript': 'django-judge-javascript'
        }
        
        # Build images if they don't exist
        self._ensure_images_exist()
    
    def _ensure_images_exist(self):
        """Build Docker images if they don't exist"""
        try:
            for lang, image_name in self.language_images.items():
                if lang in ['py', 'c']:  # Skip duplicates
                    continue
                    
                try:
                    self.docker_client.images.get(image_name)
                    logger.info(f"Image {image_name} already exists")
                except docker.errors.ImageNotFound:
                    logger.info(f"Building image {image_name}")
                    dockerfile_path = os.path.join(os.path.dirname(__file__), '..', 'docker', lang)
                    if os.path.exists(dockerfile_path):
                        self.docker_client.images.build(
                            path=dockerfile_path,
                            tag=image_name,
                            rm=True
                        )
                        logger.info(f"Successfully built image {image_name}")
                    else:
                        logger.warning(f"Dockerfile not found for {lang} at {dockerfile_path}")
        except Exception as e:
            logger.error(f"Error ensuring images exist: {e}")
    
    def _create_file_archive(self, filename: str, content: str) -> bytes:
        """Create a tar archive containing the code file"""
        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
            file_data = content.encode('utf-8')
            tarinfo = tarfile.TarInfo(name=filename)
            tarinfo.size = len(file_data)
            tarinfo.mode = 0o644
            tar.addfile(tarinfo, io.BytesIO(file_data))
        
        tar_buffer.seek(0)
        return tar_buffer.getvalue()
    
    def _get_language_config(self, language: str) -> Dict:
        """Get language-specific execution configuration"""
        configs = {
            'python': {
                'filename': 'solution.py',
                'compile_cmd': None,
                'run_cmd': ['python3', 'solution.py']
            },
            'py': {
                'filename': 'solution.py',
                'compile_cmd': None,
                'run_cmd': ['python3', 'solution.py']
            },
            'cpp': {
                'filename': 'solution.cpp',
                'compile_cmd': ['g++', '-o', 'solution', 'solution.cpp', '-std=c++17', '-O2'],
                'run_cmd': ['./solution']
            },
            'c': {
                'filename': 'solution.c',
                'compile_cmd': ['gcc', '-o', 'solution', 'solution.c', '-std=c99', '-O2'],
                'run_cmd': ['./solution']
            },
            'java': {
                'filename': 'Solution.java',
                'compile_cmd': ['javac', 'Solution.java'],
                'run_cmd': ['java', 'Solution']
            },
            'javascript': {
                'filename': 'solution.js',
                'compile_cmd': None,
                'run_cmd': ['node', 'solution.js']
            }
        }
        return configs.get(language.lower(), {})
    
    def execute_code(self, code: str, language: str, input_data: str, timeout: int = None) -> Tuple[str, str, float, bool]:
        """Execute code securely in a Docker container"""
        language = language.lower()
        
        if language not in self.language_images:
            return "", f"Language '{language}' not supported", 0, False
        
        image_name = self.language_images[language]
        lang_config = self._get_language_config(language)
        
        if not lang_config:
            return "", f"Configuration not found for language '{language}'", 0, False
        
        # Handle Java class name extraction
        if language == 'java':
            import re
            class_match = re.search(r'public\s+class\s+(\w+)', code)
            if class_match:
                class_name = class_match.group(1)
                # Update code to use the extracted class name
                code = code.replace(f'public class {class_match.group(1)}', 'public class Solution')
                lang_config['run_cmd'] = ['java', 'Solution']
        
        container = None
        start_time = time.time()
        
        try:
            # Get timeout from config
            current_timeout = timeout or self.config.get_time_limit(language)
            memory_limit = self.config.get_memory_limit(language)
            
            # Create file archive
            filename = lang_config['filename']
            file_archive = self._create_file_archive(filename, code)
            
            # Security settings for container
            security_opt = [
                'no-new-privileges:true',  # Prevent privilege escalation
                'seccomp:unconfined'       # Allow necessary system calls for compilation
            ]
            
            # Create and start container with strict resource limits
            container = self.docker_client.containers.create(
                image=image_name,
                command=['sleep', '300'],  # Keep container alive
                detach=True,
                mem_limit=memory_limit,
                memswap_limit=memory_limit,  # Prevent swap usage
                cpu_quota=50000,  # 50% CPU limit
                cpu_period=100000,
                network_mode='none',  # No network access
                security_opt=security_opt,
                user='sandbox',  # Run as non-root user
                working_dir='/sandbox',
                read_only=True,  # Read-only filesystem
                tmpfs={'/tmp': 'size=10m,noexec'},  # Small temp space, no execution
                pids_limit=50,  # Limit number of processes
                ulimits=[
                    docker.types.Ulimit(name='nproc', soft=10, hard=10),  # Process limit
                    docker.types.Ulimit(name='nofile', soft=64, hard=64),  # File descriptor limit
                    docker.types.Ulimit(name='fsize', soft=10485760, hard=10485760)  # 10MB file size limit
                ]
            )
            
            container.start()
            
            # Copy code file to container
            container.put_archive('/sandbox', file_archive)
            
            # Compilation step (if needed)
            if lang_config['compile_cmd']:
                compile_result = container.exec_run(
                    cmd=lang_config['compile_cmd'],
                    workdir='/sandbox',
                    user='sandbox',
                    demux=True
                )
                
                if compile_result.exit_code != 0:
                    stderr = compile_result.output[1].decode('utf-8') if compile_result.output[1] else ""
                    return "", f"Compilation Error: {stderr}", 0, False
            
            # Execution step with timeout
            exec_start_time = time.time()
            
            # Create execution thread to handle timeout
            result = {'stdout': '', 'stderr': '', 'exit_code': -1, 'timed_out': False}
            
            def execute():
                try:
                    exec_result = container.exec_run(
                        cmd=lang_config['run_cmd'],
                        stdin=True,
                        stdout=True,
                        stderr=True,
                        workdir='/sandbox',
                        user='sandbox',
                        demux=True
                    )
                    
                    # Send input data
                    if input_data:
                        exec_result.output.send(input_data.encode('utf-8'))
                    
                    stdout = exec_result.output[0].decode('utf-8') if exec_result.output[0] else ""
                    stderr = exec_result.output[1].decode('utf-8') if exec_result.output[1] else ""
                    
                    result['stdout'] = stdout
                    result['stderr'] = stderr
                    result['exit_code'] = exec_result.exit_code
                except Exception as e:
                    result['stderr'] = str(e)
                    result['exit_code'] = -1
            
            exec_thread = threading.Thread(target=execute)
            exec_thread.daemon = True
            exec_thread.start()
            exec_thread.join(timeout=current_timeout)
            
            execution_time = time.time() - exec_start_time
            
            if exec_thread.is_alive():
                # Timeout occurred
                result['timed_out'] = True
                return "", "Time Limit Exceeded", current_timeout, False
            
            # Check execution result
            if result['exit_code'] == 0:
                return result['stdout'].strip(), result['stderr'].strip(), execution_time, True
            else:
                return result['stdout'].strip(), result['stderr'].strip(), execution_time, False
                
        except docker.errors.APIError as e:
            logger.error(f"Docker API error: {e}")
            return "", f"Container execution error: {str(e)}", 0, False
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return "", str(e), 0, False
        finally:
            # Clean up container
            if container:
                try:
                    container.kill()
                    container.remove()
                except:
                    pass
    
    def check_docker_status(self) -> Dict[str, bool]:
        """Check if Docker and required images are available"""
        status = {'docker_available': False, 'images': {}}
        
        try:
            self.docker_client.ping()
            status['docker_available'] = True
            
            for lang, image_name in self.language_images.items():
                if lang in ['py', 'c']:  # Skip duplicates
                    continue
                try:
                    self.docker_client.images.get(image_name)
                    status['images'][lang] = True
                except docker.errors.ImageNotFound:
                    status['images'][lang] = False
        except:
            pass
        
        return status