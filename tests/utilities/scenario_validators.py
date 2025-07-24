#!/usr/bin/env python3
"""
Scenario validation helpers for BDD testing.
Provides utilities to validate test scenarios and results.
"""

import json
import time
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from enum import Enum
import re

# Add project imports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from coordination_system.conflict_resolution import ConflictType, ConflictSeverity
from coordination_system.load_balancer import LoadBalancingStrategy, TaskPriority


class ValidationResult(Enum):
    """Validation result types."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"


@dataclass
class ValidationError:
    """Validation error details."""
    field: str
    expected: Any
    actual: Any
    message: str
    severity: str = "error"


@dataclass
class ScenarioValidationResult:
    """Result of scenario validation."""
    scenario_name: str
    result: ValidationResult
    errors: List[ValidationError]
    warnings: List[ValidationError]
    execution_time: float
    metadata: Dict[str, Any]
    
    @property
    def is_valid(self) -> bool:
        """Check if scenario validation passed."""
        return self.result == ValidationResult.PASS and len(self.errors) == 0


class ScenarioValidator:
    """Base class for scenario validation."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"validator.{name}")
    
    def validate(self, scenario_data: Dict[str, Any]) -> ScenarioValidationResult:
        """Validate a scenario. Override in subclasses."""
        start_time = time.time()
        
        errors = []
        warnings = []
        
        try:
            self._validate_scenario(scenario_data, errors, warnings)
            result = ValidationResult.FAIL if errors else ValidationResult.PASS
        except Exception as e:
            errors.append(ValidationError(
                field="validation",
                expected="successful validation",
                actual=str(e),
                message=f"Validation failed with exception: {e}",
                severity="critical"
            ))
            result = ValidationResult.FAIL
        
        execution_time = time.time() - start_time
        
        return ScenarioValidationResult(
            scenario_name=self.name,
            result=result,
            errors=errors,
            warnings=warnings,
            execution_time=execution_time,
            metadata={"validator": self.__class__.__name__}
        )
    
    def _validate_scenario(self, scenario_data: Dict[str, Any], 
                          errors: List[ValidationError], 
                          warnings: List[ValidationError]) -> None:
        """Override this method in subclasses."""
        pass
    
    def _add_error(self, errors: List[ValidationError], field: str, 
                   expected: Any, actual: Any, message: str, severity: str = "error"):
        """Helper to add validation error."""
        errors.append(ValidationError(
            field=field,
            expected=expected,
            actual=actual,
            message=message,
            severity=severity
        ))
    
    def _add_warning(self, warnings: List[ValidationError], field: str,
                    expected: Any, actual: Any, message: str):
        """Helper to add validation warning."""
        warnings.append(ValidationError(
            field=field,
            expected=expected,
            actual=actual,
            message=message,
            severity="warning"
        ))


class AgentConfigurationValidator(ScenarioValidator):
    """Validator for agent configuration scenarios."""
    
    def __init__(self):
        super().__init__("agent_configuration")
    
    def _validate_scenario(self, scenario_data: Dict[str, Any], 
                          errors: List[ValidationError], 
                          warnings: List[ValidationError]) -> None:
        """Validate agent configuration scenario."""
        agents = scenario_data.get('agents', [])
        
        if not agents:
            self._add_error(errors, "agents", "non-empty list", "empty list", 
                          "No agents provided in scenario")
            return
        
        agent_names = set()
        
        for i, agent in enumerate(agents):
            agent_prefix = f"agents[{i}]"
            
            # Validate required fields
            required_fields = ['name', 'expertise_domains', 'max_concurrent_tasks', 
                             'cpu_cores', 'memory_gb']
            for field in required_fields:
                if field not in agent:
                    self._add_error(errors, f"{agent_prefix}.{field}", "present", "missing",
                                  f"Required field {field} missing from agent")
                    continue
                
                # Validate field types and values
                if field == 'name':
                    name = agent[field]
                    if not isinstance(name, str) or not name.strip():
                        self._add_error(errors, f"{agent_prefix}.{field}", "non-empty string", 
                                      type(name).__name__, "Agent name must be non-empty string")
                    elif name in agent_names:
                        self._add_error(errors, f"{agent_prefix}.{field}", "unique name", name,
                                      f"Duplicate agent name: {name}")
                    else:
                        agent_names.add(name)
                
                elif field == 'expertise_domains':
                    domains = agent[field]
                    if not isinstance(domains, list):
                        self._add_error(errors, f"{agent_prefix}.{field}", "list", 
                                      type(domains).__name__, "Expertise domains must be a list")
                    elif len(domains) == 0:
                        self._add_warning(warnings, f"{agent_prefix}.{field}", "non-empty", "empty",
                                        "Agent has no expertise domains")
                    elif len(set(domains)) != len(domains):
                        self._add_warning(warnings, f"{agent_prefix}.{field}", "unique domains", 
                                        "duplicates", "Agent has duplicate expertise domains")
                
                elif field in ['max_concurrent_tasks', 'cpu_cores', 'memory_gb']:
                    value = agent[field]
                    if not isinstance(value, int) or value <= 0:
                        self._add_error(errors, f"{agent_prefix}.{field}", "positive integer", 
                                      value, f"{field} must be positive integer")
            
            # Validate optional fields
            if 'current_workload' in agent:
                workload = agent['current_workload']
                if not isinstance(workload, (int, float)) or workload < 0:
                    self._add_error(errors, f"{agent_prefix}.current_workload", 
                                  "non-negative number", workload,
                                  "Current workload must be non-negative")
                elif workload > 100:
                    self._add_warning(warnings, f"{agent_prefix}.current_workload",
                                    "≤ 100%", f"{workload}%", 
                                    "Agent workload exceeds 100%")
            
            if 'reliability_score' in agent:
                reliability = agent['reliability_score']
                if not isinstance(reliability, (int, float)) or not (0 <= reliability <= 1):
                    self._add_error(errors, f"{agent_prefix}.reliability_score",
                                  "number between 0 and 1", reliability,
                                  "Reliability score must be between 0 and 1")


class TaskRequestValidator(ScenarioValidator):
    """Validator for task request scenarios."""
    
    def __init__(self):
        super().__init__("task_request")
    
    def _validate_scenario(self, scenario_data: Dict[str, Any], 
                          errors: List[ValidationError], 
                          warnings: List[ValidationError]) -> None:
        """Validate task request scenario."""
        tasks = scenario_data.get('tasks', [])
        
        if not tasks:
            self._add_error(errors, "tasks", "non-empty list", "empty list",
                          "No tasks provided in scenario")
            return
        
        task_ids = set()
        
        for i, task in enumerate(tasks):
            task_prefix = f"tasks[{i}]"
            
            # Validate required fields
            required_fields = ['id', 'description', 'domain', 'priority', 'estimated_duration']
            for field in required_fields:
                if field not in task:
                    self._add_error(errors, f"{task_prefix}.{field}", "present", "missing",
                                  f"Required field {field} missing from task")
                    continue
                
                if field == 'id':
                    task_id = task[field]
                    if not isinstance(task_id, str) or not task_id.strip():
                        self._add_error(errors, f"{task_prefix}.{field}", "non-empty string",
                                      type(task_id).__name__, "Task ID must be non-empty string")
                    elif task_id in task_ids:
                        self._add_error(errors, f"{task_prefix}.{field}", "unique ID", task_id,
                                      f"Duplicate task ID: {task_id}")
                    else:
                        task_ids.add(task_id)
                
                elif field == 'description':
                    desc = task[field]
                    if not isinstance(desc, str) or not desc.strip():
                        self._add_error(errors, f"{task_prefix}.{field}", "non-empty string",
                                      type(desc).__name__, "Task description must be non-empty string")
                
                elif field == 'domain':
                    domain = task[field]
                    if not isinstance(domain, str) or not domain.strip():
                        self._add_error(errors, f"{task_prefix}.{field}", "non-empty string",
                                      type(domain).__name__, "Task domain must be non-empty string")
                
                elif field == 'priority':
                    priority = task[field]
                    if isinstance(priority, str):
                        # Try to convert string to TaskPriority enum
                        try:
                            TaskPriority[priority.upper()]
                        except KeyError:
                            self._add_error(errors, f"{task_prefix}.{field}", "valid priority",
                                          priority, f"Invalid priority: {priority}")
                    elif not isinstance(priority, TaskPriority):
                        self._add_error(errors, f"{task_prefix}.{field}", "TaskPriority enum",
                                      type(priority).__name__, "Priority must be TaskPriority enum")
                
                elif field == 'estimated_duration':
                    duration = task[field]
                    if not isinstance(duration, (int, float)) or duration <= 0:
                        self._add_error(errors, f"{task_prefix}.{field}", "positive number",
                                      duration, "Estimated duration must be positive")
            
            # Validate dependencies
            if 'dependencies' in task:
                deps = task['dependencies']
                if not isinstance(deps, list):
                    self._add_error(errors, f"{task_prefix}.dependencies", "list",
                                  type(deps).__name__, "Dependencies must be a list")
                else:
                    for j, dep in enumerate(deps):
                        if not isinstance(dep, str):
                            self._add_error(errors, f"{task_prefix}.dependencies[{j}]", "string",
                                          type(dep).__name__, "Dependency ID must be string")
            
            # Validate resource requirements
            if 'resource_requirements' in task:
                resources = task['resource_requirements']
                if not isinstance(resources, dict):
                    self._add_error(errors, f"{task_prefix}.resource_requirements", "dict",
                                  type(resources).__name__, "Resource requirements must be dict")
                else:
                    for resource, value in resources.items():
                        if not isinstance(value, (int, float)) or value < 0:
                            self._add_error(errors, f"{task_prefix}.resource_requirements.{resource}",
                                          "non-negative number", value,
                                          f"Resource {resource} must be non-negative")


class ConflictScenarioValidator(ScenarioValidator):
    """Validator for conflict resolution scenarios."""
    
    def __init__(self):
        super().__init__("conflict_scenario")
    
    def _validate_scenario(self, scenario_data: Dict[str, Any], 
                          errors: List[ValidationError], 
                          warnings: List[ValidationError]) -> None:
        """Validate conflict scenario."""
        conflicts = scenario_data.get('conflicts', [])
        
        if not conflicts:
            self._add_error(errors, "conflicts", "non-empty list", "empty list",
                          "No conflicts provided in scenario")
            return
        
        for i, conflict in enumerate(conflicts):
            conflict_prefix = f"conflicts[{i}]"
            
            # Validate required fields
            required_fields = ['conflict_type', 'severity', 'parties', 'description']
            for field in required_fields:
                if field not in conflict:
                    self._add_error(errors, f"{conflict_prefix}.{field}", "present", "missing",
                                  f"Required field {field} missing from conflict")
                    continue
                
                if field == 'conflict_type':
                    c_type = conflict[field]
                    if isinstance(c_type, str):
                        try:
                            ConflictType[c_type.upper()]
                        except KeyError:
                            self._add_error(errors, f"{conflict_prefix}.{field}", "valid conflict type",
                                          c_type, f"Invalid conflict type: {c_type}")
                    elif not isinstance(c_type, ConflictType):
                        self._add_error(errors, f"{conflict_prefix}.{field}", "ConflictType enum",
                                      type(c_type).__name__, "Conflict type must be ConflictType enum")
                
                elif field == 'severity':
                    severity = conflict[field]
                    if isinstance(severity, str):
                        try:
                            ConflictSeverity[severity.upper()]
                        except KeyError:
                            self._add_error(errors, f"{conflict_prefix}.{field}", "valid severity",
                                          severity, f"Invalid severity: {severity}")
                    elif not isinstance(severity, ConflictSeverity):
                        self._add_error(errors, f"{conflict_prefix}.{field}", "ConflictSeverity enum",
                                      type(severity).__name__, "Severity must be ConflictSeverity enum")
                
                elif field == 'parties':
                    parties = conflict[field]
                    if not isinstance(parties, list):
                        self._add_error(errors, f"{conflict_prefix}.{field}", "list",
                                      type(parties).__name__, "Parties must be a list")
                    elif len(parties) < 2:
                        self._add_error(errors, f"{conflict_prefix}.{field}", "≥ 2 parties",
                                      f"{len(parties)} parties", "Conflict must have at least 2 parties")
                    elif len(set(parties)) != len(parties):
                        self._add_warning(warnings, f"{conflict_prefix}.{field}", "unique parties",
                                        "duplicates", "Conflict has duplicate parties")
                
                elif field == 'description':
                    desc = conflict[field]
                    if not isinstance(desc, str) or not desc.strip():
                        self._add_error(errors, f"{conflict_prefix}.{field}", "non-empty string",
                                      type(desc).__name__, "Conflict description must be non-empty string")
            
            # Validate context if present
            if 'context' in conflict:
                context = conflict['context']
                if not isinstance(context, dict):
                    self._add_error(errors, f"{conflict_prefix}.context", "dict",
                                  type(context).__name__, "Context must be a dictionary")
            
            # Validate resolution timeout
            if 'resolution_timeout' in conflict:
                timeout = conflict['resolution_timeout']
                if not isinstance(timeout, (int, float)) or timeout <= 0:
                    self._add_error(errors, f"{conflict_prefix}.resolution_timeout", "positive number",
                                  timeout, "Resolution timeout must be positive")


class LoadBalancingScenarioValidator(ScenarioValidator):
    """Validator for load balancing scenarios."""
    
    def __init__(self):
        super().__init__("load_balancing_scenario")
    
    def _validate_scenario(self, scenario_data: Dict[str, Any], 
                          errors: List[ValidationError], 
                          warnings: List[ValidationError]) -> None:
        """Validate load balancing scenario."""
        # Validate strategy
        if 'strategy' in scenario_data:
            strategy = scenario_data['strategy']
            if isinstance(strategy, str):
                try:
                    LoadBalancingStrategy[strategy.upper()]
                except KeyError:
                    self._add_error(errors, "strategy", "valid strategy", strategy,
                                  f"Invalid load balancing strategy: {strategy}")
            elif not isinstance(strategy, LoadBalancingStrategy):
                self._add_error(errors, "strategy", "LoadBalancingStrategy enum",
                              type(strategy).__name__, "Strategy must be LoadBalancingStrategy enum")
        
        # Validate agent workloads
        if 'agent_workloads' in scenario_data:
            workloads = scenario_data['agent_workloads']
            if not isinstance(workloads, dict):
                self._add_error(errors, "agent_workloads", "dict", type(workloads).__name__,
                              "Agent workloads must be a dictionary")
            else:
                for agent, workload in workloads.items():
                    if not isinstance(workload, (int, float)) or workload < 0:
                        self._add_error(errors, f"agent_workloads.{agent}", "non-negative number",
                                      workload, f"Workload for {agent} must be non-negative")
                    elif workload > 150:  # Allow some over-capacity for testing
                        self._add_warning(warnings, f"agent_workloads.{agent}", "reasonable load",
                                        f"{workload}%", f"Very high workload for {agent}")
        
        # Validate task distribution metrics
        if 'expected_efficiency' in scenario_data:
            efficiency = scenario_data['expected_efficiency']
            if not isinstance(efficiency, (int, float)) or not (0 <= efficiency <= 100):
                self._add_error(errors, "expected_efficiency", "percentage (0-100)", efficiency,
                              "Expected efficiency must be percentage between 0 and 100")
        
        if 'max_agent_load' in scenario_data:
            max_load = scenario_data['max_agent_load']
            if not isinstance(max_load, (int, float)) or max_load <= 0:
                self._add_error(errors, "max_agent_load", "positive number", max_load,
                              "Maximum agent load must be positive")


class CommunicationScenarioValidator(ScenarioValidator):
    """Validator for communication scenarios."""
    
    def __init__(self):
        super().__init__("communication_scenario")
    
    def _validate_scenario(self, scenario_data: Dict[str, Any], 
                          errors: List[ValidationError], 
                          warnings: List[ValidationError]) -> None:
        """Validate communication scenario."""
        # Validate network conditions
        if 'network_conditions' in scenario_data:
            network = scenario_data['network_conditions']
            if not isinstance(network, dict):
                self._add_error(errors, "network_conditions", "dict", type(network).__name__,
                              "Network conditions must be a dictionary")
            else:
                if 'latency_ms' in network:
                    latency = network['latency_ms']
                    if not isinstance(latency, (int, float)) or latency < 0:
                        self._add_error(errors, "network_conditions.latency_ms", "non-negative number",
                                      latency, "Latency must be non-negative")
                    elif latency > 30000:  # 30 seconds
                        self._add_warning(warnings, "network_conditions.latency_ms", "reasonable latency",
                                        f"{latency}ms", "Very high latency")
                
                if 'packet_loss_percent' in network:
                    loss = network['packet_loss_percent']
                    if not isinstance(loss, (int, float)) or not (0 <= loss <= 100):
                        self._add_error(errors, "network_conditions.packet_loss_percent", 
                                      "percentage (0-100)", loss,
                                      "Packet loss must be percentage between 0 and 100")
        
        # Validate message volume
        if 'message_count' in scenario_data:
            count = scenario_data['message_count']
            if not isinstance(count, int) or count < 0:
                self._add_error(errors, "message_count", "non-negative integer", count,
                              "Message count must be non-negative integer")
        
        if 'message_size_kb' in scenario_data:
            size = scenario_data['message_size_kb']
            if not isinstance(size, (int, float)) or size < 0:
                self._add_error(errors, "message_size_kb", "non-negative number", size,
                              "Message size must be non-negative")
        
        # Validate delivery expectations
        if 'expected_delivery_rate' in scenario_data:
            rate = scenario_data['expected_delivery_rate']
            if not isinstance(rate, (int, float)) or not (0 <= rate <= 100):
                self._add_error(errors, "expected_delivery_rate", "percentage (0-100)", rate,
                              "Expected delivery rate must be percentage between 0 and 100")


class ScenarioValidatorRegistry:
    """Registry for scenario validators."""
    
    def __init__(self):
        self.validators = {
            'agent_configuration': AgentConfigurationValidator(),
            'task_request': TaskRequestValidator(),
            'conflict_scenario': ConflictScenarioValidator(),
            'load_balancing_scenario': LoadBalancingScenarioValidator(),
            'communication_scenario': CommunicationScenarioValidator()
        }
    
    def get_validator(self, scenario_type: str) -> Optional[ScenarioValidator]:
        """Get validator for scenario type."""
        return self.validators.get(scenario_type)
    
    def register_validator(self, scenario_type: str, validator: ScenarioValidator):
        """Register a new validator."""
        self.validators[scenario_type] = validator
    
    def validate_scenario(self, scenario_type: str, 
                         scenario_data: Dict[str, Any]) -> ScenarioValidationResult:
        """Validate a scenario using appropriate validator."""
        validator = self.get_validator(scenario_type)
        if not validator:
            return ScenarioValidationResult(
                scenario_name=scenario_type,
                result=ValidationResult.SKIP,
                errors=[ValidationError(
                    field="validator",
                    expected="available validator",
                    actual="not found",
                    message=f"No validator found for scenario type: {scenario_type}"
                )],
                warnings=[],
                execution_time=0.0,
                metadata={"error": "validator_not_found"}
            )
        
        return validator.validate(scenario_data)


# Global registry instance
validator_registry = ScenarioValidatorRegistry()


# Convenience functions
def validate_agents(agents: List[Dict[str, Any]]) -> ScenarioValidationResult:
    """Validate agent configurations."""
    return validator_registry.validate_scenario('agent_configuration', {'agents': agents})


def validate_tasks(tasks: List[Dict[str, Any]]) -> ScenarioValidationResult:
    """Validate task requests."""
    return validator_registry.validate_scenario('task_request', {'tasks': tasks})


def validate_conflicts(conflicts: List[Dict[str, Any]]) -> ScenarioValidationResult:
    """Validate conflict scenarios."""
    return validator_registry.validate_scenario('conflict_scenario', {'conflicts': conflicts})


def validate_load_balancing(scenario_data: Dict[str, Any]) -> ScenarioValidationResult:
    """Validate load balancing scenario."""
    return validator_registry.validate_scenario('load_balancing_scenario', scenario_data)


def validate_communication(scenario_data: Dict[str, Any]) -> ScenarioValidationResult:
    """Validate communication scenario."""
    return validator_registry.validate_scenario('communication_scenario', scenario_data)


# Utility functions
def format_validation_report(result: ScenarioValidationResult) -> str:
    """Format validation result as human-readable report."""
    lines = [
        f"Scenario Validation Report: {result.scenario_name}",
        f"Result: {result.result.value.upper()}",
        f"Execution Time: {result.execution_time:.3f}s",
        ""
    ]
    
    if result.errors:
        lines.append(f"Errors ({len(result.errors)}):")
        for error in result.errors:
            lines.append(f"  - {error.field}: {error.message}")
            lines.append(f"    Expected: {error.expected}")
            lines.append(f"    Actual: {error.actual}")
        lines.append("")
    
    if result.warnings:
        lines.append(f"Warnings ({len(result.warnings)}):")
        for warning in result.warnings:
            lines.append(f"  - {warning.field}: {warning.message}")
        lines.append("")
    
    if result.metadata:
        lines.append("Metadata:")
        for key, value in result.metadata.items():
            lines.append(f"  {key}: {value}")
    
    return "\n".join(lines)


def validate_scenario_batch(scenarios: List[Tuple[str, Dict[str, Any]]]) -> List[ScenarioValidationResult]:
    """Validate multiple scenarios in batch."""
    results = []
    for scenario_type, scenario_data in scenarios:
        result = validator_registry.validate_scenario(scenario_type, scenario_data)
        results.append(result)
    return results


def get_validation_summary(results: List[ScenarioValidationResult]) -> Dict[str, Any]:
    """Get summary of validation results."""
    total = len(results)
    passed = sum(1 for r in results if r.result == ValidationResult.PASS)
    failed = sum(1 for r in results if r.result == ValidationResult.FAIL)
    warnings = sum(len(r.warnings) for r in results)
    errors = sum(len(r.errors) for r in results)
    
    return {
        "total_scenarios": total,
        "passed": passed,
        "failed": failed,
        "success_rate": (passed / total * 100) if total > 0 else 0,
        "total_warnings": warnings,
        "total_errors": errors,
        "avg_execution_time": sum(r.execution_time for r in results) / total if total > 0 else 0
    }