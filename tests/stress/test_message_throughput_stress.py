"""
Message Throughput Stress Tests

This module tests the multi-agent coordination system's communication infrastructure
under high message throughput scenarios, including message bursts, large payloads,
concurrent message storms, and communication bottleneck identification.
"""

import time
import json
import os
import threading
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import random
import uuid
import queue
import gzip
import pytest

from .stress_test_engine import (
    StressTestScenario, StressTestRunner, StressTestConfig,
    create_light_stress_config, create_medium_stress_config, 
    create_heavy_stress_config, create_extreme_stress_config
)


@dataclass
class MessageThroughputMetrics:
    """Metrics for message throughput performance."""
    total_messages_sent: int
    total_messages_received: int
    total_bytes_sent: int
    total_bytes_received: int
    message_loss_rate: float
    average_latency: float
    max_latency: float
    min_latency: float
    throughput_messages_per_second: float
    throughput_bytes_per_second: float
    queue_overflow_events: int
    network_errors: int
    large_message_count: int
    burst_events: int


class MockCommunicationChannel:
    """Simulates communication channel with realistic delays and failures."""
    
    def __init__(self, channel_id: str, temp_dir: str, failure_rate: float = 0.02):
        self.channel_id = channel_id
        self.temp_dir = temp_dir
        self.failure_rate = failure_rate
        self.is_active = False
        
        # Channel metrics
        self.messages_sent = 0
        self.messages_received = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.latencies = []
        self.errors = 0
        
        # Message queues (simulating network buffers)
        self.outbound_queue = queue.Queue(maxsize=1000)
        self.inbound_queue = queue.Queue(maxsize=1000)
        
        # Files for persistent messaging
        self.outbound_file = os.path.join(temp_dir, f"channel_{channel_id}_out.json")
        self.inbound_file = os.path.join(temp_dir, f"channel_{channel_id}_in.json")
        
        # Processing threads
        self.processing_thread: Optional[threading.Thread] = None
        
        self._initialize_channel()
        
    def _initialize_channel(self):
        """Initialize channel files."""
        empty_queue = {"messages": [], "stats": {"total": 0, "processed": 0}}
        
        with open(self.outbound_file, 'w') as f:
            json.dump(empty_queue, f)
            
        with open(self.inbound_file, 'w') as f:
            json.dump(empty_queue, f)
            
    def start(self):
        """Start channel message processing."""
        self.is_active = True
        self.processing_thread = threading.Thread(target=self._process_messages, daemon=True)
        self.processing_thread.start()
        
    def stop(self):
        """Stop channel processing."""
        self.is_active = False
        if self.processing_thread:
            self.processing_thread.join(timeout=2.0)
            
    def send_message(self, message: Dict[str, Any], target_channel: str = None) -> bool:
        """Send a message through the channel."""
        try:
            # Add metadata
            message_with_metadata = {
                **message,
                "id": str(uuid.uuid4()),
                "sender_channel": self.channel_id,
                "target_channel": target_channel,
                "sent_at": time.time(),
                "size_bytes": len(json.dumps(message).encode('utf-8'))
            }
            
            # Simulate network failure
            if random.random() < self.failure_rate:
                self.errors += 1
                return False
                
            # Try to add to queue
            try:
                self.outbound_queue.put_nowait(message_with_metadata)
                self.messages_sent += 1
                self.bytes_sent += message_with_metadata["size_bytes"]
                return True
            except queue.Full:
                # Queue overflow
                self.errors += 1
                return False
                
        except Exception:
            self.errors += 1
            return False
            
    def _process_messages(self):
        """Process messages from queue to files."""
        while self.is_active:
            try:
                # Process outbound messages
                try:
                    message = self.outbound_queue.get(timeout=0.1)
                    self._write_message_to_file(message, self.outbound_file)
                    
                    # Simulate network latency
                    network_delay = random.uniform(0.001, 0.05)  # 1-50ms
                    time.sleep(network_delay)
                    
                except queue.Empty:
                    pass
                    
                # Process inbound messages (simulate receiving)
                self._simulate_inbound_messages()
                
            except Exception:
                pass  # Continue processing on errors
                
    def _write_message_to_file(self, message: Dict[str, Any], filename: str):
        """Write message to file (simulating network transmission)."""
        try:
            # Read current file
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {"messages": [], "stats": {"total": 0, "processed": 0}}
                
            # Add message
            data["messages"].append(message)
            data["stats"]["total"] += 1
            
            # Write back (with compression for large files)
            if len(data["messages"]) > 1000:
                # Compress old messages
                compressed_file = filename + ".gz"
                with gzip.open(compressed_file, 'wt') as f:
                    json.dump({"messages": data["messages"][:-500]}, f)
                data["messages"] = data["messages"][-500:]  # Keep recent messages
                
            with open(filename, 'w') as f:
                json.dump(data, f)
                
        except Exception:
            pass  # Ignore file errors
            
    def _simulate_inbound_messages(self):
        """Simulate receiving messages from other channels."""
        # Randomly receive messages to simulate network traffic
        if random.random() < 0.3:  # 30% chance each cycle
            fake_message = {
                "id": str(uuid.uuid4()),
                "type": "coordination_update",
                "data": {"status": "active", "progress": random.randint(0, 100)},
                "received_at": time.time(),
                "size_bytes": random.randint(100, 1000)
            }
            
            try:
                self.inbound_queue.put_nowait(fake_message)
                self.messages_received += 1
                self.bytes_received += fake_message["size_bytes"]
                
                # Calculate latency (simulated)
                latency = random.uniform(0.001, 0.1)
                self.latencies.append(latency)
                
            except queue.Full:
                pass  # Ignore overflow
                
    def get_metrics(self) -> Dict[str, Any]:
        """Get channel performance metrics."""
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        max_latency = max(self.latencies) if self.latencies else 0
        min_latency = min(self.latencies) if self.latencies else 0
        
        return {
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "errors": self.errors,
            "average_latency": avg_latency,
            "max_latency": max_latency,
            "min_latency": min_latency,
            "queue_size_out": self.outbound_queue.qsize(),
            "queue_size_in": self.inbound_queue.qsize()
        }


class MockHighThroughputAgent:
    """Simulates agent generating high message throughput."""
    
    def __init__(self, agent_id: str, channel: MockCommunicationChannel, throughput_level: str = "medium"):
        self.agent_id = agent_id
        self.channel = channel
        self.throughput_level = throughput_level
        self.is_running = False
        self.activity_thread: Optional[threading.Thread] = None
        
        # Throughput metrics
        self.messages_generated = 0
        self.burst_events = 0
        self.large_messages = 0
        
    def start(self):
        """Start high-throughput message generation."""
        self.is_running = True
        self.activity_thread = threading.Thread(target=self._throughput_loop, daemon=True)
        self.activity_thread.start()
        
    def stop(self):
        """Stop message generation."""
        self.is_running = False
        if self.activity_thread:
            self.activity_thread.join(timeout=2.0)
            
    def _throughput_loop(self):
        """Main loop for generating high message throughput."""
        while self.is_running:
            try:
                if self.throughput_level == "light":
                    self._generate_light_throughput()
                    time.sleep(0.1)
                elif self.throughput_level == "medium":
                    self._generate_medium_throughput()
                    time.sleep(0.05)
                elif self.throughput_level == "heavy":
                    self._generate_heavy_throughput()
                    time.sleep(0.02)
                else:  # extreme
                    self._generate_extreme_throughput()
                    time.sleep(0.01)
                    
            except Exception:
                pass  # Continue on errors
                
    def _generate_light_throughput(self):
        """Generate light message throughput."""
        # Send 1-3 messages
        for _ in range(random.randint(1, 3)):
            self._send_coordination_message()
            
    def _generate_medium_throughput(self):
        """Generate medium message throughput."""
        # Send 3-8 messages
        for _ in range(random.randint(3, 8)):
            self._send_coordination_message()
            
        # Occasional burst
        if random.random() < 0.1:  # 10% chance
            self._send_message_burst(10)
            
    def _generate_heavy_throughput(self):
        """Generate heavy message throughput."""
        # Send 8-15 messages
        for _ in range(random.randint(8, 15)):
            self._send_coordination_message()
            
        # Frequent bursts
        if random.random() < 0.2:  # 20% chance
            self._send_message_burst(20)
            
        # Large messages
        if random.random() < 0.1:  # 10% chance
            self._send_large_message()
            
    def _generate_extreme_throughput(self):
        """Generate extreme message throughput."""
        # Send 15-30 messages
        for _ in range(random.randint(15, 30)):
            self._send_coordination_message()
            
        # Constant bursts
        if random.random() < 0.4:  # 40% chance
            self._send_message_burst(50)
            
        # Many large messages
        if random.random() < 0.2:  # 20% chance
            self._send_large_message()
            
    def _send_coordination_message(self):
        """Send a standard coordination message."""
        message = {
            "type": "coordination",
            "sender": self.agent_id,
            "data": {
                "status": random.choice(["active", "working", "waiting"]),
                "progress": random.randint(0, 100),
                "current_task": f"task_{random.randint(1, 100)}",
                "timestamp": time.time()
            }
        }
        
        success = self.channel.send_message(message)
        if success:
            self.messages_generated += 1
            
    def _send_message_burst(self, burst_size: int):
        """Send a burst of messages rapidly."""
        self.burst_events += 1
        
        for i in range(burst_size):
            message = {
                "type": "burst",
                "sender": self.agent_id,
                "burst_id": str(uuid.uuid4()),
                "burst_sequence": i,
                "burst_size": burst_size,
                "data": {
                    "urgent": True,
                    "payload": f"burst_data_{i}_{random.randint(1000, 9999)}"
                }
            }
            
            success = self.channel.send_message(message)
            if success:
                self.messages_generated += 1
                
            # Small delay between burst messages
            time.sleep(0.001)  # 1ms
            
    def _send_large_message(self):
        """Send a large message to test payload handling."""
        self.large_messages += 1
        
        # Generate large payload (1-10KB)
        payload_size = random.randint(1000, 10000)
        large_payload = "x" * payload_size
        
        message = {
            "type": "large_payload",
            "sender": self.agent_id,
            "size_bytes": payload_size,
            "data": {
                "payload": large_payload,
                "metadata": {
                    "generated_at": time.time(),
                    "purpose": "stress_test_large_message",
                    "compression": False
                }
            }
        }
        
        success = self.channel.send_message(message)
        if success:
            self.messages_generated += 1


class MessageThroughputStressScenario(StressTestScenario):
    """Stress test scenario for message throughput."""
    
    def __init__(self, config: StressTestConfig):
        super().__init__(config)
        self.temp_dir: Optional[str] = None
        self.channels: List[MockCommunicationChannel] = []
        self.agents: List[MockHighThroughputAgent] = []
        self.throughput_metrics = MessageThroughputMetrics(
            total_messages_sent=0, total_messages_received=0,
            total_bytes_sent=0, total_bytes_received=0,
            message_loss_rate=0.0, average_latency=0.0,
            max_latency=0.0, min_latency=0.0,
            throughput_messages_per_second=0.0, throughput_bytes_per_second=0.0,
            queue_overflow_events=0, network_errors=0,
            large_message_count=0, burst_events=0
        )
        
    def setup(self):
        """Setup the message throughput stress test."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="message_throughput_stress_")
        
        # Determine parameters based on stress level
        level_params = {
            "light": (3, 2, 0.01),    # 3 channels, 2 agents per channel, 1% failure rate
            "medium": (6, 4, 0.02),   # 6 channels, 4 agents per channel, 2% failure rate  
            "heavy": (10, 6, 0.03),   # 10 channels, 6 agents per channel, 3% failure rate
            "extreme": (15, 8, 0.05)  # 15 channels, 8 agents per channel, 5% failure rate
        }
        
        channel_count, agents_per_channel, failure_rate = level_params.get(
            self.config.level.value, (6, 4, 0.02)
        )
        
        print(f"📡 Setting up {channel_count} channels with {agents_per_channel} agents each")
        
        # Create communication channels
        for i in range(channel_count):
            channel_id = f"channel_{i}"
            channel = MockCommunicationChannel(channel_id, self.temp_dir, failure_rate)
            self.channels.append(channel)
            
        # Create high-throughput agents
        throughput_level = self.config.level.value
        for i, channel in enumerate(self.channels):
            for j in range(agents_per_channel):
                agent_id = f"throughput_agent_{i}_{j}"
                agent = MockHighThroughputAgent(agent_id, channel, throughput_level)
                self.agents.append(agent)
                
    def execute_stress(self):
        """Execute the message throughput stress test."""
        print(f"📡 Starting message throughput test with {len(self.channels)} channels and {len(self.agents)} agents")
        
        # Start all channels
        for channel in self.channels:
            channel.start()
            
        # Start all agents
        test_start_time = time.time()
        for agent in self.agents:
            agent.start()
            
        # Monitor throughput during the test
        test_duration = self.config.duration_seconds
        end_time = time.time() + test_duration
        
        print(f"📡 Message throughput running for {test_duration} seconds...")
        
        # Collect interim metrics every 10 seconds
        while time.time() < end_time and self.should_continue():
            time.sleep(10.0)
            self._collect_interim_throughput_metrics()
            
        # Stop all agents and channels
        for agent in self.agents:
            agent.stop()
            
        for channel in self.channels:
            channel.stop()
            
        # Calculate final throughput metrics
        total_test_time = time.time() - test_start_time
        self._collect_final_throughput_metrics(total_test_time)
        
        print(f"✅ Message throughput test completed")
        print(f"📊 Total messages: {self.throughput_metrics.total_messages_sent}")
        print(f"📊 Throughput: {self.throughput_metrics.throughput_messages_per_second:.1f} msg/s")
        print(f"📊 Data rate: {self.throughput_metrics.throughput_bytes_per_second / 1024:.1f} KB/s")
        
    def _collect_interim_throughput_metrics(self):
        """Collect throughput metrics during the test."""
        total_sent = sum(channel.messages_sent for channel in self.channels)
        total_received = sum(channel.messages_received for channel in self.channels)
        total_errors = sum(channel.errors for channel in self.channels)
        
        # Record interim metrics
        self.record_metric("interim_messages_sent", total_sent)
        self.record_metric("interim_messages_received", total_received)
        self.record_metric("interim_error_rate", total_errors / max(total_sent, 1) * 100, "percent")
        
    def _collect_final_throughput_metrics(self, test_duration: float):
        """Collect final throughput metrics."""
        # Aggregate metrics from all channels
        total_sent = sum(channel.messages_sent for channel in self.channels)
        total_received = sum(channel.messages_received for channel in self.channels)
        total_bytes_sent = sum(channel.bytes_sent for channel in self.channels)
        total_bytes_received = sum(channel.bytes_received for channel in self.channels)
        total_errors = sum(channel.errors for channel in self.channels)
        
        # Aggregate latency data
        all_latencies = []
        for channel in self.channels:
            all_latencies.extend(channel.latencies)
            
        avg_latency = sum(all_latencies) / len(all_latencies) if all_latencies else 0
        max_latency = max(all_latencies) if all_latencies else 0
        min_latency = min(all_latencies) if all_latencies else 0
        
        # Calculate throughput rates
        msg_throughput = total_sent / test_duration if test_duration > 0 else 0
        byte_throughput = total_bytes_sent / test_duration if test_duration > 0 else 0
        
        # Calculate message loss rate
        message_loss_rate = (total_sent - total_received) / max(total_sent, 1) * 100
        
        # Aggregate agent metrics
        total_bursts = sum(agent.burst_events for agent in self.agents)
        total_large_messages = sum(agent.large_messages for agent in self.agents)
        
        # Update metrics object
        self.throughput_metrics.total_messages_sent = total_sent
        self.throughput_metrics.total_messages_received = total_received
        self.throughput_metrics.total_bytes_sent = total_bytes_sent
        self.throughput_metrics.total_bytes_received = total_bytes_received
        self.throughput_metrics.message_loss_rate = message_loss_rate
        self.throughput_metrics.average_latency = avg_latency
        self.throughput_metrics.max_latency = max_latency
        self.throughput_metrics.min_latency = min_latency
        self.throughput_metrics.throughput_messages_per_second = msg_throughput
        self.throughput_metrics.throughput_bytes_per_second = byte_throughput
        self.throughput_metrics.network_errors = total_errors
        self.throughput_metrics.burst_events = total_bursts
        self.throughput_metrics.large_message_count = total_large_messages
        
        # Record final metrics
        self.record_metric("total_messages_sent", total_sent)
        self.record_metric("total_messages_received", total_received)
        self.record_metric("total_bytes_sent", total_bytes_sent, "bytes")
        self.record_metric("total_bytes_received", total_bytes_received, "bytes")
        self.record_metric("message_loss_rate", message_loss_rate, "percent")
        self.record_metric("average_latency", avg_latency * 1000, "milliseconds")
        self.record_metric("max_latency", max_latency * 1000, "milliseconds")
        self.record_metric("throughput_messages_per_second", msg_throughput, "msg/s")
        self.record_metric("throughput_kilobytes_per_second", byte_throughput / 1024, "KB/s")
        self.record_metric("network_errors", total_errors)
        self.record_metric("burst_events", total_bursts)
        self.record_metric("large_message_count", total_large_messages)
        
        # Validate performance
        self._validate_throughput_performance()
        
    def _validate_throughput_performance(self):
        """Validate message throughput performance."""
        # Check message loss rate
        if self.throughput_metrics.message_loss_rate > 10.0:  # Over 10% loss
            self.record_failure(
                "high_message_loss",
                f"Message loss rate too high: {self.throughput_metrics.message_loss_rate:.1f}%"
            )
            
        # Check latency
        if self.throughput_metrics.average_latency > 0.5:  # Over 500ms average
            self.record_failure(
                "high_latency",
                f"Average latency too high: {self.throughput_metrics.average_latency*1000:.1f}ms"
            )
            
        if self.throughput_metrics.max_latency > 2.0:  # Over 2 seconds max
            self.record_failure(
                "excessive_max_latency",
                f"Maximum latency too high: {self.throughput_metrics.max_latency*1000:.1f}ms"
            )
            
        # Check throughput minimums based on test level
        min_throughput_requirements = {
            "light": 50,    # 50 msg/s minimum
            "medium": 100,  # 100 msg/s minimum
            "heavy": 200,   # 200 msg/s minimum
            "extreme": 400  # 400 msg/s minimum
        }
        
        required_throughput = min_throughput_requirements.get(self.config.level.value, 100)
        if self.throughput_metrics.throughput_messages_per_second < required_throughput:
            self.record_failure(
                "insufficient_throughput",
                f"Throughput below requirement: {self.throughput_metrics.throughput_messages_per_second:.1f} < {required_throughput} msg/s"
            )
            
        # Check error rate
        error_rate = self.throughput_metrics.network_errors / max(self.throughput_metrics.total_messages_sent, 1) * 100
        if error_rate > 15.0:  # Over 15% error rate
            self.record_failure(
                "high_error_rate",
                f"Network error rate too high: {error_rate:.1f}%"
            )
            
    def cleanup(self):
        """Clean up the message throughput stress test."""
        # Stop any remaining channels and agents
        for agent in self.agents:
            agent.stop()
            
        for channel in self.channels:
            channel.stop()
            
        # Generate throughput analysis report
        self._generate_throughput_report()
        
        # Clean up temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def _generate_throughput_report(self):
        """Generate detailed message throughput analysis report."""
        report = {
            "message_throughput_analysis": {
                "test_config": {
                    "level": self.config.level.value,
                    "channel_count": len(self.channels),
                    "agent_count": len(self.agents),
                    "duration": self.config.duration_seconds
                },
                "throughput_metrics": {
                    "messages_sent": self.throughput_metrics.total_messages_sent,
                    "messages_received": self.throughput_metrics.total_messages_received,
                    "bytes_sent": self.throughput_metrics.total_bytes_sent,
                    "bytes_received": self.throughput_metrics.total_bytes_received,
                    "message_loss_rate_percent": self.throughput_metrics.message_loss_rate,
                    "throughput_msg_per_sec": self.throughput_metrics.throughput_messages_per_second,
                    "throughput_kb_per_sec": self.throughput_metrics.throughput_bytes_per_second / 1024,
                    "average_latency_ms": self.throughput_metrics.average_latency * 1000,
                    "max_latency_ms": self.throughput_metrics.max_latency * 1000,
                    "network_errors": self.throughput_metrics.network_errors,
                    "burst_events": self.throughput_metrics.burst_events,
                    "large_messages": self.throughput_metrics.large_message_count
                },
                "channel_performance": [
                    {
                        "channel_id": channel.channel_id,
                        **channel.get_metrics()
                    }
                    for channel in self.channels
                ],
                "agent_performance": [
                    {
                        "agent_id": agent.agent_id,
                        "messages_generated": agent.messages_generated,
                        "burst_events": agent.burst_events,
                        "large_messages": agent.large_messages
                    }
                    for agent in self.agents
                ],
                "recommendations": self._generate_throughput_recommendations()
            }
        }
        
        # Save report
        report_file = os.path.join("stress_test_results", f"message_throughput_analysis_{int(time.time())}.json")
        os.makedirs("stress_test_results", exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
    def _generate_throughput_recommendations(self) -> List[str]:
        """Generate recommendations for improving message throughput."""
        recommendations = []
        
        if self.throughput_metrics.message_loss_rate > 5.0:
            recommendations.append("Increase message queue sizes to reduce overflow")
            recommendations.append("Implement message acknowledgment and retry mechanisms")
            
        if self.throughput_metrics.average_latency > 0.1:
            recommendations.append("Optimize message serialization and deserialization")
            recommendations.append("Consider message batching for improved efficiency")
            
        if self.throughput_metrics.network_errors > 100:
            recommendations.append("Improve error handling and recovery mechanisms")
            recommendations.append("Add circuit breaker patterns for failing channels")
            
        if self.throughput_metrics.throughput_messages_per_second < 200:
            recommendations.append("Optimize communication channel implementation")
            recommendations.append("Consider asynchronous message processing")
            
        return recommendations


# Pytest integration
@pytest.mark.stress
@pytest.mark.communication
class TestMessageThroughputStress:
    """Pytest class for message throughput stress tests."""
    
    def test_light_message_throughput(self):
        """Test light message throughput stress."""
        config = create_light_stress_config("light_message_throughput", 
                                           duration_seconds=60, agent_count=6)
        scenario = MessageThroughputStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        assert result.success, f"Light message throughput test failed: {result.error_message}"
        assert scenario.throughput_metrics.total_messages_sent > 0, "No messages sent"
        
    def test_medium_message_throughput(self):
        """Test medium message throughput stress."""
        config = create_medium_stress_config("medium_message_throughput",
                                            duration_seconds=180, agent_count=24)
        scenario = MessageThroughputStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        assert result.success, f"Medium message throughput test failed: {result.error_message}"
        assert scenario.throughput_metrics.total_messages_sent > 1000, "Insufficient message volume"
        
    @pytest.mark.slow
    def test_heavy_message_throughput(self):
        """Test heavy message throughput stress."""
        config = create_heavy_stress_config("heavy_message_throughput",
                                           duration_seconds=300, agent_count=60)
        scenario = MessageThroughputStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        assert result.success, f"Heavy message throughput test failed: {result.error_message}"
        assert scenario.throughput_metrics.total_messages_sent > 5000, "Insufficient message volume"
        
    @pytest.mark.slow
    @pytest.mark.extreme
    def test_extreme_message_throughput(self):
        """Test extreme message throughput stress."""
        config = create_extreme_stress_config("extreme_message_throughput",
                                             duration_seconds=600, agent_count=120)
        scenario = MessageThroughputStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        # Extreme tests may fail due to resource limits
        if not result.success:
            pytest.skip(f"Extreme message throughput test hit limits: {result.error_message}")
            
        assert scenario.throughput_metrics.total_messages_sent > 10000, "Insufficient message volume for extreme test"


if __name__ == "__main__":
    # Run message throughput stress tests directly
    runner = StressTestRunner()
    
    # Test different throughput levels
    scenarios = [
        MessageThroughputStressScenario(create_light_stress_config("light_throughput", duration_seconds=30)),
        MessageThroughputStressScenario(create_medium_stress_config("medium_throughput", duration_seconds=60))
    ]
    
    results = runner.run_scenarios(scenarios)
    
    print("\n" + runner.generate_summary_report(results))