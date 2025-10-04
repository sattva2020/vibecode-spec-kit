"""
Contract testing framework for Memory Bank CLI
"""

from typing import Dict, List, Any, Optional, Union
from enum import Enum
from datetime import datetime
import json
import requests
from pathlib import Path


class ContractType(Enum):
    """Types of contracts"""
    API = "api"
    COMPONENT = "component"
    DATABASE = "database"
    FILE = "file"
    CLI = "cli"


class ContractValidator:
    """Base contract validator"""
    
    def __init__(self, contract_type: ContractType):
        self.contract_type = contract_type
        self.validation_results: List[Dict[str, Any]] = []
    
    def validate(self, contract: Dict[str, Any], implementation: Any) -> Dict[str, Any]:
        """Validate contract against implementation"""
        raise NotImplementedError


class APIContractValidator(ContractValidator):
    """API contract validator"""
    
    def __init__(self):
        super().__init__(ContractType.API)
    
    def validate(self, contract: Dict[str, Any], base_url: str) -> Dict[str, Any]:
        """Validate API contract"""
        results = {
            'contract_type': 'api',
            'base_url': base_url,
            'validations': [],
            'passed': 0,
            'failed': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        endpoints = contract.get('endpoints', [])
        
        for endpoint in endpoints:
            validation_result = self._validate_endpoint(endpoint, base_url)
            results['validations'].append(validation_result)
            
            if validation_result['passed']:
                results['passed'] += 1
            else:
                results['failed'] += 1
        
        results['total'] = results['passed'] + results['failed']
        results['success_rate'] = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
        
        return results
    
    def _validate_endpoint(self, endpoint: Dict[str, Any], base_url: str) -> Dict[str, Any]:
        """Validate individual API endpoint"""
        result = {
            'endpoint': endpoint.get('path', ''),
            'method': endpoint.get('method', 'GET'),
            'passed': False,
            'status_code': None,
            'response_time': 0,
            'errors': []
        }
        
        try:
            url = f"{base_url.rstrip('/')}/{endpoint['path'].lstrip('/')}"
            method = endpoint.get('method', 'GET').upper()
            
            # Prepare request parameters
            params = endpoint.get('params', {})
            headers = endpoint.get('headers', {})
            data = endpoint.get('data')
            
            # Make request
            start_time = datetime.now()
            
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                result['errors'].append(f"Unsupported HTTP method: {method}")
                return result
            
            end_time = datetime.now()
            result['response_time'] = (end_time - start_time).total_seconds()
            result['status_code'] = response.status_code
            
            # Validate response
            expected_status = endpoint.get('expected_status', 200)
            if response.status_code != expected_status:
                result['errors'].append(f"Expected status {expected_status}, got {response.status_code}")
            
            # Validate response schema if provided
            expected_schema = endpoint.get('response_schema')
            if expected_schema:
                try:
                    response_data = response.json()
                    schema_validation = self._validate_schema(response_data, expected_schema)
                    if not schema_validation['valid']:
                        result['errors'].extend(schema_validation['errors'])
                except json.JSONDecodeError:
                    result['errors'].append("Response is not valid JSON")
            
            result['passed'] = len(result['errors']) == 0
            
        except requests.exceptions.RequestException as e:
            result['errors'].append(f"Request failed: {str(e)}")
        except Exception as e:
            result['errors'].append(f"Validation error: {str(e)}")
        
        return result
    
    def _validate_schema(self, data: Any, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against JSON schema"""
        # Simplified schema validation
        result = {'valid': True, 'errors': []}
        
        required_fields = schema.get('required', [])
        properties = schema.get('properties', {})
        
        for field in required_fields:
            if field not in data:
                result['errors'].append(f"Required field '{field}' missing")
                result['valid'] = False
        
        for field, value in data.items():
            if field in properties:
                field_schema = properties[field]
                field_type = field_schema.get('type')
                
                if field_type == 'string' and not isinstance(value, str):
                    result['errors'].append(f"Field '{field}' should be string, got {type(value).__name__}")
                    result['valid'] = False
                elif field_type == 'number' and not isinstance(value, (int, float)):
                    result['errors'].append(f"Field '{field}' should be number, got {type(value).__name__}")
                    result['valid'] = False
                elif field_type == 'boolean' and not isinstance(value, bool):
                    result['errors'].append(f"Field '{field}' should be boolean, got {type(value).__name__}")
                    result['valid'] = False
        
        return result


class ComponentContractValidator(ContractValidator):
    """Component contract validator"""
    
    def __init__(self):
        super().__init__(ContractType.COMPONENT)
    
    def validate(self, contract: Dict[str, Any], component: Any) -> Dict[str, Any]:
        """Validate component contract"""
        results = {
            'contract_type': 'component',
            'component_name': contract.get('name', 'unknown'),
            'validations': [],
            'passed': 0,
            'failed': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Validate interface
        interface_validation = self._validate_interface(contract, component)
        results['validations'].append(interface_validation)
        
        if interface_validation['passed']:
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # Validate methods
        methods = contract.get('methods', [])
        for method in methods:
            method_validation = self._validate_method(method, component)
            results['validations'].append(method_validation)
            
            if method_validation['passed']:
                results['passed'] += 1
            else:
                results['failed'] += 1
        
        results['total'] = results['passed'] + results['failed']
        results['success_rate'] = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
        
        return results
    
    def _validate_interface(self, contract: Dict[str, Any], component: Any) -> Dict[str, Any]:
        """Validate component interface"""
        result = {
            'validation_type': 'interface',
            'passed': False,
            'errors': []
        }
        
        try:
            # Check if component exists
            if component is None:
                result['errors'].append("Component is None")
                return result
            
            # Check required attributes
            required_attrs = contract.get('required_attributes', [])
            for attr in required_attrs:
                if not hasattr(component, attr):
                    result['errors'].append(f"Required attribute '{attr}' missing")
            
            # Check attribute types
            attribute_types = contract.get('attribute_types', {})
            for attr, expected_type in attribute_types.items():
                if hasattr(component, attr):
                    actual_value = getattr(component, attr)
                    if not isinstance(actual_value, expected_type):
                        result['errors'].append(
                            f"Attribute '{attr}' should be {expected_type.__name__}, "
                            f"got {type(actual_value).__name__}"
                        )
            
            result['passed'] = len(result['errors']) == 0
            
        except Exception as e:
            result['errors'].append(f"Interface validation error: {str(e)}")
        
        return result
    
    def _validate_method(self, method: Dict[str, Any], component: Any) -> Dict[str, Any]:
        """Validate component method"""
        result = {
            'validation_type': 'method',
            'method_name': method.get('name', ''),
            'passed': False,
            'errors': []
        }
        
        try:
            method_name = method.get('name')
            if not method_name:
                result['errors'].append("Method name not specified")
                return result
            
            if not hasattr(component, method_name):
                result['errors'].append(f"Method '{method_name}' not found")
                return result
            
            method_obj = getattr(component, method_name)
            if not callable(method_obj):
                result['errors'].append(f"'{method_name}' is not callable")
                return result
            
            # Test method signature if specified
            expected_params = method.get('parameters', [])
            # This is a simplified validation - in practice, you'd use inspect module
            
            result['passed'] = len(result['errors']) == 0
            
        except Exception as e:
            result['errors'].append(f"Method validation error: {str(e)}")
        
        return result


class ContractTester:
    """Main contract testing orchestrator"""
    
    def __init__(self):
        self.validators = {
            ContractType.API: APIContractValidator(),
            ContractType.COMPONENT: ComponentContractValidator()
        }
        self.contracts: Dict[str, Dict[str, Any]] = {}
        self.test_results: List[Dict[str, Any]] = []
    
    def load_contract(self, name: str, contract_data: Dict[str, Any]) -> None:
        """Load contract for testing"""
        self.contracts[name] = contract_data
    
    def load_contract_from_file(self, file_path: str) -> str:
        """Load contract from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            contract_data = json.load(f)
        
        contract_name = contract_data.get('name', Path(file_path).stem)
        self.load_contract(contract_name, contract_data)
        return contract_name
    
    def test_contract(self, contract_name: str, implementation: Any) -> Dict[str, Any]:
        """Test specific contract"""
        if contract_name not in self.contracts:
            raise ValueError(f"Contract '{contract_name}' not found")
        
        contract = self.contracts[contract_name]
        contract_type = ContractType(contract.get('type', 'component'))
        
        if contract_type not in self.validators:
            raise ValueError(f"No validator for contract type: {contract_type}")
        
        validator = self.validators[contract_type]
        result = validator.validate(contract, implementation)
        
        result['contract_name'] = contract_name
        self.test_results.append(result)
        
        return result
    
    def test_all_contracts(self, implementations: Dict[str, Any]) -> Dict[str, Any]:
        """Test all loaded contracts"""
        results = {
            'total_contracts': len(self.contracts),
            'passed': 0,
            'failed': 0,
            'test_results': [],
            'timestamp': datetime.now().isoformat()
        }
        
        for contract_name in self.contracts:
            implementation = implementations.get(contract_name)
            if implementation is None:
                results['test_results'].append({
                    'contract_name': contract_name,
                    'status': 'skipped',
                    'error': 'No implementation provided'
                })
                results['failed'] += 1
                continue
            
            try:
                result = self.test_contract(contract_name, implementation)
                results['test_results'].append(result)
                
                if result.get('success_rate', 0) >= 80:  # 80% threshold
                    results['passed'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                results['test_results'].append({
                    'contract_name': contract_name,
                    'status': 'error',
                    'error': str(e)
                })
                results['failed'] += 1
        
        results['success_rate'] = (results['passed'] / results['total_contracts'] * 100) if results['total_contracts'] > 0 else 0
        
        return results
    
    def generate_report(self, output_file: str = "contract_test_report.json") -> str:
        """Generate contract test report"""
        report = {
            'summary': {
                'total_contracts': len(self.contracts),
                'total_tests': len(self.test_results),
                'timestamp': datetime.now().isoformat()
            },
            'test_results': self.test_results
        }
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        return str(output_path)
