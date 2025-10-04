"""
Test framework for Memory Bank CLI
"""

from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from datetime import datetime
import json
from pathlib import Path


class TestStatus(Enum):
    """Test execution status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestResult:
    """Test execution result"""
    
    def __init__(self, test_name: str, status: TestStatus, 
                 message: str = "", duration: float = 0.0,
                 details: Dict[str, Any] = None):
        self.test_name = test_name
        self.status = status
        self.message = message
        self.duration = duration
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()


class TestCase:
    """Individual test case"""
    
    def __init__(self, name: str, description: str = "", 
                 test_function: Callable = None, 
                 setup: Callable = None, 
                 teardown: Callable = None,
                 timeout: float = 30.0):
        self.name = name
        self.description = description
        self.test_function = test_function
        self.setup = setup
        self.teardown = teardown
        self.timeout = timeout
        self.result: Optional[TestResult] = None
    
    def execute(self) -> TestResult:
        """Execute the test case"""
        start_time = datetime.now()
        
        try:
            # Setup
            if self.setup:
                self.setup()
            
            # Execute test
            if self.test_function:
                self.test_function()
                status = TestStatus.PASSED
                message = "Test passed"
            else:
                status = TestStatus.SKIPPED
                message = "No test function provided"
            
            # Teardown
            if self.teardown:
                self.teardown()
                
        except AssertionError as e:
            status = TestStatus.FAILED
            message = str(e)
        except Exception as e:
            status = TestStatus.ERROR
            message = f"Test error: {str(e)}"
        finally:
            # Ensure teardown runs even on error
            if self.teardown:
                try:
                    self.teardown()
                except Exception:
                    pass
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.result = TestResult(
            test_name=self.name,
            status=status,
            message=message,
            duration=duration
        )
        
        return self.result


class TestSuite:
    """Collection of related test cases"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.test_cases: List[TestCase] = []
        self.results: List[TestResult] = []
    
    def add_test_case(self, test_case: TestCase):
        """Add test case to suite"""
        self.test_cases.append(test_case)
    
    def add_test(self, name: str, test_function: Callable, **kwargs):
        """Add test case with function"""
        test_case = TestCase(name, test_function=test_function, **kwargs)
        self.add_test_case(test_case)
    
    def execute(self) -> List[TestResult]:
        """Execute all test cases in suite"""
        self.results = []
        
        for test_case in self.test_cases:
            result = test_case.execute()
            self.results.append(result)
        
        return self.results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test suite summary"""
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
        errors = sum(1 for r in self.results if r.status == TestStatus.ERROR)
        
        return {
            'suite_name': self.name,
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'errors': errors,
            'success_rate': (passed / total_tests * 100) if total_tests > 0 else 0,
            'total_duration': sum(r.duration for r in self.results)
        }


class TestFramework:
    """Main test framework"""
    
    def __init__(self, test_directory: str = "tests"):
        self.test_directory = Path(test_directory)
        self.test_suites: List[TestSuite] = []
        self.results: List[TestResult] = []
    
    def create_suite(self, name: str, description: str = "") -> TestSuite:
        """Create new test suite"""
        suite = TestSuite(name, description)
        self.test_suites.append(suite)
        return suite
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        all_results = []
        suite_summaries = []
        
        for suite in self.test_suites:
            suite_results = suite.execute()
            all_results.extend(suite_results)
            suite_summaries.append(suite.get_summary())
        
        self.results = all_results
        
        # Calculate overall summary
        total_tests = len(all_results)
        passed = sum(1 for r in all_results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in all_results if r.status == TestStatus.FAILED)
        skipped = sum(1 for r in all_results if r.status == TestStatus.SKIPPED)
        errors = sum(1 for r in all_results if r.status == TestStatus.ERROR)
        
        summary = {
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'errors': errors,
            'success_rate': (passed / total_tests * 100) if total_tests > 0 else 0,
            'total_duration': sum(r.duration for r in all_results),
            'suite_summaries': suite_summaries,
            'timestamp': datetime.now().isoformat()
        }
        
        return summary
    
    def generate_report(self, output_file: str = "test_report.json") -> str:
        """Generate test report"""
        summary = self.run_all_tests()
        
        report = {
            'summary': summary,
            'test_results': [
                {
                    'test_name': r.test_name,
                    'status': r.status.value,
                    'message': r.message,
                    'duration': r.duration,
                    'timestamp': r.timestamp,
                    'details': r.details
                }
                for r in self.results
            ]
        }
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        return str(output_path)
    
    def create_cli_tests(self) -> TestSuite:
        """Create test suite for CLI functionality"""
        suite = self.create_suite("CLI Tests", "Tests for CLI command functionality")
        
        # Test CLI help
        def test_cli_help():
            import subprocess
            result = subprocess.run(['python', 'memory-bank-cli.py', '--help'], 
                                  capture_output=True, text=True)
            assert result.returncode == 0, "CLI help command failed"
            assert "Memory Bank CLI" in result.stdout, "CLI help output missing expected content"
        
        suite.add_test("cli_help", test_cli_help)
        
        # Test status command
        def test_status_command():
            import subprocess
            result = subprocess.run(['python', 'memory-bank-cli.py', 'status'], 
                                  capture_output=True, text=True)
            assert result.returncode == 0, "Status command failed"
        
        suite.add_test("status_command", test_status_command)
        
        # Test spec preview
        def test_spec_preview():
            import subprocess
            result = subprocess.run(['python', 'memory-bank-cli.py', 'spec', 'preview', '--level', '1'], 
                                  capture_output=True, text=True)
            assert result.returncode == 0, "Spec preview command failed"
        
        suite.add_test("spec_preview", test_spec_preview)
        
        return suite
    
    def create_template_tests(self) -> TestSuite:
        """Create test suite for template system"""
        suite = self.create_suite("Template Tests", "Tests for template system functionality")
        
        # Test template generation
        def test_template_generation():
            from ..templates.engine.template_engine import TemplateEngine
            engine = TemplateEngine()
            
            # Test Level 1 template
            template = engine.generate_template(1, {
                'title': 'Test Feature',
                'description': 'Test description'
            })
            
            assert template is not None, "Template generation failed"
            assert 'title' in template, "Template missing title field"
        
        suite.add_test("template_generation", test_template_generation)
        
        # Test template validation
        def test_template_validation():
            from ..templates.engine.template_engine import TemplateEngine
            engine = TemplateEngine()
            
            # Test valid template
            valid_data = {
                'title': 'Test Feature',
                'description': 'This is a comprehensive test description that meets minimum length requirements'
            }
            
            result = engine.validate_template(valid_data)
            assert result.is_valid, "Valid template should pass validation"
        
        suite.add_test("template_validation", test_template_validation)
        
        return suite
    
    def create_workflow_tests(self) -> TestSuite:
        """Create test suite for workflow system"""
        suite = self.create_suite("Workflow Tests", "Tests for workflow and transition functionality")
        
        # Test mode manager
        def test_mode_manager():
            from ..workflow.mode_manager import ModeManager
            from ..config import CLIConfig
            from ..memory_bank import MemoryBank
            
            config = CLIConfig.default()
            memory_bank = MemoryBank()
            mode_manager = ModeManager(config, memory_bank)
            
            # Test transition validation
            result = mode_manager.can_transition('van', 'plan')
            assert 'is_valid' in result, "Mode manager should return validation result"
        
        suite.add_test("mode_manager", test_mode_manager)
        
        return suite
