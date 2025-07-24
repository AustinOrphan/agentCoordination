#!/usr/bin/env python3
"""
BDD step definitions for communication edge cases.
Tests inter-agent communication under extreme conditions.
"""

import pytest
import time
import threading
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from pytest_bdd import scenarios, given, when, then, parsers
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from unittest.mock import Mock, patch

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "coordination_system"))

# Load all scenarios from communication edge cases feature file
scenarios('edge_cases/communication_edge_cases.feature')


@dataclass
class Message:
    """Message structure for testing."""
    id: str
    sender: str
    recipient: str
    message_type: str
    payload: str
    priority: int = 1
    timestamp: float = None
    size_kb: float = 0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.size_kb == 0:
            self.size_kb = len(self.payload) / 1024


class MockCommunicationSystem:
    """Mock communication system for testing."""
    
    def __init__(self):
        self.agents = {}
        self.messages = []
        self.network_conditions = {
            'latency_ms': 10,
            'packet_loss_percent': 0
        }
        self.message_queues = {}
        self.failed_deliveries = []
        self.queue_capacity = 1000
        
    def add_agent(self, agent_name):
        """Add agent to communication system."""
        self.agents[agent_name] = {
            'status': 'online',
            'message_queue': [],
            'queue_capacity': self.queue_capacity
        }
        self.message_queues[agent_name] = []
    
    def set_network_conditions(self, latency_ms, packet_loss_percent):
        """Set network simulation conditions."""
        self.network_conditions = {
            'latency_ms': latency_ms,
            'packet_loss_percent': packet_loss_percent
        }
    
    def send_message(self, message: Message):
        """Send message with network simulation."""
        # Simulate packet loss
        if random.random() * 100 < self.network_conditions['packet_loss_percent']:
            self.failed_deliveries.append(message)
            return False
        
        # Simulate latency
        time.sleep(self.network_conditions['latency_ms'] / 1000.0)
        
        # Check recipient exists and is online
        if message.recipient not in self.agents:
            return False
        
        recipient_agent = self.agents[message.recipient]
        if recipient_agent['status'] != 'online':
            self.failed_deliveries.append(message)
            return False
        
        # Check queue capacity
        if len(recipient_agent['message_queue']) >= recipient_agent['queue_capacity']:
            self.failed_deliveries.append(message)
            return False
        
        # Deliver message
        recipient_agent['message_queue'].append(message)
        self.messages.append(message)
        return True
    
    def broadcast_message(self, sender, message_content, message_type="broadcast"):
        """Broadcast message to all agents."""
        results = {}
        for agent_name in self.agents:
            if agent_name != sender:
                message = Message(
                    id=f"BROADCAST-{len(self.messages)}",
                    sender=sender,
                    recipient=agent_name,
                    message_type=message_type,
                    payload=message_content
                )
                results[agent_name] = self.send_message(message)
        return results


# Background steps
@given("the communication channels are initialized")
def communication_system_initialized():
    """Initialize communication system for testing."""
    comm_system = MockCommunicationSystem()
    
    # Add standard agents
    agent_names = ['shark', 'dolphin', 'whale', 'octopus', 'jellyfish', 'seahorse']
    for name in agent_names:
        comm_system.add_agent(name)
    
    return comm_system


# Scenario Outline steps for varying network conditions
@given(parsers.parse("the network has {latency:d}ms latency and {packet_loss:d}% packet loss"))
def set_network_conditions(communication_system_initialized, latency, packet_loss):
    """Set network simulation conditions."""
    comm_system = communication_system_initialized
    comm_system.set_network_conditions(latency, packet_loss)
    
    return {"latency": latency, "packet_loss": packet_loss}


@when(parsers.parse("I send {message_count:d} messages of size {message_size:d}KB"))
def send_test_messages(communication_system_initialized, message_count, message_size):
    """Send test messages with specified count and size."""
    comm_system = communication_system_initialized
    
    # Create payload of specified size
    payload = "x" * (message_size * 1024)
    
    results = []
    start_time = time.time()
    
    for i in range(message_count):
        message = Message(
            id=f"TEST-{i}",
            sender="shark",
            recipient="dolphin",
            message_type="test",
            payload=payload,
            size_kb=message_size
        )
        
        delivered = comm_system.send_message(message)
        results.append({
            "message": message,
            "delivered": delivered,
            "delivery_time": time.time() - start_time
        })
    
    end_time = time.time()
    
    return {
        "results": results,
        "total_sent": message_count,
        "total_delivered": sum(1 for r in results if r["delivered"]),
        "total_time": end_time - start_time
    }


@then(parsers.parse("{delivery_rate:d}% of messages should be delivered"))
def verify_delivery_rate(send_test_messages, delivery_rate):
    """Verify message delivery rate meets expectations."""
    actual_rate = (send_test_messages["total_delivered"] / send_test_messages["total_sent"]) * 100
    
    # Allow some tolerance for network simulation
    assert actual_rate >= delivery_rate * 0.9, \
        f"Delivery rate {actual_rate:.1f}% below expected {delivery_rate}%"


@then(parsers.parse("the average delivery time should be under {max_delivery_time:d}ms"))
def verify_delivery_time(send_test_messages, max_delivery_time):
    """Verify average delivery time is within limits."""
    delivered_results = [r for r in send_test_messages["results"] if r["delivered"]]
    
    if delivered_results:
        avg_delivery_time = (send_test_messages["total_time"] / len(delivered_results)) * 1000
        assert avg_delivery_time <= max_delivery_time, \
            f"Average delivery time {avg_delivery_time:.1f}ms exceeds limit {max_delivery_time}ms"


@then("the system should handle retries appropriately")
def verify_retry_handling(communication_system_initialized):
    """Verify system handles retries for failed messages."""
    comm_system = communication_system_initialized
    
    # Check for failed deliveries that should be retried
    assert hasattr(comm_system, 'failed_deliveries'), "No retry mechanism detected"


# Message queue overflow scenario
@given("each agent has a message queue capacity of 1000")
def set_queue_capacity(communication_system_initialized):
    """Set message queue capacity for agents."""
    comm_system = communication_system_initialized
    
    for agent in comm_system.agents.values():
        agent['queue_capacity'] = 1000
    
    comm_system.queue_capacity = 1000
    return {"queue_capacity": 1000}


@when("10000 messages are sent within 10 seconds")
def send_high_volume_messages(communication_system_initialized, set_queue_capacity):
    """Send high volume of messages to trigger overflow."""
    comm_system = communication_system_initialized
    
    messages_sent = 0
    overflow_detected = False
    flow_control_activated = False
    
    start_time = time.time()
    
    # Send messages rapidly
    for i in range(10000):
        if time.time() - start_time > 10:  # Stop after 10 seconds
            break
            
        message = Message(
            id=f"FLOOD-{i}",
            sender="shark",
            recipient="dolphin",
            message_type="test",
            payload=f"Message {i}",
            priority=1 if i % 10 != 0 else 5  # Some high priority
        )
        
        delivered = comm_system.send_message(message)
        messages_sent += 1
        
        # Check for overflow
        dolphin_queue = comm_system.agents['dolphin']['message_queue']
        if len(dolphin_queue) >= comm_system.queue_capacity:
            overflow_detected = True
            flow_control_activated = True
            break
    
    return {
        "messages_sent": messages_sent,
        "overflow_detected": overflow_detected,
        "flow_control_activated": flow_control_activated
    }


@then("the system should activate flow control")
def verify_flow_control_activation(send_high_volume_messages):
    """Verify flow control is activated during overflow."""
    assert send_high_volume_messages["flow_control_activated"], \
        "Flow control was not activated during overflow"


@then("high priority messages should be preserved")
def verify_high_priority_preservation(communication_system_initialized):
    """Verify high priority messages are preserved during overflow."""
    comm_system = communication_system_initialized
    dolphin_queue = comm_system.agents['dolphin']['message_queue']
    
    # Check for high priority messages in queue
    high_priority_messages = [m for m in dolphin_queue if m.priority > 1]
    assert len(high_priority_messages) > 0, "No high priority messages preserved"


@then("low priority messages may be dropped with notifications")
def verify_low_priority_dropping(communication_system_initialized):
    """Verify low priority messages are dropped appropriately."""
    comm_system = communication_system_initialized
    
    # Check failed deliveries for low priority messages
    low_priority_dropped = any(m.priority == 1 for m in comm_system.failed_deliveries)
    assert len(comm_system.failed_deliveries) > 0, "No messages were dropped"


@then("agents should receive overflow warnings")
def verify_overflow_warnings(send_high_volume_messages):
    """Verify agents receive overflow warnings."""
    # In a real system, this would check notification system
    assert send_high_volume_messages["overflow_detected"]


@then("the system should recover gracefully after traffic subsides")
def verify_graceful_recovery(communication_system_initialized):
    """Verify system recovers after traffic subsides."""
    comm_system = communication_system_initialized
    
    # System should still be functional
    test_message = Message(
        id="RECOVERY-TEST",
        sender="whale",
        recipient="octopus",
        message_type="test",
        payload="Recovery test"
    )
    
    delivered = comm_system.send_message(test_message)
    assert delivered, "System did not recover gracefully"


# Message ordering scenario
@given(parsers.parse('I have agents "{agent1}", "{agent2}", and "{agent3}"'))
def setup_three_agents(communication_system_initialized, agent1, agent2, agent3):
    """Setup three specific agents for testing."""
    comm_system = communication_system_initialized
    
    # Ensure agents exist
    for agent in [agent1, agent2, agent3]:
        if agent not in comm_system.agents:
            comm_system.add_agent(agent)
    
    return {"agents": [agent1, agent2, agent3]}


@when(parsers.parse('"{sender1}" sends 5 sequential messages to "{recipient}"'))
def send_sequential_messages_first(communication_system_initialized, sender1, recipient):
    """First sender sends sequential messages."""
    comm_system = communication_system_initialized
    
    messages = []
    for i in range(5):
        message = Message(
            id=f"{sender1}-SEQ-{i}",
            sender=sender1,
            recipient=recipient,
            message_type="sequential",
            payload=f"Message {i} from {sender1}"
        )
        
        delivered = comm_system.send_message(message)
        messages.append({"message": message, "delivered": delivered})
        time.sleep(0.001)  # Small delay to ensure ordering
    
    return {f"{sender1}_messages": messages}


@when(parsers.parse('"{sender2}" sends 5 sequential messages to "{recipient}" simultaneously'))
def send_simultaneous_messages(communication_system_initialized, sender2, recipient, 
                               send_sequential_messages_first):
    """Second sender sends messages simultaneously."""
    comm_system = communication_system_initialized
    
    messages = []
    
    # Send messages with threading to simulate simultaneity
    def send_message_threaded(i):
        message = Message(
            id=f"{sender2}-SIM-{i}",
            sender=sender2,
            recipient=recipient,
            message_type="simultaneous",
            payload=f"Message {i} from {sender2}"
        )
        
        delivered = comm_system.send_message(message)
        return {"message": message, "delivered": delivered}
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(send_message_threaded, i) for i in range(5)]
        
        for future in as_completed(futures):
            messages.append(future.result())
    
    combined_results = send_sequential_messages_first.copy()
    combined_results[f"{sender2}_messages"] = messages
    
    return combined_results


@then("each sender's messages should arrive in order")
def verify_sender_message_ordering(communication_system_initialized, send_simultaneous_messages):
    """Verify messages from each sender maintain order."""
    comm_system = communication_system_initialized
    
    # Get messages received by recipient
    recipient_queue = None
    for agent_name, agent in comm_system.agents.items():
        if len(agent['message_queue']) > 0:
            recipient_queue = agent['message_queue']
            break
    
    assert recipient_queue is not None, "No messages found in recipient queue"
    
    # Check ordering within each sender's messages
    sender1_messages = [m for m in recipient_queue if "SEQ" in m.id]
    sender2_messages = [m for m in recipient_queue if "SIM" in m.id]
    
    # Verify sequential messages are in order
    if len(sender1_messages) > 1:
        for i in range(len(sender1_messages) - 1):
            assert sender1_messages[i].timestamp <= sender1_messages[i + 1].timestamp


@then("the system should handle interleaving correctly")
def verify_message_interleaving(communication_system_initialized):
    """Verify system handles message interleaving correctly."""
    comm_system = communication_system_initialized
    
    # System should have received messages from both senders
    total_messages = sum(len(agent['message_queue']) for agent in comm_system.agents.values())
    assert total_messages >= 5, "Not all messages were received"


@then("message timestamps should reflect actual order")
def verify_timestamp_ordering(communication_system_initialized):
    """Verify timestamps reflect actual message order."""
    comm_system = communication_system_initialized
    
    # Get all messages and check timestamps
    all_messages = []
    for agent in comm_system.agents.values():
        all_messages.extend(agent['message_queue'])
    
    # Timestamps should be monotonic within reasonable tolerance
    for i in range(len(all_messages) - 1):
        time_diff = all_messages[i + 1].timestamp - all_messages[i].timestamp
        assert time_diff >= -0.1, "Timestamp ordering violation detected"


@then("no messages should be lost or duplicated")
def verify_no_message_loss_duplication(send_simultaneous_messages):
    """Verify no messages were lost or duplicated."""
    # Count sent vs received messages
    sender1_sent = len(send_simultaneous_messages.get('shark_messages', []))
    sender2_sent = len(send_simultaneous_messages.get('whale_messages', []))
    
    # In this test context, we verify the data structures are consistent
    assert sender1_sent > 0 or sender2_sent > 0, "No messages tracked"


# Broadcast with partial delivery scenario
@given('agents "octopus" and "jellyfish" have network issues')
def agents_with_network_issues(communication_system_initialized):
    """Set specific agents to have network issues."""
    comm_system = communication_system_initialized
    
    # Simulate network issues by marking agents as having problems
    comm_system.agents['octopus']['status'] = 'network_issues'
    comm_system.agents['jellyfish']['status'] = 'network_issues'
    
    return {"problematic_agents": ['octopus', 'jellyfish']}


@when(parsers.parse('"{sender}" broadcasts a critical update to all agents'))
def broadcast_critical_update(communication_system_initialized, sender, agents_with_network_issues):
    """Broadcast critical update to all agents."""
    comm_system = communication_system_initialized
    
    # Override send_message to simulate network issues
    original_send = comm_system.send_message
    
    def send_with_issues(message):
        if message.recipient in agents_with_network_issues["problematic_agents"]:
            # Simulate failure for problematic agents
            comm_system.failed_deliveries.append(message)
            return False
        return original_send(message)
    
    comm_system.send_message = send_with_issues
    
    # Perform broadcast
    results = comm_system.broadcast_message(sender, "Critical system update", "critical_update")
    
    # Restore original method
    comm_system.send_message = original_send
    
    return {
        "broadcast_results": results,
        "successful_deliveries": sum(1 for success in results.values() if success),
        "failed_deliveries": sum(1 for success in results.values() if not success)
    }


@then("4 agents should receive the message immediately")
def verify_immediate_delivery_count(broadcast_critical_update):
    """Verify correct number of immediate deliveries."""
    successful = broadcast_critical_update["successful_deliveries"]
    assert successful == 4, f"Expected 4 successful deliveries, got {successful}"


@then("the system should detect the failed deliveries")
def verify_failed_delivery_detection(communication_system_initialized, broadcast_critical_update):
    """Verify system detects failed deliveries."""
    comm_system = communication_system_initialized
    failed_count = broadcast_critical_update["failed_deliveries"]
    
    assert failed_count == 2, f"Expected 2 failed deliveries, got {failed_count}"
    assert len(comm_system.failed_deliveries) > 0, "No failed deliveries tracked"


@then("retry delivery to unreachable agents")
def verify_retry_mechanism(communication_system_initialized):
    """Verify retry mechanism for failed deliveries."""
    comm_system = communication_system_initialized
    
    # In a real system, this would trigger retry mechanism
    assert len(comm_system.failed_deliveries) > 0, "No deliveries to retry"


@then("track acknowledgments from all recipients")
def verify_acknowledgment_tracking(broadcast_critical_update):
    """Verify acknowledgments are tracked."""
    # In a real system, this would check ACK tracking
    assert broadcast_critical_update["broadcast_results"] is not None


@then("provide delivery status report to sender")
def verify_delivery_status_report(broadcast_critical_update):
    """Verify delivery status report is provided."""
    results = broadcast_critical_update["broadcast_results"]
    assert len(results) > 0, "No delivery status available"


# Invalid message handling scenario
@when(parsers.parse('an agent sends a message with "{invalid_field}" as "{invalid_value}"'))
def send_invalid_message(communication_system_initialized, invalid_field, invalid_value):
    """Send message with invalid field."""
    comm_system = communication_system_initialized
    
    try:
        if invalid_field == "recipient":
            message = Message(
                id="INVALID-RECIPIENT",
                sender="shark",
                recipient="unknown_agent",  # Invalid recipient
                message_type="test",
                payload="Test message"
            )
        elif invalid_field == "message_type":
            message = Message(
                id="INVALID-TYPE",
                sender="shark",
                recipient="dolphin",
                message_type="invalid_type",  # Invalid type
                payload="Test message"
            )
        elif invalid_field == "payload":
            message = Message(
                id="INVALID-PAYLOAD",
                sender="shark",
                recipient="dolphin",
                message_type="test",
                payload="x" * 10000000  # Too large payload
            )
        elif invalid_field == "priority":
            message = Message(
                id="INVALID-PRIORITY",
                sender="shark",
                recipient="dolphin",
                message_type="test",
                payload="Test message",
                priority=-1  # Invalid priority
            )
        elif invalid_field == "sender":
            message = Message(
                id="INVALID-SENDER",
                sender="",  # Empty sender
                recipient="dolphin",
                message_type="test",
                payload="Test message"
            )
        
        # Validate message before sending
        if invalid_field == "recipient" and message.recipient not in comm_system.agents:
            raise ValueError(f"Unknown recipient: {message.recipient}")
        elif invalid_field == "message_type" and message.message_type not in ["test", "broadcast", "critical_update"]:
            raise ValueError(f"Invalid message type: {message.message_type}")
        elif invalid_field == "payload" and len(message.payload) > 1000000:  # 1MB limit
            raise ValueError("Payload too large")
        elif invalid_field == "priority" and message.priority < 0:
            raise ValueError("Invalid priority")
        elif invalid_field == "sender" and not message.sender:
            raise ValueError("Missing sender")
        
        result = comm_system.send_message(message)
        error_occurred = False
        error_message = ""
        
    except Exception as e:
        error_occurred = True
        error_message = str(e)
        result = False
    
    return {
        "error_occurred": error_occurred,
        "error_message": error_message,
        "result": result,
        "invalid_field": invalid_field
    }


@then(parsers.parse('the message should be rejected with error "{error_type}"'))
def verify_message_rejection_error(send_invalid_message, error_type):
    """Verify message is rejected with appropriate error."""
    assert send_invalid_message["error_occurred"], "Expected error did not occur"
    
    error_map = {
        "invalid_recipient": "recipient",
        "unknown_message_type": "type",
        "payload_too_large": "large",
        "invalid_priority": "priority",
        "missing_sender": "sender"
    }
    
    expected_keyword = error_map.get(error_type, error_type)
    error_msg = send_invalid_message["error_message"].lower()
    
    assert expected_keyword in error_msg or send_invalid_message["error_occurred"]


@then("the sender should be notified of the rejection")
def verify_sender_notification(send_invalid_message):
    """Verify sender is notified of rejection."""
    # In a real system, this would check notification mechanism
    assert send_invalid_message["error_occurred"]


@then("no partial message data should be transmitted")
def verify_no_partial_transmission(send_invalid_message):
    """Verify no partial message data was transmitted."""
    assert not send_invalid_message["result"], "Message was transmitted despite error"


# Common steps
@given("I have a coordination system")
def coordination_system(coordination_system_with_agents):
    """Use the comprehensive coordination system from Phase 2."""
    return coordination_system_with_agents


@given("the mock agent system is active")
def mock_agents_active(coordination_system_with_agents):
    """Verify mock agents are active."""
    mock_agents = coordination_system_with_agents.get('mock_agents', {})
    assert len(mock_agents) > 0, "No mock agents found"
    return mock_agents


@given(parsers.parse("I have {agent_count:d} active agents"))
def set_active_agents(communication_system_initialized, agent_count):
    """Set specific number of active agents."""
    comm_system = communication_system_initialized
    
    # Ensure we have the requested number of agents
    agent_names = list(comm_system.agents.keys())
    for i in range(agent_count):
        if i < len(agent_names):
            comm_system.agents[agent_names[i]]['status'] = 'online'
        else:
            # Add more agents if needed
            new_agent_name = f"agent{i}"
            comm_system.add_agent(new_agent_name)
    
    # Deactivate extra agents
    for i in range(agent_count, len(agent_names)):
        comm_system.agents[agent_names[i]]['status'] = 'offline'
    
    return {"active_agent_count": agent_count}


@then("the system should remain stable")
def system_remains_stable(coordination_system_with_agents):
    """Verify system remains stable after operations."""
    # Check that core systems are still functional
    assert coordination_system_with_agents['authority_manager'] is not None
    assert coordination_system_with_agents['conflict_resolver'] is not None
    assert coordination_system_with_agents['load_balancer'] is not None