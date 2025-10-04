"""
Testing commands for Memory Bank CLI
"""

import argparse
from typing import Dict, Any

from ..core.config import CLIConfig
from ..core.testing import TestFramework, ContractTester, TDDIntegration, QAEnhancer, QualityLevel
from ..utils.output import OutputFormatter


class TestingCommand:
    """Testing command handler"""
    
    def __init__(self):
        self.test_framework = TestFramework()
        self.contract_tester = ContractTester()
        self.tdd_integration = TDDIntegration()
        self.qa_enhancer = QAEnhancer()
    
    def execute(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute testing command"""
        try:
            if args.testing_action == 'run':
                return self._run_tests(args, config, formatter)
            elif args.testing_action == 'tdd':
                return self._tdd_cycle(args, config, formatter)
            elif args.testing_action == 'contract':
                return self._contract_test(args, config, formatter)
            elif args.testing_action == 'qa':
                return self._qa_assessment(args, config, formatter)
            elif args.testing_action == 'generate':
                return self._generate_tests(args, config, formatter)
            else:
                formatter.error(f"Unknown testing action: {args.testing_action}")
                return 1
        except Exception as e:
            formatter.error(f"Testing command failed: {e}")
            return 1
    
    def _run_tests(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Run test suite"""
        formatter.info("🧪 Running Test Suite")
        
        # Create test suites
        cli_suite = self.test_framework.create_cli_tests()
        template_suite = self.test_framework.create_template_tests()
        workflow_suite = self.test_framework.create_workflow_tests()
        
        # Run all tests
        summary = self.test_framework.run_all_tests()
        
        # Display results
        formatter.info(f"📊 Test Results Summary:")
        formatter.info(f"  Total Tests: {summary['total_tests']}")
        formatter.info(f"  Passed: {summary['passed']}")
        formatter.info(f"  Failed: {summary['failed']}")
        formatter.info(f"  Skipped: {summary['skipped']}")
        formatter.info(f"  Errors: {summary['errors']}")
        formatter.info(f"  Success Rate: {summary['success_rate']:.1f}%")
        formatter.info(f"  Total Duration: {summary['total_duration']:.2f}s")
        
        # Show detailed results
        if args.verbose > 0:
            formatter.info("\n📋 Detailed Results:")
            for result in self.test_framework.results:
                status_icon = "✅" if result.status.value == "passed" else "❌" if result.status.value == "failed" else "⚠️"
                formatter.info(f"  {status_icon} {result.test_name}: {result.status.value} ({result.duration:.2f}s)")
                if result.message and result.status.value != "passed":
                    formatter.info(f"      {result.message}")
        
        # Generate report
        if args.report:
            report_file = self.test_framework.generate_report()
            formatter.success(f"📄 Test report generated: {report_file}")
        
        return 0 if summary['failed'] == 0 and summary['errors'] == 0 else 1
    
    def _tdd_cycle(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Run TDD cycle"""
        formatter.info("🔄 Starting TDD Cycle")
        
        if args.tdd_action == 'start':
            return self._start_tdd_cycle(args, formatter)
        elif args.tdd_action == 'red':
            return self._run_red_phase(args, formatter)
        elif args.tdd_action == 'green':
            return self._run_green_phase(args, formatter)
        elif args.tdd_action == 'refactor':
            return self._run_refactor_phase(args, formatter)
        elif args.tdd_action == 'complete':
            return self._complete_tdd_cycle(args, formatter)
        else:
            formatter.error(f"Unknown TDD action: {args.tdd_action}")
            return 1
    
    def _start_tdd_cycle(self, args: argparse.Namespace, formatter: OutputFormatter) -> int:
        """Start new TDD cycle"""
        feature_name = args.feature_name or "feature"
        
        # Load specification if provided
        spec_data = {}
        if args.spec_file:
            import json
            with open(args.spec_file, 'r', encoding='utf-8') as f:
                spec_data = json.load(f)
        
        # Start TDD cycle
        cycle_info = self.tdd_integration.start_tdd_cycle(spec_data, feature_name)
        
        formatter.success(f"🚀 TDD Cycle Started for '{feature_name}'")
        formatter.info(f"  Cycle Number: {cycle_info['cycle_number']}")
        formatter.info(f"  Phase: {cycle_info['phase']}")
        formatter.info(f"  Tests Generated: {cycle_info['tests_generated']}")
        formatter.info(f"  Test Files: {len(cycle_info['test_files'])}")
        
        for test_file in cycle_info['test_files']:
            formatter.info(f"    - {test_file}")
        
        formatter.info("\n💡 Next Steps:")
        formatter.info("  1. Review generated tests")
        formatter.info("  2. Run 'testing tdd red' to verify tests fail")
        formatter.info("  3. Implement minimal code to pass tests")
        formatter.info("  4. Run 'testing tdd green' to verify tests pass")
        
        return 0
    
    def _run_red_phase(self, args: argparse.Namespace, formatter: OutputFormatter) -> int:
        """Run RED phase"""
        formatter.info("🔴 Running RED Phase - Tests Should Fail")
        
        # Get test files from last cycle
        if not self.tdd_integration.cycle_history:
            formatter.error("No TDD cycle found. Run 'testing tdd start' first.")
            return 1
        
        last_cycle = self.tdd_integration.cycle_history[-1]
        test_files = last_cycle.get('test_files', [])
        
        # Run RED phase
        red_result = self.tdd_integration.run_red_phase(test_files)
        
        if red_result['success']:
            formatter.success("✅ RED Phase Successful - Tests Failed as Expected")
            formatter.info(f"  Failed Tests: {red_result['test_results']['failed']}")
            formatter.info(f"  Errors: {red_result['test_results']['errors']}")
        else:
            formatter.error("❌ RED Phase Failed - Tests Passed When They Should Fail")
            formatter.info("  This indicates the implementation already exists or tests are incorrect")
        
        return 0 if red_result['success'] else 1
    
    def _run_green_phase(self, args: argparse.Namespace, formatter: OutputFormatter) -> int:
        """Run GREEN phase"""
        formatter.info("🟢 Running GREEN Phase - Implement Minimal Code")
        
        # Get test files from last cycle
        if not self.tdd_integration.cycle_history:
            formatter.error("No TDD cycle found. Run 'testing tdd start' first.")
            return 1
        
        last_cycle = self.tdd_integration.cycle_history[-1]
        test_files = last_cycle.get('test_files', [])
        
        # Run GREEN phase
        green_result = self.tdd_integration.run_green_phase(test_files)
        
        if green_result['success']:
            formatter.success("✅ GREEN Phase Successful - All Tests Pass")
            formatter.info(f"  Passed Tests: {green_result['test_results']['passed']}")
            formatter.info(f"  Success Rate: {green_result['test_results']['success_rate']:.1f}%")
        else:
            formatter.error("❌ GREEN Phase Failed - Tests Still Failing")
            formatter.info(f"  Failed Tests: {green_result['test_results']['failed']}")
            formatter.info("  Implement minimal code to make tests pass")
        
        return 0 if green_result['success'] else 1
    
    def _run_refactor_phase(self, args: argparse.Namespace, formatter: OutputFormatter) -> int:
        """Run REFACTOR phase"""
        formatter.info("🔧 Running REFACTOR Phase - Improve Code Quality")
        
        # Get test files from last cycle
        if not self.tdd_integration.cycle_history:
            formatter.error("No TDD cycle found. Run 'testing tdd start' first.")
            return 1
        
        last_cycle = self.tdd_integration.cycle_history[-1]
        test_files = last_cycle.get('test_files', [])
        
        # Run REFACTOR phase
        refactor_result = self.tdd_integration.run_refactor_phase(test_files)
        
        if refactor_result['success']:
            formatter.success("✅ REFACTOR Phase Successful - Tests Still Pass")
            formatter.info(f"  Passed Tests: {refactor_result['test_results']['passed']}")
            formatter.info(f"  Success Rate: {refactor_result['test_results']['success_rate']:.1f}%")
        else:
            formatter.error("❌ REFACTOR Phase Failed - Tests Broke During Refactoring")
            formatter.info(f"  Failed Tests: {refactor_result['test_results']['failed']}")
            formatter.info("  Fix the broken tests before proceeding")
        
        return 0 if refactor_result['success'] else 1
    
    def _complete_tdd_cycle(self, args: argparse.Namespace, formatter: OutputFormatter) -> int:
        """Complete TDD cycle"""
        formatter.info("🏁 Completing TDD Cycle")
        
        feature_name = args.feature_name or "feature"
        
        # Complete TDD cycle
        cycle_summary = self.tdd_integration.complete_tdd_cycle(feature_name)
        
        if 'error' in cycle_summary:
            formatter.error(f"❌ TDD Cycle Completion Failed: {cycle_summary['error']}")
            return 1
        
        formatter.success(f"✅ TDD Cycle Completed for '{feature_name}'")
        formatter.info(f"  Final Success Rate: {cycle_summary['final_test_results']['success_rate']:.1f}%")
        formatter.info(f"  TDD Success: {'✅' if cycle_summary['tdd_success'] else '❌'}")
        
        if args.report:
            # Generate TDD report
            tdd_report = self.tdd_integration.get_tdd_report()
            import json
            with open('tdd_report.json', 'w', encoding='utf-8') as f:
                json.dump(tdd_report, f, indent=2)
            formatter.success("📄 TDD report generated: tdd_report.json")
        
        return 0 if cycle_summary['tdd_success'] else 1
    
    def _contract_test(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Run contract tests"""
        formatter.info("📋 Running Contract Tests")
        
        if args.contract_action == 'load':
            return self._load_contract(args, formatter)
        elif args.contract_action == 'test':
            return self._test_contract(args, formatter)
        elif args.contract_action == 'test-all':
            return self._test_all_contracts(args, formatter)
        else:
            formatter.error(f"Unknown contract action: {args.contract_action}")
            return 1
    
    def _load_contract(self, args: argparse.Namespace, formatter: OutputFormatter) -> int:
        """Load contract from file"""
        contract_name = self.contract_tester.load_contract_from_file(args.contract_file)
        formatter.success(f"✅ Contract loaded: {contract_name}")
        return 0
    
    def _test_contract(self, args: argparse.Namespace, formatter: OutputFormatter) -> int:
        """Test specific contract"""
        # This would require implementation details
        formatter.info("📋 Contract testing requires implementation details")
        formatter.info("Use 'testing contract test-all' to test all loaded contracts")
        return 0
    
    def _test_all_contracts(self, args: argparse.Namespace, formatter: OutputFormatter) -> int:
        """Test all loaded contracts"""
        # This would require implementation details
        formatter.info("📋 Testing all loaded contracts")
        formatter.info("No contracts loaded. Use 'testing contract load' to load contracts first.")
        return 0
    
    def _qa_assessment(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Run QA assessment"""
        formatter.info("🔍 Running QA Assessment")
        
        # Set quality level
        quality_level = QualityLevel(args.quality_level) if args.quality_level else QualityLevel.STANDARD
        
        # Create QA enhancer with specified quality level
        qa_enhancer = QAEnhancer(quality_level)
        
        # Run quality assessment
        assessment = qa_enhancer.run_quality_assessment()
        
        # Display results
        formatter.info(f"📊 QA Assessment Results:")
        formatter.info(f"  Quality Level: {assessment['quality_level']}")
        formatter.info(f"  Overall Score: {assessment['overall_score']:.1f}/100")
        formatter.info(f"  Assessment Passed: {'✅' if assessment['passed'] else '❌'}")
        
        # Show quality gate results
        formatter.info(f"\n📋 Quality Gates:")
        for gate_result in assessment['quality_gates']:
            status = "✅" if gate_result['passed'] else "❌"
            formatter.info(f"  {status} {gate_result['gate_name']}: {gate_result['score']:.1f}/100")
            
            if gate_result['issues']:
                for issue in gate_result['issues']:
                    formatter.warning(f"    - {issue}")
        
        # Show compliance results
        compliance = assessment['compliance_check']
        status = "✅" if compliance['score'] >= 80 else "❌"
        formatter.info(f"\n📋 Compliance Check:")
        formatter.info(f"  {status} Compliance Score: {compliance['score']:.1f}/100")
        formatter.info(f"  Rules Passed: {compliance['passed']}/{compliance['total_rules']}")
        
        if compliance['violations']:
            formatter.warning("  Violations:")
            for violation in compliance['violations']:
                formatter.warning(f"    - {violation['rule_name']}: {violation['message']}")
        
        # Generate report
        if args.report:
            report_file = qa_enhancer.generate_qa_report(assessment)
            formatter.success(f"📄 QA report generated: {report_file}")
        
        return 0 if assessment['passed'] else 1
    
    def _generate_tests(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Generate tests from specification"""
        formatter.info("🔧 Generating Tests from Specification")
        
        # Load specification
        import json
        with open(args.spec_file, 'r', encoding='utf-8') as f:
            spec_data = json.load(f)
        
        # Generate tests
        test_generator = self.tdd_integration.test_generator
        tests = test_generator.generate_tests_from_spec(spec_data, args.test_type)
        
        # Generate test files
        feature_name = args.feature_name or "feature"
        test_files = self.tdd_integration.test_runner.generate_test_files(tests, feature_name)
        
        formatter.success(f"✅ Generated {len(tests)} tests for '{feature_name}'")
        formatter.info(f"  Test Type: {args.test_type}")
        formatter.info(f"  Test Files: {len(test_files)}")
        
        for test_file in test_files:
            formatter.info(f"    - {test_file}")
        
        formatter.info("\n💡 Next Steps:")
        formatter.info("  1. Review generated tests")
        formatter.info("  2. Implement test logic")
        formatter.info("  3. Run 'testing run' to execute tests")
        
        return 0


# Create command instance
testing_command = TestingCommand()

__all__ = ['testing_command']
