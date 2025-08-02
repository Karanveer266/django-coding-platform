import subprocess
import tempfile
import os
import time
import signal
import shutil
from typing import Tuple, Optional, Dict
import logging
from .config import JudgeConfig

logger = logging.getLogger(__name__)

class CodeJudge:
    """Enhanced code judge supporting multiple languages with dynamic configuration"""
    
    def __init__(self):
        # These will be set dynamically per submission
        self.config = JudgeConfig()
        
        # Language configurations
        self.language_configs = {
            'python': {
                'extension': '.py',
                'compile_cmd': None,  # Python doesn't need compilation
                'execute_cmd': ['python3', '{file}'],
                'docker_image': None  # For future Docker support
            },
            'py': {
                'extension': '.py',
                'compile_cmd': None,
                'execute_cmd': ['python3', '{file}'],
                'docker_image': None
            },
            'cpp': {
                'extension': '.cpp',
                'compile_cmd': ['g++', '-o', '{output}', '{file}', '-std=c++17', '-O2'],
                'execute_cmd': ['{output}'],
                'docker_image': None
            },
            'c': {
                'extension': '.c',
                'compile_cmd': ['gcc', '-o', '{output}', '{file}', '-std=c99', '-O2'],
                'execute_cmd': ['{output}'],
                'docker_image': None
            },
            'java': {
                'extension': '.java',
                'compile_cmd': ['javac', '{file}'],
                'execute_cmd': ['java', '-cp', '{dir}', '{class}'],
                'docker_image': None
            },
            'javascript': {
                'extension': '.js',
                'compile_cmd': None,
                'execute_cmd': ['node', '{file}'],
                'docker_image': None
            }
        }
        
    def check_system_requirements(self) -> Dict[str, bool]:
        """Check if required compilers/interpreters are available"""
        requirements = {}
        
        # Check Python
        requirements['python'] = shutil.which('python3') is not None or shutil.which('python') is not None
        
        # Check C++
        requirements['cpp'] = shutil.which('g++') is not None
        
        # Check C
        requirements['c'] = shutil.which('gcc') is not None
        
        # Check Java
        requirements['java'] = shutil.which('javac') is not None and shutil.which('java') is not None
        
        # Check Node.js
        requirements['javascript'] = shutil.which('node') is not None
        
        return requirements
        
    def execute_python(self, code: str, input_data: str, timeout: int = None) -> Tuple[str, str, float, bool]:
        """Execute Python code with input and return output, error, time, success"""
        try:
            start_time = time.time()
            current_timeout = timeout or self.config.get_time_limit('python')
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.flush()
                temp_file = f.name
            
            try:
                # Use python3 if available, otherwise python
                python_cmd = 'python3' if shutil.which('python3') else 'python'
                
                # Run the code
                process = subprocess.Popen(
                    [python_cmd, temp_file],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate(input=input_data, timeout=current_timeout)
                execution_time = time.time() - start_time
                
                return stdout.strip(), stderr.strip(), execution_time, process.returncode == 0
                
            except subprocess.TimeoutExpired:
                process.kill()
                return "", "Time Limit Exceeded", current_timeout, False
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    
        except Exception as e:
            logger.error(f"Python execution error: {str(e)}")
            return "", str(e), 0, False
            
    def execute_cpp(self, code: str, input_data: str, timeout: int = None) -> Tuple[str, str, float, bool]:
        """Execute C++ code with compilation and execution"""
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
                f.write(code)
                f.flush()
                source_file = f.name
                
            executable_file = source_file.replace('.cpp', '')
            
            try:
                # Compile
                compile_start = time.time()
                # Compile
                compile_process = subprocess.Popen(
                    ['g++', '-o', executable_file, source_file, '-std=c++17', '-O2'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                    # Remove the timeout parameter from here
                )
                
                # The timeout should only be used with communicate()
                compile_timeout = self.config.get_compile_timeout('cpp')
                compile_stdout, compile_stderr = compile_process.communicate(timeout=compile_timeout)
                
                if compile_process.returncode != 0:
                    return "", f"Compilation Error: {compile_stderr}", 0, False
                
                # Execute
                start_time = time.time()
                current_timeout = timeout or self.config.get_time_limit('cpp')
                process = subprocess.Popen(
                    [executable_file],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate(input=input_data, timeout=current_timeout)
                execution_time = time.time() - start_time
                
                return stdout.strip(), stderr.strip(), execution_time, process.returncode == 0
                
            except subprocess.TimeoutExpired:
                try:
                    process.kill()
                except:
                    pass
                return "", "Time Limit Exceeded", current_timeout, False
                
            finally:
                # Clean up files
                for file_path in [source_file, executable_file]:
                    if os.path.exists(file_path):
                        try:
                            os.unlink(file_path)
                        except:
                            pass
                            
        except Exception as e:
            logger.error(f"C++ execution error: {str(e)}")
            return "", str(e), 0, False
            
    def execute_java(self, code: str, input_data: str, timeout: int = None) -> Tuple[str, str, float, bool]:
        """Execute Java code with compilation and execution"""
        try:
            # Extract class name from code
            import re
            class_match = re.search(r'public\s+class\s+(\w+)', code)
            if not class_match:
                return "", "No public class found in Java code", 0, False
                
            class_name = class_match.group(1)
            
            # Create temporary directory and file
            temp_dir = tempfile.mkdtemp()
            source_file = os.path.join(temp_dir, f"{class_name}.java")
            
            try:
                with open(source_file, 'w') as f:
                    f.write(code)
                
                # Compile
                # Compile
                compile_process = subprocess.Popen(
                    ['javac', source_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                    # Remove the timeout parameter from here
                )
                
                # The timeout should only be used with communicate()
                compile_timeout = self.config.get_compile_timeout('java')
                compile_stdout, compile_stderr = compile_process.communicate(timeout=compile_timeout)
                
                if compile_process.returncode != 0:
                    return "", f"Compilation Error: {compile_stderr}", 0, False
                
                # Execute
                start_time = time.time()
                current_timeout = timeout or self.config.get_time_limit('java')
                process = subprocess.Popen(
                    ['java', '-cp', temp_dir, class_name],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate(input=input_data, timeout=current_timeout)
                execution_time = time.time() - start_time
                
                return stdout.strip(), stderr.strip(), execution_time, process.returncode == 0
                
            except subprocess.TimeoutExpired:
                try:
                    process.kill()
                except:
                    pass
                return "", "Time Limit Exceeded", current_timeout, False
                
            finally:
                # Clean up directory
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Java execution error: {str(e)}")
            return "", str(e), 0, False
            
    def execute_code(self, code: str, language: str, input_data: str, timeout: int = None) -> Tuple[str, str, float, bool]:
        """Execute code in the specified language"""
        language = language.lower()
        
        if language in ['python', 'py']:
            return self.execute_python(code, input_data, timeout)
        elif language in ['cpp', 'c++']:
            return self.execute_cpp(code, input_data, timeout)
        elif language == 'java':
            return self.execute_java(code, input_data, timeout)
        else:
            return "", f"Language '{language}' not supported", 0, False
    
    def judge_submission(self, code: str, language: str, test_cases: list, problem=None) -> dict:
        """Judge a submission against test cases with dynamic configuration"""
        results = {
            'status': 'ACCEPTED',
            'passed_tests': 0,
            'total_tests': len(test_cases),
            'max_time': 0,
            'test_results': [],
            'compilation_error': None
        }
        
        # Get dynamic timeout from problem or language defaults
        timeout = None
        if problem:
            timeout = problem.time_limit
        if not timeout:
            timeout = self.config.get_time_limit(language)
            
        for test_case in test_cases:
            input_data = test_case.input_data
            expected_output = test_case.expected_output.strip()
            
            # Use the enhanced execute_code method that supports multiple languages
            output, error, exec_time, success = self.execute_code(code, language, input_data, timeout)
            
            results['max_time'] = max(results['max_time'], exec_time)
            
            # Determine test result
            if not success:
                if "Time Limit Exceeded" in error:
                    test_status = 'TIME_LIMIT_EXCEEDED'
                elif "Compilation Error" in error:
                    test_status = 'COMPILATION_ERROR'
                    results['compilation_error'] = error  # Store exact compilation error
                elif error:
                    test_status = 'RUNTIME_ERROR'
                else:
                    test_status = 'ERROR'
            elif output.strip() == expected_output:
                test_status = 'ACCEPTED'
                results['passed_tests'] += 1
            else:
                test_status = 'WRONG_ANSWER'
            
            results['test_results'].append({
                'test_case_id': test_case.id,
                'status': test_status,
                'execution_time': exec_time,
                'actual_output': output,
                'expected_output': expected_output,
                'error': error
            })
            
            # If any test fails, overall status changes
            if test_status != 'ACCEPTED' and results['status'] == 'ACCEPTED':
                results['status'] = test_status
                
            # For compilation errors, stop testing other cases
            if test_status == 'COMPILATION_ERROR':
                break
        
        return results

# Global instance with error handling
try:
    judge = CodeJudge()
except Exception as e:
    logger.error(f"Failed to initialize judge: {e}")
    judge = None