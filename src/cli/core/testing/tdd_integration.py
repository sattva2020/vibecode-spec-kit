"""
TDD Integration for Memory Bank CLI
"""

from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from datetime import datetime
import json
import subprocess
from pathlib import Path


class TDDPhase(Enum):
    """TDD phases"""
    RED = "red"      # Write failing test
    GREEN = "green"  # Write minimal code to pass
    REFACTOR = "refactor"  # Refactor while keeping tests green


class TestGenerator:
    """Generates tests from specifications"""
    
    def __init__(self):
        self.test_templates = {
            'unit': self._generate_unit_test,
            'integration': self._generate_integration_test,
            'contract': self._generate_contract_test,
            'api': self._generate_api_test
        }
    
    def generate_tests_from_spec(self, spec_data: Dict[str, Any], 
                                test_type: str = 'unit') -> List[Dict[str, Any]]:
        """Generate tests from specification"""
        if test_type not in self.test_templates:
            raise ValueError(f"Unknown test type: {test_type}")
        
        generator = self.test_templates[test_type]
        return generator(spec_data)
    
    def _generate_unit_test(self, spec_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate unit tests"""
        tests = []
        
        # Generate tests for each requirement
        requirements = spec_data.get('requirements', [])
        for i, requirement in enumerate(requirements):
            test = {
                'name': f'test_requirement_{i+1}',
                'description': f'Test requirement: {requirement}',
                'type': 'unit',
                'code': self._generate_unit_test_code(requirement, i+1),
                'setup': self._generate_test_setup(),
                'teardown': self._generate_test_teardown()
            }
            tests.append(test)
        
        # Generate tests for acceptance criteria
        acceptance_criteria = spec_data.get('acceptance_criteria', [])
        for i, criteria in enumerate(acceptance_criteria):
            test = {
                'name': f'test_acceptance_criteria_{i+1}',
                'description': f'Test acceptance criteria: {criteria}',
                'type': 'unit',
                'code': self._generate_acceptance_test_code(criteria, i+1),
                'setup': self._generate_test_setup(),
                'teardown': self._generate_test_teardown()
            }
            tests.append(test)
        
        return tests
    
    def _generate_integration_test(self, spec_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate integration tests"""
        tests = []
        
        # Generate integration test for main functionality
        test = {
            'name': 'test_integration_main_flow',
            'description': 'Test main integration flow',
            'type': 'integration',
            'code': self._generate_integration_test_code(spec_data),
            'setup': self._generate_integration_setup(),
            'teardown': self._generate_integration_teardown()
        }
        tests.append(test)
        
        return tests
    
    def _generate_contract_test(self, spec_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate contract tests"""
        tests = []
        
        # Generate contract test for API if present
        if 'api' in spec_data:
            test = {
                'name': 'test_api_contract',
                'description': 'Test API contract compliance',
                'type': 'contract',
                'code': self._generate_api_contract_test_code(spec_data['api']),
                'setup': self._generate_contract_setup(),
                'teardown': self._generate_contract_teardown()
            }
            tests.append(test)
        
        return tests
    
    def _generate_api_test(self, spec_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate API tests"""
        tests = []
        
        api_config = spec_data.get('api', {})
        endpoints = api_config.get('endpoints', [])
        
        for i, endpoint in enumerate(endpoints):
            test = {
                'name': f'test_api_endpoint_{i+1}',
                'description': f'Test API endpoint: {endpoint.get("path", "")}',
                'type': 'api',
                'code': self._generate_api_endpoint_test_code(endpoint, i+1),
                'setup': self._generate_api_setup(),
                'teardown': self._generate_api_teardown()
            }
            tests.append(test)
        
        return tests
    
    def _generate_unit_test_code(self, requirement: str, index: int) -> str:
        """Generate unit test code"""
        return f'''def test_requirement_{index}():
    """Test requirement: {requirement}"""
    # TODO: Implement test for requirement
    # Arrange
    # Act  
    # Assert
    assert True  # Placeholder - implement actual test logic
'''
    
    def _generate_acceptance_test_code(self, criteria: str, index: int) -> str:
        """Generate acceptance test code"""
        return f'''def test_acceptance_criteria_{index}():
    """Test acceptance criteria: {criteria}"""
    # TODO: Implement acceptance test
    # Given
    # When
    # Then
    assert True  # Placeholder - implement actual test logic
'''
    
    def _generate_integration_test_code(self, spec_data: Dict[str, Any]) -> str:
        """Generate integration test code"""
        return f'''def test_integration_main_flow():
    """Test main integration flow"""
    # TODO: Implement integration test
    # Setup components
    # Execute main flow
    # Verify end-to-end behavior
    assert True  # Placeholder - implement actual test logic
'''
    
    def _generate_api_contract_test_code(self, api_config: Dict[str, Any]) -> str:
        """Generate API contract test code"""
        return f'''def test_api_contract():
    """Test API contract compliance"""
    # TODO: Implement API contract test
    # Test API endpoints
    # Verify response schemas
    # Check status codes
    assert True  # Placeholder - implement actual test logic
'''
    
    def _generate_api_endpoint_test_code(self, endpoint: Dict[str, Any], index: int) -> str:
        """Generate API endpoint test code"""
        path = endpoint.get('path', '')
        method = endpoint.get('method', 'GET')
        
        return f'''def test_api_endpoint_{index}():
    """Test API endpoint: {method} {path}"""
    # TODO: Implement API endpoint test
    # Make request to {path}
    # Verify response
    assert True  # Placeholder - implement actual test logic
'''
    
    def _generate_test_setup(self) -> str:
        """Generate test setup code"""
        return '''def setup_test():
    """Setup test environment"""
    # TODO: Implement test setup
    pass
'''
    
    def _generate_test_teardown(self) -> str:
        """Generate test teardown code"""
        return '''def teardown_test():
    """Cleanup test environment"""
    # TODO: Implement test teardown
    pass
'''
    
    def _generate_integration_setup(self) -> str:
        """Generate integration test setup"""
        return '''def setup_integration_test():
    """Setup integration test environment"""
    # TODO: Implement integration test setup
    pass
'''
    
    def _generate_integration_teardown(self) -> str:
        """Generate integration test teardown"""
        return '''def teardown_integration_test():
    """Cleanup integration test environment"""
    # TODO: Implement integration test teardown
    pass
'''
    
    def _generate_contract_setup(self) -> str:
        """Generate contract test setup"""
        return '''def setup_contract_test():
    """Setup contract test environment"""
    # TODO: Implement contract test setup
    pass
'''
    
    def _generate_contract_teardown(self) -> str:
        """Generate contract test teardown"""
        return '''def teardown_contract_test():
    """Cleanup contract test environment"""
    # TODO: Implement contract test teardown
    pass
'''
    
    def _generate_api_setup(self) -> str:
        """Generate API test setup"""
        return '''def setup_api_test():
    """Setup API test environment"""
    # TODO: Implement API test setup
    pass
'''
    
    def _generate_api_teardown(self) -> str:
        """Generate API test teardown"""
        return '''def teardown_api_test():
    """Cleanup API test environment"""
    # TODO: Implement API test teardown
    pass
'''


class TestRunner:
    """Runs tests and manages TDD cycle"""
    
    def __init__(self, test_directory: str = "tests"):
        self.test_directory = Path(test_directory)
        self.test_directory.mkdir(exist_ok=True)
        self.current_phase = TDDPhase.RED
        self.test_results: List[Dict[str, Any]] = []
    
    def run_tests(self, test_files: List[str] = None) -> Dict[str, Any]:
        """Run tests and return results"""
        if test_files is None:
            test_files = list(self.test_directory.glob("test_*.py"))
        
        results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'test_results': [],
            'timestamp': datetime.now().isoformat()
        }
        
        for test_file in test_files:
            file_results = self._run_test_file(test_file)
            results['test_results'].extend(file_results)
            results['total_tests'] += len(file_results)
            
            for test_result in file_results:
                if test_result['status'] == 'passed':
                    results['passed'] += 1
                elif test_result['status'] == 'failed':
                    results['failed'] += 1
                else:
                    results['errors'] += 1
        
        results['success_rate'] = (results['passed'] / results['total_tests'] * 100) if results['total_tests'] > 0 else 0
        
        return results
    
    def _run_test_file(self, test_file: Path) -> List[Dict[str, Any]]:
        """Run individual test file"""
        results = []
        
        try:
            # Run pytest on the test file
            cmd = ['python', '-m', 'pytest', str(test_file), '-v', '--tb=short']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Parse pytest output (simplified)
            lines = result.stdout.split('\n')
            for line in lines:
                if '::' in line and ('PASSED' in line or 'FAILED' in line or 'ERROR' in line):
                    parts = line.split('::')
                    if len(parts) >= 2:
                        test_name = parts[-1].split()[0]
                        status = 'passed' if 'PASSED' in line else 'failed' if 'FAILED' in line else 'error'
                        
                        results.append({
                            'test_name': test_name,
                            'file': str(test_file),
                            'status': status,
                            'message': line.strip()
                        })
            
        except subprocess.TimeoutExpired:
            results.append({
                'test_name': 'timeout',
                'file': str(test_file),
                'status': 'error',
                'message': 'Test execution timeout'
            })
        except Exception as e:
            results.append({
                'test_name': 'error',
                'file': str(test_file),
                'status': 'error',
                'message': f'Test execution error: {str(e)}'
            })
        
        return results
    
    def generate_test_files(self, tests: List[Dict[str, Any]], 
                          feature_name: str = "feature") -> List[str]:
        """Generate test files from test definitions"""
        generated_files = []
        
        # Group tests by type
        test_groups = {}
        for test in tests:
            test_type = test.get('type', 'unit')
            if test_type not in test_groups:
                test_groups[test_type] = []
            test_groups[test_type].append(test)
        
        # Generate test files for each type
        for test_type, type_tests in test_groups.items():
            filename = f"test_{feature_name}_{test_type}.py"
            file_path = self.test_directory / filename
            
            content = self._generate_test_file_content(type_tests, test_type)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            generated_files.append(str(file_path))
        
        return generated_files
    
    def _generate_test_file_content(self, tests: List[Dict[str, Any]], 
                                   test_type: str) -> str:
        """Generate test file content"""
        content = f'"""\n{test_type.title()} tests\n"""\n\n'
        content += 'import pytest\n\n'
        
        # Add setup and teardown if present
        setup_code = tests[0].get('setup', '') if tests else ''
        teardown_code = tests[0].get('teardown', '') if tests else ''
        
        if setup_code:
            content += setup_code + '\n\n'
        
        # Add test functions
        for test in tests:
            content += test.get('code', '') + '\n\n'
        
        if teardown_code:
            content += teardown_code + '\n'
        
        return content


class TDDIntegration:
    """Main TDD integration manager"""
    
    def __init__(self):
        self.test_generator = TestGenerator()
        self.test_runner = TestRunner()
        self.current_cycle = 1
        self.cycle_history: List[Dict[str, Any]] = []
    
    def start_tdd_cycle(self, spec_data: Dict[str, Any], 
                       feature_name: str = "feature") -> Dict[str, Any]:
        """Start new TDD cycle"""
        cycle_info = {
            'cycle_number': self.current_cycle,
            'feature_name': feature_name,
            'phase': TDDPhase.RED.value,
            'start_time': datetime.now().isoformat(),
            'spec_data': spec_data
        }
        
        # Generate tests for RED phase
        tests = self.test_generator.generate_tests_from_spec(spec_data)
        test_files = self.test_runner.generate_test_files(tests, feature_name)
        
        cycle_info['test_files'] = test_files
        cycle_info['tests_generated'] = len(tests)
        
        self.cycle_history.append(cycle_info)
        self.current_cycle += 1
        
        return cycle_info
    
    def run_red_phase(self, test_files: List[str]) -> Dict[str, Any]:
        """Run RED phase - tests should fail"""
        results = self.test_runner.run_tests(test_files)
        
        # In RED phase, we expect tests to fail
        red_phase_success = results['failed'] > 0 or results['errors'] > 0
        
        return {
            'phase': TDDPhase.RED.value,
            'expected_result': 'tests_should_fail',
            'actual_result': 'tests_failed' if red_phase_success else 'tests_passed',
            'success': red_phase_success,
            'test_results': results
        }
    
    def run_green_phase(self, test_files: List[str]) -> Dict[str, Any]:
        """Run GREEN phase - implement minimal code to pass tests"""
        results = self.test_runner.run_tests(test_files)
        
        # In GREEN phase, we expect tests to pass
        green_phase_success = results['failed'] == 0 and results['errors'] == 0
        
        return {
            'phase': TDDPhase.GREEN.value,
            'expected_result': 'tests_should_pass',
            'actual_result': 'tests_passed' if green_phase_success else 'tests_failed',
            'success': green_phase_success,
            'test_results': results
        }
    
    def run_refactor_phase(self, test_files: List[str]) -> Dict[str, Any]:
        """Run REFACTOR phase - refactor while keeping tests green"""
        results = self.test_runner.run_tests(test_files)
        
        # In REFACTOR phase, tests should still pass
        refactor_phase_success = results['failed'] == 0 and results['errors'] == 0
        
        return {
            'phase': TDDPhase.REFACTOR.value,
            'expected_result': 'tests_should_still_pass',
            'actual_result': 'tests_passed' if refactor_phase_success else 'tests_failed',
            'success': refactor_phase_success,
            'test_results': results
        }
    
    def complete_tdd_cycle(self, feature_name: str) -> Dict[str, Any]:
        """Complete TDD cycle and generate report"""
        if not self.cycle_history:
            return {'error': 'No TDD cycles to complete'}
        
        last_cycle = self.cycle_history[-1]
        
        # Run final tests
        test_files = last_cycle.get('test_files', [])
        final_results = self.test_runner.run_tests(test_files)
        
        cycle_summary = {
            'cycle_number': last_cycle['cycle_number'],
            'feature_name': feature_name,
            'completion_time': datetime.now().isoformat(),
            'final_test_results': final_results,
            'cycle_history': self.cycle_history,
            'tdd_success': final_results['success_rate'] >= 80
        }
        
        return cycle_summary
    
    def get_tdd_report(self) -> Dict[str, Any]:
        """Generate TDD report"""
        return {
            'total_cycles': len(self.cycle_history),
            'current_cycle': self.current_cycle,
            'cycle_history': self.cycle_history,
            'generated_at': datetime.now().isoformat()
        }
