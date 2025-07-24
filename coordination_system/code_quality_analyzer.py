#!/usr/bin/env python3
"""
Code Quality Analyzer - Advanced technical debt detection and code quality metrics
"""

import os
import ast
import re
import json
from typing import Dict, List, Optional, Any, Tuple, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from datetime import datetime
import tokenize
import io

@dataclass
class CodeMetrics:
    file_path: str
    lines_of_code: int
    cyclomatic_complexity: int
    function_count: int
    class_count: int
    average_function_length: float
    max_function_length: int
    duplicate_code_blocks: int
    comment_ratio: float
    import_count: int
    global_variable_count: int
    nested_depth_max: int
    coupling_score: float

@dataclass
class TechnicalDebt:
    category: str  # complexity, duplication, standards, architecture, test
    severity: str  # critical, high, medium, low
    file_path: str
    line_range: Tuple[int, int]
    description: str
    estimated_hours: int
    impact: str
    recommendation: str
    code_snippet: str
    metrics: Dict[str, Any]

@dataclass
class QualityReport:
    overall_score: float  # 0-100
    total_debt_hours: int
    debt_by_category: Dict[str, int]
    debt_by_severity: Dict[str, int]
    hotspot_files: List[str]  # Files with most issues
    improvement_recommendations: List[str]
    metrics_summary: Dict[str, Any]

class CodeQualityAnalyzer:
    def __init__(self):
        self.complexity_thresholds = {
            'function_complexity': 10,
            'function_length': 50,
            'class_length': 300,
            'file_length': 500,
            'nested_depth': 4,
            'parameter_count': 5
        }
        self.quality_weights = {
            'complexity': 0.3,
            'duplication': 0.2,
            'standards': 0.2,
            'test_coverage': 0.2,
            'documentation': 0.1
        }
        
    def analyze_code_quality(self, project_path: str) -> Tuple[List[TechnicalDebt], QualityReport]:
        """Perform comprehensive code quality analysis"""
        project_path = Path(project_path)
        
        technical_debts = []
        file_metrics = []
        
        # Analyze each source file
        source_files = self._get_source_files(project_path)
        
        for file_path in source_files:
            try:
                # Analyze file metrics
                metrics = self._analyze_file_metrics(project_path / file_path)
                file_metrics.append(metrics)
                
                # Detect technical debt
                debts = self._detect_technical_debt(project_path / file_path, metrics)
                technical_debts.extend(debts)
                
            except Exception as e:
                print(f"Warning: Error analyzing {file_path}: {e}")
                continue
        
        # Analyze cross-file issues
        cross_file_debts = self._analyze_cross_file_issues(project_path, file_metrics)
        technical_debts.extend(cross_file_debts)
        
        # Generate quality report
        report = self._generate_quality_report(technical_debts, file_metrics)
        
        return technical_debts, report
    
    def _get_source_files(self, project_path: Path) -> List[str]:
        """Get all source files in the project"""
        source_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs'}
        source_files = []
        
        for root, dirs, files in os.walk(project_path):
            # Skip common ignored directories
            dirs[:] = [d for d in dirs if d not in {
                '.git', 'node_modules', '__pycache__', '.pytest_cache',
                'venv', 'env', '.env', 'dist', 'build', '.next',
                'target', 'bin', 'obj', 'coverage', '.coverage'
            }]
            
            for file in files:
                if any(file.endswith(ext) for ext in source_extensions):
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(project_path)
                    source_files.append(str(relative_path))
        
        return source_files
    
    def _analyze_file_metrics(self, file_path: Path) -> CodeMetrics:
        """Analyze metrics for a single file"""
        if file_path.suffix == '.py':
            return self._analyze_python_file(file_path)
        elif file_path.suffix in ['.js', '.jsx', '.ts', '.tsx']:
            return self._analyze_javascript_file(file_path)
        else:
            return self._analyze_generic_file(file_path)
    
    def _analyze_python_file(self, file_path: Path) -> CodeMetrics:
        """Analyze Python file metrics using AST"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Fallback to basic analysis if parsing fails
            return self._analyze_generic_file(file_path)
        
        # Calculate metrics
        analyzer = PythonCodeAnalyzer()
        analyzer.visit(tree)
        
        # Count actual lines of code (non-empty, non-comment)
        loc = 0
        comment_lines = 0
        for line in lines:
            stripped = line.strip()
            if stripped:
                if stripped.startswith('#'):
                    comment_lines += 1
                else:
                    loc += 1
        
        # Calculate average function length
        avg_func_length = (
            analyzer.total_function_lines / analyzer.function_count 
            if analyzer.function_count > 0 else 0
        )
        
        return CodeMetrics(
            file_path=str(file_path),
            lines_of_code=loc,
            cyclomatic_complexity=analyzer.total_complexity,
            function_count=analyzer.function_count,
            class_count=analyzer.class_count,
            average_function_length=avg_func_length,
            max_function_length=analyzer.max_function_length,
            duplicate_code_blocks=0,  # Will be calculated separately
            comment_ratio=comment_lines / len(lines) if lines else 0,
            import_count=analyzer.import_count,
            global_variable_count=analyzer.global_var_count,
            nested_depth_max=analyzer.max_nested_depth,
            coupling_score=analyzer.coupling_score
        )
    
    def _analyze_javascript_file(self, file_path: Path) -> CodeMetrics:
        """Analyze JavaScript/TypeScript file metrics"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
        
        # Basic JavaScript analysis
        loc = 0
        comment_lines = 0
        function_count = 0
        class_count = 0
        import_count = 0
        
        in_multiline_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            # Handle multi-line comments
            if '/*' in stripped:
                in_multiline_comment = True
            if '*/' in stripped:
                in_multiline_comment = False
                comment_lines += 1
                continue
                
            if in_multiline_comment:
                comment_lines += 1
                continue
            
            if stripped:
                if stripped.startswith('//'):
                    comment_lines += 1
                else:
                    loc += 1
                    
                    # Count functions and classes
                    if re.match(r'(function\s+\w+|const\s+\w+\s*=\s*\(|let\s+\w+\s*=\s*\(|var\s+\w+\s*=\s*\()', stripped):
                        function_count += 1
                    elif re.match(r'class\s+\w+', stripped):
                        class_count += 1
                    elif stripped.startswith('import ') or stripped.startswith('const ') and 'require(' in stripped:
                        import_count += 1
        
        # Estimate complexity based on control flow keywords
        complexity = len(re.findall(r'\b(if|else|for|while|switch|case|catch)\b', content))
        
        return CodeMetrics(
            file_path=str(file_path),
            lines_of_code=loc,
            cyclomatic_complexity=complexity,
            function_count=function_count,
            class_count=class_count,
            average_function_length=loc / function_count if function_count > 0 else loc,
            max_function_length=0,  # Would need more sophisticated parsing
            duplicate_code_blocks=0,
            comment_ratio=comment_lines / len(lines) if lines else 0,
            import_count=import_count,
            global_variable_count=0,  # Would need more sophisticated parsing
            nested_depth_max=0,  # Would need more sophisticated parsing
            coupling_score=import_count * 0.1  # Simple estimation
        )
    
    def _analyze_generic_file(self, file_path: Path) -> CodeMetrics:
        """Basic analysis for other file types"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        loc = sum(1 for line in lines if line.strip())
        
        return CodeMetrics(
            file_path=str(file_path),
            lines_of_code=loc,
            cyclomatic_complexity=0,
            function_count=0,
            class_count=0,
            average_function_length=0,
            max_function_length=0,
            duplicate_code_blocks=0,
            comment_ratio=0,
            import_count=0,
            global_variable_count=0,
            nested_depth_max=0,
            coupling_score=0
        )
    
    def _detect_technical_debt(self, file_path: Path, metrics: CodeMetrics) -> List[TechnicalDebt]:
        """Detect technical debt in a file based on metrics"""
        debts = []
        
        # High complexity
        if metrics.cyclomatic_complexity > self.complexity_thresholds['function_complexity'] * metrics.function_count:
            debts.append(TechnicalDebt(
                category="complexity",
                severity="high" if metrics.cyclomatic_complexity > 50 else "medium",
                file_path=str(file_path),
                line_range=(0, metrics.lines_of_code),
                description=f"High overall complexity (score: {metrics.cyclomatic_complexity})",
                estimated_hours=8,
                impact="Difficult to understand and maintain, higher bug probability",
                recommendation="Refactor complex functions, extract methods, simplify logic",
                code_snippet="",
                metrics={"complexity": metrics.cyclomatic_complexity}
            ))
        
        # Long functions
        if metrics.max_function_length > self.complexity_thresholds['function_length']:
            debts.append(TechnicalDebt(
                category="complexity",
                severity="medium",
                file_path=str(file_path),
                line_range=(0, 0),  # Would need function location
                description=f"Functions too long (max: {metrics.max_function_length} lines)",
                estimated_hours=4,
                impact="Hard to test and understand, violates single responsibility",
                recommendation="Break down into smaller, focused functions",
                code_snippet="",
                metrics={"max_length": metrics.max_function_length}
            ))
        
        # Large files
        if metrics.lines_of_code > self.complexity_thresholds['file_length']:
            debts.append(TechnicalDebt(
                category="architecture",
                severity="medium",
                file_path=str(file_path),
                line_range=(0, metrics.lines_of_code),
                description=f"File too large ({metrics.lines_of_code} lines)",
                estimated_hours=8,
                impact="Difficult navigation, potential god object anti-pattern",
                recommendation="Split into multiple focused modules",
                code_snippet="",
                metrics={"lines": metrics.lines_of_code}
            ))
        
        # Low documentation
        if metrics.comment_ratio < 0.1 and metrics.lines_of_code > 100:
            debts.append(TechnicalDebt(
                category="standards",
                severity="low",
                file_path=str(file_path),
                line_range=(0, metrics.lines_of_code),
                description=f"Low documentation ({metrics.comment_ratio:.1%} comments)",
                estimated_hours=2,
                impact="Difficult onboarding, knowledge loss risk",
                recommendation="Add docstrings and inline comments for complex logic",
                code_snippet="",
                metrics={"comment_ratio": metrics.comment_ratio}
            ))
        
        # High coupling
        if metrics.coupling_score > 0.8:
            debts.append(TechnicalDebt(
                category="architecture",
                severity="medium",
                file_path=str(file_path),
                line_range=(0, 0),
                description=f"High coupling (score: {metrics.coupling_score:.2f})",
                estimated_hours=12,
                impact="Difficult to test in isolation, brittle to changes",
                recommendation="Reduce dependencies, use dependency injection",
                code_snippet="",
                metrics={"coupling": metrics.coupling_score}
            ))
        
        # Deep nesting
        if metrics.nested_depth_max > self.complexity_thresholds['nested_depth']:
            debts.append(TechnicalDebt(
                category="complexity",
                severity="medium",
                file_path=str(file_path),
                line_range=(0, 0),
                description=f"Deep nesting detected (max depth: {metrics.nested_depth_max})",
                estimated_hours=4,
                impact="Hard to follow control flow, increased cognitive load",
                recommendation="Extract nested logic, use early returns, simplify conditions",
                code_snippet="",
                metrics={"max_depth": metrics.nested_depth_max}
            ))
        
        return debts
    
    def _analyze_cross_file_issues(self, project_path: Path, file_metrics: List[CodeMetrics]) -> List[TechnicalDebt]:
        """Analyze issues that span multiple files"""
        debts = []
        
        # Detect code duplication across files
        duplication_map = self._detect_code_duplication(project_path, file_metrics)
        for dup_info in duplication_map:
            debts.append(TechnicalDebt(
                category="duplication",
                severity="medium" if dup_info['lines'] > 20 else "low",
                file_path=dup_info['files'][0],
                line_range=(dup_info['start_line'], dup_info['end_line']),
                description=f"Duplicate code found in {len(dup_info['files'])} files",
                estimated_hours=2 * len(dup_info['files']),
                impact="Maintenance overhead, inconsistent bug fixes",
                recommendation="Extract to shared module or base class",
                code_snippet=dup_info['snippet'][:200] + "...",
                metrics={"files": dup_info['files'], "lines": dup_info['lines']}
            ))
        
        # Detect circular dependencies
        circular_deps = self._detect_circular_dependencies(project_path, file_metrics)
        for cycle in circular_deps:
            debts.append(TechnicalDebt(
                category="architecture",
                severity="high",
                file_path=cycle[0],
                line_range=(0, 0),
                description=f"Circular dependency: {' -> '.join(cycle)} -> {cycle[0]}",
                estimated_hours=8,
                impact="Tight coupling, difficult refactoring, potential runtime issues",
                recommendation="Introduce abstraction layer or reorganize module structure",
                code_snippet="",
                metrics={"cycle": cycle}
            ))
        
        # Detect god objects/modules
        god_objects = self._detect_god_objects(file_metrics)
        for god_file in god_objects:
            debts.append(TechnicalDebt(
                category="architecture",
                severity="high",
                file_path=god_file['file'],
                line_range=(0, god_file['metrics'].lines_of_code),
                description=f"God object detected: {god_file['issues']}",
                estimated_hours=16,
                impact="Violates single responsibility, difficult to maintain and test",
                recommendation="Break down into smaller, focused modules",
                code_snippet="",
                metrics=god_file['stats']
            ))
        
        return debts
    
    def _detect_code_duplication(self, project_path: Path, file_metrics: List[CodeMetrics]) -> List[Dict[str, Any]]:
        """Detect duplicate code blocks across files"""
        duplications = []
        
        # Simple approach: hash code blocks and find duplicates
        # In production, would use more sophisticated algorithms like suffix trees
        
        block_hashes = defaultdict(list)
        min_block_size = 10  # Minimum lines for duplication detection
        
        for metrics in file_metrics:
            try:
                file_path = project_path / metrics.file_path
                if not file_path.exists():
                    continue
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Create sliding window of code blocks
                for i in range(len(lines) - min_block_size):
                    block = lines[i:i + min_block_size]
                    # Normalize whitespace and strip comments for comparison
                    normalized = [self._normalize_code_line(line) for line in block]
                    block_hash = hash(tuple(normalized))
                    
                    block_hashes[block_hash].append({
                        'file': metrics.file_path,
                        'start_line': i + 1,
                        'end_line': i + min_block_size,
                        'snippet': ''.join(block[:5])  # First 5 lines as snippet
                    })
            except Exception:
                continue
        
        # Find actual duplicates
        for block_hash, locations in block_hashes.items():
            if len(locations) > 1:
                duplications.append({
                    'files': [loc['file'] for loc in locations],
                    'start_line': locations[0]['start_line'],
                    'end_line': locations[0]['end_line'],
                    'lines': min_block_size,
                    'snippet': locations[0]['snippet']
                })
        
        return duplications[:10]  # Limit to top 10 duplications
    
    def _normalize_code_line(self, line: str) -> str:
        """Normalize a code line for duplication detection"""
        # Remove comments and extra whitespace
        line = re.sub(r'#.*$', '', line)  # Python comments
        line = re.sub(r'//.*$', '', line)  # JS comments
        line = re.sub(r'\s+', ' ', line)  # Normalize whitespace
        return line.strip()
    
    def _detect_circular_dependencies(self, project_path: Path, file_metrics: List[CodeMetrics]) -> List[List[str]]:
        """Detect circular import dependencies"""
        import_graph = defaultdict(set)
        
        # Build import graph
        for metrics in file_metrics:
            file_path = project_path / metrics.file_path
            if not file_path.exists():
                continue
                
            imports = self._extract_imports(file_path)
            for imp in imports:
                # Resolve relative imports to file paths
                resolved = self._resolve_import(imp, metrics.file_path, project_path)
                if resolved:
                    import_graph[metrics.file_path].add(resolved)
        
        # Find cycles using DFS
        cycles = []
        visited = set()
        rec_stack = set()
        
        def find_cycles(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in import_graph.get(node, []):
                if neighbor not in visited:
                    cycle = find_cycles(neighbor, path[:])
                    if cycle:
                        cycles.append(cycle)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:]
            
            rec_stack.remove(node)
            return None
        
        for node in import_graph:
            if node not in visited:
                find_cycles(node, [])
        
        return cycles[:5]  # Limit to first 5 cycles
    
    def _extract_imports(self, file_path: Path) -> List[str]:
        """Extract import statements from a file"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if file_path.suffix == '.py':
                # Python imports
                import_pattern = r'(?:from\s+([\w.]+)\s+)?import\s+'
                imports.extend(re.findall(import_pattern, content))
            elif file_path.suffix in ['.js', '.jsx', '.ts', '.tsx']:
                # JavaScript imports
                import_pattern = r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]'
                imports.extend(re.findall(import_pattern, content))
                # Also handle require
                require_pattern = r'require\([\'"](.+?)[\'"]\)'
                imports.extend(re.findall(require_pattern, content))
        except Exception:
            pass
        
        return [imp for imp in imports if imp]
    
    def _resolve_import(self, import_path: str, current_file: str, project_path: Path) -> Optional[str]:
        """Resolve an import path to a file path"""
        # Simplified import resolution
        # In production, would need full module resolution logic
        
        if import_path.startswith('.'):
            # Relative import
            current_dir = Path(current_file).parent
            resolved = (current_dir / import_path).resolve()
            try:
                relative = resolved.relative_to(project_path)
                return str(relative)
            except ValueError:
                return None
        else:
            # Absolute import - would need more sophisticated resolution
            return None
    
    def _detect_god_objects(self, file_metrics: List[CodeMetrics]) -> List[Dict[str, Any]]:
        """Detect god objects/modules with too many responsibilities"""
        god_objects = []
        
        for metrics in file_metrics:
            issues = []
            stats = {}
            
            # Check multiple metrics
            if metrics.class_count > 5:
                issues.append(f"{metrics.class_count} classes")
                stats['classes'] = metrics.class_count
                
            if metrics.function_count > 20:
                issues.append(f"{metrics.function_count} functions")
                stats['functions'] = metrics.function_count
                
            if metrics.lines_of_code > 500:
                issues.append(f"{metrics.lines_of_code} lines")
                stats['lines'] = metrics.lines_of_code
                
            if metrics.import_count > 15:
                issues.append(f"{metrics.import_count} imports")
                stats['imports'] = metrics.import_count
            
            # If multiple issues, it's likely a god object
            if len(issues) >= 3:
                god_objects.append({
                    'file': metrics.file_path,
                    'metrics': metrics,
                    'issues': ', '.join(issues),
                    'stats': stats
                })
        
        return sorted(god_objects, key=lambda x: x['metrics'].lines_of_code, reverse=True)[:5]
    
    def _generate_quality_report(self, technical_debts: List[TechnicalDebt], 
                               file_metrics: List[CodeMetrics]) -> QualityReport:
        """Generate comprehensive quality report"""
        # Calculate debt summaries
        debt_by_category = defaultdict(int)
        debt_by_severity = defaultdict(int)
        total_debt_hours = 0
        
        for debt in technical_debts:
            debt_by_category[debt.category] += 1
            debt_by_severity[debt.severity] += 1
            total_debt_hours += debt.estimated_hours
        
        # Find hotspot files (files with most issues)
        file_issue_count = Counter(debt.file_path for debt in technical_debts)
        hotspot_files = [file for file, _ in file_issue_count.most_common(5)]
        
        # Calculate overall quality score
        quality_score = self._calculate_quality_score(technical_debts, file_metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(technical_debts, file_metrics)
        
        # Create metrics summary
        metrics_summary = {
            'total_files': len(file_metrics),
            'total_lines': sum(m.lines_of_code for m in file_metrics),
            'average_complexity': sum(m.cyclomatic_complexity for m in file_metrics) / len(file_metrics) if file_metrics else 0,
            'average_file_size': sum(m.lines_of_code for m in file_metrics) / len(file_metrics) if file_metrics else 0,
            'total_functions': sum(m.function_count for m in file_metrics),
            'total_classes': sum(m.class_count for m in file_metrics)
        }
        
        return QualityReport(
            overall_score=quality_score,
            total_debt_hours=total_debt_hours,
            debt_by_category=dict(debt_by_category),
            debt_by_severity=dict(debt_by_severity),
            hotspot_files=hotspot_files,
            improvement_recommendations=recommendations,
            metrics_summary=metrics_summary
        )
    
    def _calculate_quality_score(self, technical_debts: List[TechnicalDebt], 
                               file_metrics: List[CodeMetrics]) -> float:
        """Calculate overall quality score (0-100)"""
        if not file_metrics:
            return 0.0
        
        # Start with perfect score
        score = 100.0
        
        # Deduct points for technical debt
        severity_penalties = {
            'critical': 5,
            'high': 3,
            'medium': 1.5,
            'low': 0.5
        }
        
        for debt in technical_debts:
            score -= severity_penalties.get(debt.severity, 1)
        
        # Factor in complexity
        avg_complexity = sum(m.cyclomatic_complexity for m in file_metrics) / len(file_metrics)
        if avg_complexity > 20:
            score -= 10
        elif avg_complexity > 10:
            score -= 5
        
        # Factor in file sizes
        large_files = sum(1 for m in file_metrics if m.lines_of_code > 500)
        score -= large_files * 2
        
        # Factor in documentation
        avg_comment_ratio = sum(m.comment_ratio for m in file_metrics) / len(file_metrics)
        if avg_comment_ratio < 0.05:
            score -= 10
        elif avg_comment_ratio < 0.1:
            score -= 5
        
        return max(0.0, min(100.0, score))
    
    def _generate_recommendations(self, technical_debts: List[TechnicalDebt], 
                                file_metrics: List[CodeMetrics]) -> List[str]:
        """Generate prioritized improvement recommendations"""
        recommendations = []
        
        # Group debts by category
        category_counts = Counter(debt.category for debt in technical_debts)
        
        # Priority recommendations based on most common issues
        if category_counts.get('complexity', 0) > 5:
            recommendations.append("Focus on reducing code complexity through refactoring and method extraction")
        
        if category_counts.get('duplication', 0) > 3:
            recommendations.append("Eliminate code duplication by creating shared modules and utilities")
        
        if category_counts.get('architecture', 0) > 3:
            recommendations.append("Review and improve module architecture to reduce coupling and god objects")
        
        if category_counts.get('standards', 0) > 5:
            recommendations.append("Implement and enforce coding standards with linting and pre-commit hooks")
        
        # Check for critical issues
        critical_count = sum(1 for debt in technical_debts if debt.severity == 'critical')
        if critical_count > 0:
            recommendations.insert(0, f"Address {critical_count} critical issues immediately")
        
        # Check test coverage (would need actual test metrics)
        if any('test' in debt.category for debt in technical_debts):
            recommendations.append("Improve test coverage and implement test-driven development practices")
        
        # Documentation recommendations
        avg_comment_ratio = sum(m.comment_ratio for m in file_metrics) / len(file_metrics) if file_metrics else 0
        if avg_comment_ratio < 0.1:
            recommendations.append("Add comprehensive documentation and inline comments")
        
        return recommendations[:7]  # Top 7 recommendations


class PythonCodeAnalyzer(ast.NodeVisitor):
    """AST visitor for analyzing Python code metrics"""
    
    def __init__(self):
        self.function_count = 0
        self.class_count = 0
        self.total_complexity = 0
        self.max_function_length = 0
        self.total_function_lines = 0
        self.import_count = 0
        self.global_var_count = 0
        self.max_nested_depth = 0
        self.current_depth = 0
        self.coupling_score = 0.0
        
    def visit_FunctionDef(self, node):
        self.function_count += 1
        
        # Calculate function length
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            func_length = node.end_lineno - node.lineno
            self.max_function_length = max(self.max_function_length, func_length)
            self.total_function_lines += func_length
        
        # Calculate complexity
        self.total_complexity += self._calculate_complexity(node)
        
        # Track nesting depth
        self.current_depth += 1
        self.max_nested_depth = max(self.max_nested_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1
        
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)
        
    def visit_ClassDef(self, node):
        self.class_count += 1
        self.generic_visit(node)
        
    def visit_Import(self, node):
        self.import_count += len(node.names)
        self.coupling_score += 0.1 * len(node.names)
        
    def visit_ImportFrom(self, node):
        self.import_count += len(node.names)
        self.coupling_score += 0.1 * len(node.names)
        
    def visit_Assign(self, node):
        # Count global variables (assignments at module level)
        if isinstance(node.targets[0], ast.Name) and self.current_depth == 0:
            self.global_var_count += 1
        self.generic_visit(node)
        
    def _calculate_complexity(self, node):
        """Calculate cyclomatic complexity of a node"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Each 'and' or 'or' adds complexity
                complexity += len(child.values) - 1
        
        return complexity


def main():
    """Command-line interface for code quality analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze code quality and technical debt")
    parser.add_argument("project_path", help="Path to project directory")
    parser.add_argument("--output", "-o", help="Output file for analysis results")
    parser.add_argument("--format", choices=["json", "report"], default="report", help="Output format")
    parser.add_argument("--threshold", type=float, default=70.0, help="Quality score threshold")
    
    args = parser.parse_args()
    
    analyzer = CodeQualityAnalyzer()
    
    try:
        technical_debts, report = analyzer.analyze_code_quality(args.project_path)
        
        if args.format == "json":
            output_data = {
                "quality_score": report.overall_score,
                "total_debt_hours": report.total_debt_hours,
                "technical_debts": [asdict(debt) for debt in technical_debts],
                "report": asdict(report)
            }
            output_str = json.dumps(output_data, indent=2, default=str)
        else:
            # Generate human-readable report
            output_str = f"""
# Code Quality Analysis Report

**Project**: {args.project_path}
**Analysis Date**: {datetime.now().isoformat()}

## Overall Quality Score: {report.overall_score:.1f}/100

**Status**: {"✅ PASS" if report.overall_score >= args.threshold else "❌ FAIL"} (Threshold: {args.threshold})

## Technical Debt Summary
- **Total Debt**: {report.total_debt_hours} hours
- **Critical Issues**: {report.debt_by_severity.get('critical', 0)}
- **High Priority**: {report.debt_by_severity.get('high', 0)}
- **Medium Priority**: {report.debt_by_severity.get('medium', 0)}
- **Low Priority**: {report.debt_by_severity.get('low', 0)}

## Debt by Category
"""
            for category, count in sorted(report.debt_by_category.items(), key=lambda x: x[1], reverse=True):
                output_str += f"- **{category.title()}**: {count} issues\n"
            
            output_str += f"""
## Hotspot Files
These files have the most quality issues:
"""
            for i, file in enumerate(report.hotspot_files, 1):
                issue_count = sum(1 for debt in technical_debts if debt.file_path == file)
                output_str += f"{i}. `{file}` ({issue_count} issues)\n"
            
            output_str += f"""
## Metrics Summary
- **Total Files**: {report.metrics_summary['total_files']}
- **Total Lines**: {report.metrics_summary['total_lines']:,}
- **Average Complexity**: {report.metrics_summary['average_complexity']:.1f}
- **Average File Size**: {report.metrics_summary['average_file_size']:.0f} lines
- **Total Functions**: {report.metrics_summary['total_functions']}
- **Total Classes**: {report.metrics_summary['total_classes']}

## Top Recommendations
"""
            for i, rec in enumerate(report.improvement_recommendations, 1):
                output_str += f"{i}. {rec}\n"
            
            # Add top 10 technical debt items
            output_str += """
## Top Technical Debt Items
"""
            sorted_debts = sorted(technical_debts, 
                                key=lambda x: {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}[x.severity], 
                                reverse=True)
            
            for i, debt in enumerate(sorted_debts[:10], 1):
                output_str += f"""
### {i}. {debt.description}
- **File**: `{debt.file_path}`
- **Category**: {debt.category.title()}
- **Severity**: {debt.severity.upper()}
- **Estimated Hours**: {debt.estimated_hours}
- **Impact**: {debt.impact}
- **Recommendation**: {debt.recommendation}
"""
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_str)
            print(f"Analysis written to {args.output}")
        else:
            print(output_str)
            
    except Exception as e:
        print(f"Error analyzing code quality: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())