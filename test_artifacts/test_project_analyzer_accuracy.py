#!/usr/bin/env python3
"""
TDD Test Suite for Project Analysis Accuracy
Tests the accuracy of project type detection, technology detection, and workflow matching
"""

import pytest
import tempfile
import shutil
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import asdict

from coordination_system.project_analyzer import ProjectAnalyzer, ProjectType, TechnologyStack, AnalysisResult


class TestProjectGenerator:
    """Utility class to generate test project structures"""
    
    @staticmethod
    def create_react_webapp(base_path: Path):
        """Create a React web application structure"""
        # Package.json with React dependencies
        (base_path / "package.json").write_text(json.dumps({
            "name": "react-app",
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build"
            }
        }, indent=2))
        
        # React structure
        (base_path / "public").mkdir()
        (base_path / "public" / "index.html").write_text("""
        <!DOCTYPE html>
        <html>
        <head><title>React App</title></head>
        <body><div id="root"></div></body>
        </html>
        """)
        
        (base_path / "src").mkdir()
        (base_path / "src" / "index.js").write_text("""
        import React from 'react';
        import ReactDOM from 'react-dom';
        import App from './App';
        
        ReactDOM.render(<App />, document.getElementById('root'));
        """)
        
        (base_path / "src" / "App.js").write_text("""
        import React from 'react';
        
        function App() {
          return <div>Hello React!</div>;
        }
        
        export default App;
        """)
        
        return {"expected_type": ProjectType.WEB_APP, "expected_frameworks": ["react"]}
    
    @staticmethod
    def create_python_api(base_path: Path):
        """Create a Python API service structure"""
        # Requirements file
        (base_path / "requirements.txt").write_text("""
        fastapi==0.68.0
        uvicorn==0.15.0
        pydantic==1.8.2
        sqlalchemy==1.4.23
        """)
        
        # API structure
        (base_path / "app.py").write_text("""
        from fastapi import FastAPI
        from pydantic import BaseModel
        
        app = FastAPI()
        
        class Item(BaseModel):
            name: str
            price: float
        
        @app.get("/")
        async def root():
            return {"message": "Hello API"}
        
        @app.post("/items/")
        async def create_item(item: Item):
            return item
        """)
        
        (base_path / "models.py").write_text("""
        from sqlalchemy import Column, Integer, String, Float
        from sqlalchemy.ext.declarative import declarative_base
        
        Base = declarative_base()
        
        class Item(Base):
            __tablename__ = "items"
            id = Column(Integer, primary_key=True)
            name = Column(String)
            price = Column(Float)
        """)
        
        return {"expected_type": ProjectType.API_SERVICE, "expected_frameworks": ["fastapi"]}
    
    @staticmethod
    def create_ml_project(base_path: Path):
        """Create a machine learning project structure"""
        # Requirements with ML libraries
        (base_path / "requirements.txt").write_text("""
        numpy==1.21.0
        pandas==1.3.0
        scikit-learn==1.0.0
        tensorflow==2.6.0
        jupyter==1.0.0
        matplotlib==3.4.0
        """)
        
        # ML project structure
        (base_path / "data").mkdir()
        (base_path / "data" / "raw").mkdir()
        (base_path / "data" / "processed").mkdir()
        
        (base_path / "models").mkdir()
        (base_path / "notebooks").mkdir()
        
        # Jupyter notebook
        (base_path / "notebooks" / "analysis.ipynb").write_text(json.dumps({
            "cells": [
                {
                    "cell_type": "code",
                    "source": ["import pandas as pd\n", "import numpy as np\n", "from sklearn.model_selection import train_test_split"]
                }
            ],
            "metadata": {"kernelspec": {"name": "python3"}},
            "nbformat": 4
        }))
        
        # Python ML script
        (base_path / "train.py").write_text("""
        import pandas as pd
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        import joblib
        
        def train_model():
            # Load data
            data = pd.read_csv('data/processed/features.csv')
            X, y = data.drop('target', axis=1), data['target']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            
            # Train model
            model = RandomForestClassifier()
            model.fit(X_train, y_train)
            
            # Save model
            joblib.dump(model, 'models/model.pkl')
        
        if __name__ == "__main__":
            train_model()
        """)
        
        return {"expected_type": ProjectType.ML_PROJECT, "expected_frameworks": []}
    
    @staticmethod
    def create_unity_game(base_path: Path):
        """Create a Unity game project structure"""
        # Unity directories
        (base_path / "Assets").mkdir()
        (base_path / "Assets" / "Scripts").mkdir()
        (base_path / "Assets" / "Scenes").mkdir()
        (base_path / "Assets" / "Prefabs").mkdir()
        
        (base_path / "ProjectSettings").mkdir()
        (base_path / "Library").mkdir()
        
        # Unity files
        (base_path / "Assets" / "Scenes" / "MainScene.unity").write_text("Unity scene data")
        (base_path / "Assets" / "Prefabs" / "Player.prefab").write_text("Unity prefab data")
        
        # C# scripts
        (base_path / "Assets" / "Scripts" / "PlayerController.cs").write_text("""
        using UnityEngine;
        
        public class PlayerController : MonoBehaviour
        {
            public float speed = 5.0f;
            
            void Update()
            {
                float horizontal = Input.GetAxis("Horizontal");
                float vertical = Input.GetAxis("Vertical");
                
                Vector3 movement = new Vector3(horizontal, 0, vertical);
                transform.Translate(movement * speed * Time.deltaTime);
            }
        }
        """)
        
        (base_path / "ProjectSettings" / "ProjectSettings.asset").write_text("Unity project settings")
        
        return {"expected_type": ProjectType.GAME_DEV, "expected_frameworks": ["unity"]}
    
    @staticmethod
    def create_blockchain_truffle(base_path: Path):
        """Create a Truffle blockchain project structure"""
        # Truffle structure
        (base_path / "contracts").mkdir()
        (base_path / "migrations").mkdir()
        (base_path / "test").mkdir()
        
        # Truffle config
        (base_path / "truffle-config.js").write_text("""
        module.exports = {
          networks: {
            development: {
              host: "127.0.0.1",
              port: 8545,
              network_id: "*"
            }
          },
          compilers: {
            solc: {
              version: "0.8.0"
            }
          }
        };
        """)
        
        # Smart contract
        (base_path / "contracts" / "Token.sol").write_text("""
        pragma solidity ^0.8.0;
        
        contract Token {
            string public name = "MyToken";
            string public symbol = "MTK";
            uint256 public totalSupply = 1000000;
            
            mapping(address => uint256) public balanceOf;
            
            constructor() {
                balanceOf[msg.sender] = totalSupply;
            }
            
            function transfer(address to, uint256 amount) public returns (bool) {
                require(balanceOf[msg.sender] >= amount, "Insufficient balance");
                balanceOf[msg.sender] -= amount;
                balanceOf[to] += amount;
                return true;
            }
        }
        """)
        
        # Migration
        (base_path / "migrations" / "1_initial_migration.js").write_text("""
        const Token = artifacts.require("Token");
        
        module.exports = function (deployer) {
          deployer.deploy(Token);
        };
        """)
        
        return {"expected_type": ProjectType.BLOCKCHAIN, "expected_frameworks": ["truffle"]}
    
    @staticmethod
    def create_cli_tool(base_path: Path):
        """Create a CLI tool project structure"""
        # Python CLI tool
        (base_path / "setup.py").write_text("""
        from setuptools import setup, find_packages
        
        setup(
            name="mycli",
            version="1.0.0",
            packages=find_packages(),
            entry_points={
                'console_scripts': [
                    'mycli=mycli.main:main',
                ],
            },
        )
        """)
        
        (base_path / "mycli").mkdir()
        (base_path / "mycli" / "__init__.py").write_text("")
        (base_path / "mycli" / "main.py").write_text("""
        import argparse
        import sys
        
        def main():
            parser = argparse.ArgumentParser(description='My CLI tool')
            parser.add_argument('--verbose', '-v', action='store_true')
            parser.add_argument('command', help='Command to run')
            
            args = parser.parse_args()
            
            if args.command == 'status':
                print("Status: OK")
            elif args.command == 'version':
                print("Version: 1.0.0")
            else:
                print(f"Unknown command: {args.command}")
                sys.exit(1)
        
        if __name__ == "__main__":
            main()
        """)
        
        (base_path / "README.md").write_text("""
        # My CLI Tool
        
        A command-line tool for doing things.
        
        ## Usage
        
        ```bash
        mycli status
        mycli version
        ```
        """)
        
        return {"expected_type": ProjectType.CLI_TOOL, "expected_frameworks": []}


@pytest.fixture
def analyzer():
    """Fixture providing a ProjectAnalyzer instance"""
    return ProjectAnalyzer()


@pytest.fixture
def test_projects():
    """Fixture providing temporary test project structures"""
    projects = {}
    temp_dirs = []
    
    generators = [
        ("react_webapp", TestProjectGenerator.create_react_webapp),
        ("python_api", TestProjectGenerator.create_python_api),
        ("ml_project", TestProjectGenerator.create_ml_project),
        ("unity_game", TestProjectGenerator.create_unity_game),
        ("blockchain_truffle", TestProjectGenerator.create_blockchain_truffle),
        ("cli_tool", TestProjectGenerator.create_cli_tool),
    ]
    
    for name, generator in generators:
        temp_dir = tempfile.mkdtemp()
        temp_dirs.append(temp_dir)
        project_path = Path(temp_dir)
        
        expected = generator(project_path)
        projects[name] = {
            "path": str(project_path),
            "expected_type": expected["expected_type"],
            "expected_frameworks": expected["expected_frameworks"]
        }
    
    yield projects
    
    # Cleanup
    for temp_dir in temp_dirs:
        shutil.rmtree(temp_dir, ignore_errors=True)


class TestProjectAnalysisAccuracy:
    """Test suite for project analysis accuracy"""
    
    def test_project_type_detection_accuracy(self, analyzer, test_projects):
        """Test accuracy of project type detection"""
        results = {}
        correct_predictions = 0
        total_predictions = len(test_projects)
        
        for project_name, project_info in test_projects.items():
            result = analyzer.analyze_project(project_info["path"])
            
            is_correct = result.project_type == project_info["expected_type"]
            if is_correct:
                correct_predictions += 1
            
            results[project_name] = {
                "expected": project_info["expected_type"],
                "predicted": result.project_type,
                "confidence": result.confidence,
                "correct": is_correct
            }
        
        accuracy = correct_predictions / total_predictions
        
        # Print detailed results
        print(f"\n=== Project Type Detection Accuracy: {accuracy:.2%} ===")
        for project_name, result in results.items():
            status = "✅" if result["correct"] else "❌"
            print(f"{status} {project_name}: {result['expected']} -> {result['predicted']} (conf: {result['confidence']:.2f})")
        
        # Assert minimum accuracy threshold
        assert accuracy >= 0.8, f"Project type detection accuracy {accuracy:.2%} below 80% threshold"
    
    def test_framework_detection_accuracy(self, analyzer, test_projects):
        """Test accuracy of framework detection"""
        results = {}
        framework_correct = 0
        framework_total = 0
        
        for project_name, project_info in test_projects.items():
            result = analyzer.analyze_project(project_info["path"])
            expected_frameworks = set(project_info["expected_frameworks"])
            detected_frameworks = set(result.tech_stack.frameworks)
            
            # Calculate precision and recall for frameworks
            if expected_frameworks or detected_frameworks:
                framework_total += 1
                
                if expected_frameworks == detected_frameworks:
                    framework_correct += 1
                    match_status = "✅ Exact Match"
                elif expected_frameworks.intersection(detected_frameworks):
                    match_status = "🔶 Partial Match"
                else:
                    match_status = "❌ No Match"
                
                results[project_name] = {
                    "expected": list(expected_frameworks),
                    "detected": list(detected_frameworks),
                    "status": match_status
                }
        
        framework_accuracy = framework_correct / framework_total if framework_total > 0 else 0
        
        print(f"\n=== Framework Detection Accuracy: {framework_accuracy:.2%} ===")
        for project_name, result in results.items():
            print(f"{result['status']} {project_name}: {result['expected']} -> {result['detected']}")
        
        # Assert minimum framework detection accuracy
        assert framework_accuracy >= 0.7, f"Framework detection accuracy {framework_accuracy:.2%} below 70% threshold"
    
    def test_confidence_scoring_distribution(self, analyzer, test_projects):
        """Test that confidence scores are well-distributed and meaningful"""
        confidences = []
        correct_high_conf = 0
        high_conf_total = 0
        
        for project_name, project_info in test_projects.items():
            result = analyzer.analyze_project(project_info["path"])
            confidences.append(result.confidence)
            
            # Check if high-confidence predictions are more accurate
            if result.confidence >= 0.8:
                high_conf_total += 1
                if result.project_type == project_info["expected_type"]:
                    correct_high_conf += 1
        
        avg_confidence = sum(confidences) / len(confidences)
        min_confidence = min(confidences)
        max_confidence = max(confidences)
        
        high_conf_accuracy = correct_high_conf / high_conf_total if high_conf_total > 0 else 0
        
        print(f"\n=== Confidence Score Analysis ===")
        print(f"Average confidence: {avg_confidence:.2f}")
        print(f"Confidence range: {min_confidence:.2f} - {max_confidence:.2f}")
        print(f"High-confidence predictions (≥0.8): {high_conf_total}")
        print(f"High-confidence accuracy: {high_conf_accuracy:.2%}")
        
        # Assert confidence score quality
        assert 0.0 <= min_confidence <= max_confidence <= 1.0, "Confidence scores out of valid range"
        assert avg_confidence >= 0.5, f"Average confidence {avg_confidence:.2f} too low"
        if high_conf_total > 0:
            assert high_conf_accuracy >= 0.9, f"High-confidence predictions should be >90% accurate, got {high_conf_accuracy:.2%}"
    
    def test_technology_stack_completeness(self, analyzer, test_projects):
        """Test that technology stacks are detected completely"""
        for project_name, project_info in test_projects.items():
            result = analyzer.analyze_project(project_info["path"])
            tech_stack = result.tech_stack
            
            print(f"\n=== {project_name} Technology Stack ===")
            print(f"Languages: {tech_stack.languages}")
            print(f"Frameworks: {tech_stack.frameworks}")
            print(f"Databases: {tech_stack.databases}")
            print(f"Build Tools: {tech_stack.build_tools}")
            
            # Basic assertions
            assert isinstance(tech_stack.languages, list), "Languages should be a list"
            assert isinstance(tech_stack.frameworks, list), "Frameworks should be a list"
            
            # Project-specific assertions
            if project_name == "react_webapp":
                assert "javascript" in tech_stack.languages, "React project should detect JavaScript"
            elif project_name == "python_api":
                assert "python" in tech_stack.languages, "Python API should detect Python"
            elif project_name == "unity_game":
                assert "csharp" in tech_stack.languages, "Unity project should detect C#"
            elif project_name == "blockchain_truffle":
                assert "solidity" in tech_stack.languages, "Blockchain project should detect Solidity"
    
    def test_edge_cases(self, analyzer):
        """Test edge cases and error handling"""
        # Test empty directory
        with tempfile.TemporaryDirectory() as empty_dir:
            result = analyzer.analyze_project(empty_dir)
            assert result.project_type is not None, "Should handle empty directories gracefully"
            assert 0.0 <= result.confidence <= 1.0, "Confidence should be in valid range"
        
        # Test directory with only README
        with tempfile.TemporaryDirectory() as readme_dir:
            Path(readme_dir, "README.md").write_text("# Test Project\nThis is a test.")
            result = analyzer.analyze_project(readme_dir)
            assert result.project_type is not None, "Should handle README-only directories"
        
        # Test mixed project (both web and API indicators)
        with tempfile.TemporaryDirectory() as mixed_dir:
            mixed_path = Path(mixed_dir)
            
            # Add both React and FastAPI files
            (mixed_path / "package.json").write_text('{"dependencies": {"react": "^18.0.0"}}')
            (mixed_path / "requirements.txt").write_text("fastapi==0.68.0")
            (mixed_path / "src").mkdir()
            (mixed_path / "src" / "App.js").write_text("import React from 'react';")
            (mixed_path / "app").mkdir()
            (mixed_path / "app" / "main.py").write_text("from fastapi import FastAPI")
            
            result = analyzer.analyze_project(str(mixed_path))
            print(f"\nMixed project detected as: {result.project_type} (confidence: {result.confidence:.2f})")
            assert result.project_type is not None, "Should handle mixed projects"
    
    def test_performance_benchmarks(self, analyzer, test_projects):
        """Test analysis performance on different project sizes"""
        performance_results = {}
        
        for project_name, project_info in test_projects.items():
            start_time = time.time()
            result = analyzer.analyze_project(project_info["path"])
            end_time = time.time()
            
            analysis_time = end_time - start_time
            performance_results[project_name] = analysis_time
            
            # Assert reasonable performance
            assert analysis_time < 5.0, f"Analysis took too long: {analysis_time:.2f}s for {project_name}"
        
        avg_time = sum(performance_results.values()) / len(performance_results)
        print(f"\n=== Performance Benchmarks ===")
        print(f"Average analysis time: {avg_time:.3f}s")
        for project_name, time_taken in performance_results.items():
            print(f"{project_name}: {time_taken:.3f}s")
        
        assert avg_time < 2.0, f"Average analysis time {avg_time:.3f}s too slow"


def generate_accuracy_report(analyzer, test_projects):
    """Generate a comprehensive accuracy report"""
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_projects_tested": len(test_projects),
        "results": {},
        "summary": {}
    }
    
    correct_types = 0
    correct_frameworks = 0
    total_confidence = 0
    
    for project_name, project_info in test_projects.items():
        result = analyzer.analyze_project(project_info["path"])
        
        type_correct = result.project_type == project_info["expected_type"]
        if type_correct:
            correct_types += 1
        
        expected_frameworks = set(project_info["expected_frameworks"])
        detected_frameworks = set(result.tech_stack.frameworks)
        framework_correct = expected_frameworks == detected_frameworks
        if framework_correct:
            correct_frameworks += 1
        
        total_confidence += result.confidence
        
        report["results"][project_name] = {
            "expected_type": str(project_info["expected_type"]),
            "detected_type": str(result.project_type),
            "type_correct": type_correct,
            "expected_frameworks": list(expected_frameworks),
            "detected_frameworks": list(detected_frameworks),
            "framework_correct": framework_correct,
            "confidence": result.confidence,
            "complexity": result.estimated_complexity,
            "team_size": result.team_size_recommendation
        }
    
    report["summary"] = {
        "type_accuracy": correct_types / len(test_projects),
        "framework_accuracy": correct_frameworks / len(test_projects),
        "average_confidence": total_confidence / len(test_projects),
        "pass_threshold": 0.8
    }
    
    return report


if __name__ == "__main__":
    # Run tests and generate report
    analyzer = ProjectAnalyzer()
    
    # Create test projects
    temp_dirs = []
    test_projects = {}
    
    generators = [
        ("react_webapp", TestProjectGenerator.create_react_webapp),
        ("python_api", TestProjectGenerator.create_python_api),
        ("ml_project", TestProjectGenerator.create_ml_project),
        ("unity_game", TestProjectGenerator.create_unity_game),
        ("blockchain_truffle", TestProjectGenerator.create_blockchain_truffle),
        ("cli_tool", TestProjectGenerator.create_cli_tool),
    ]
    
    try:
        for name, generator in generators:
            temp_dir = tempfile.mkdtemp()
            temp_dirs.append(temp_dir)
            project_path = Path(temp_dir)
            
            expected = generator(project_path)
            test_projects[name] = {
                "path": str(project_path),
                "expected_type": expected["expected_type"],
                "expected_frameworks": expected["expected_frameworks"]
            }
        
        # Generate report
        report = generate_accuracy_report(analyzer, test_projects)
        
        # Save report
        report_path = Path("project_analysis_accuracy_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n=== ACCURACY REPORT SUMMARY ===")
        print(f"Type Detection Accuracy: {report['summary']['type_accuracy']:.2%}")
        print(f"Framework Detection Accuracy: {report['summary']['framework_accuracy']:.2%}")
        print(f"Average Confidence: {report['summary']['average_confidence']:.2f}")
        print(f"Pass Threshold: {report['summary']['pass_threshold']:.2%}")
        print(f"Overall Result: {'✅ PASS' if report['summary']['type_accuracy'] >= report['summary']['pass_threshold'] else '❌ FAIL'}")
        print(f"\nDetailed report saved to: {report_path}")
        
    finally:
        # Cleanup
        for temp_dir in temp_dirs:
            shutil.rmtree(temp_dir, ignore_errors=True)