#!/usr/bin/env python3
"""
Example: How agents communicate using the new bidirectional messaging system
"""

import sys
import time
sys.path.append('../coordination_system')

from agent_communication import (
    CommunicationChannel, Message, MessageType, 
    Priority, AgentStatus
)

def agent_alpha_example():
    """Example code for Agent Alpha"""
    print("=== Agent Alpha Example ===\n")
    
    # Initialize communication channel
    channel = CommunicationChannel("alpha")
    
    # 1. Send initial heartbeat
    print("1. Sending heartbeat...")
    channel.send_heartbeat(
        status=AgentStatus.WORKING,
        current_task="Implementing core integration",
        metrics={"cpu_usage": 45, "memory_usage": 512}
    )
    print("✓ Heartbeat sent\n")
    
    # 2. Send status update to central
    print("2. Sending status update...")
    status_msg = Message(
        from_id="alpha",
        to_id="central",
        msg_type=MessageType.STATUS_UPDATE,
        payload={
            "task_id": "task_001",
            "status": "in_progress",
            "progress": 50,
            "message": "Completed database schema design"
        }
    )
    channel.send_message(status_msg)
    print("✓ Status update sent\n")
    
    # 3. Request information from Beta
    print("3. Requesting info from Agent Beta...")
    info_request = Message(
        from_id="alpha",
        to_id="beta",
        msg_type=MessageType.INFO_REQUEST,
        payload={
            "request_id": "req_001",
            "question": "What migration tools are you planning to use?",
            "context": "Need to ensure compatibility with core integration",
            "deadline": "2024-01-01T14:00:00Z"
        }
    )
    channel.send_message(info_request)
    print("✓ Information request sent\n")
    
    # 4. Check inbox for messages
    print("4. Checking inbox for new messages...")
    messages = channel.receive_messages()
    
    if messages:
        print(f"Found {len(messages)} messages:")
        for msg in messages:
            print(f"  - {msg.type} from {msg.from_id}")
            print(f"    Payload: {msg.payload}")
            
            # Acknowledge if required
            if msg.requires_ack:
                channel.acknowledge_message(msg)
                print(f"    ✓ Acknowledged message {msg.id}")
    else:
        print("No new messages\n")
    
    print("\n✓ Agent Alpha example complete")

def agent_beta_example():
    """Example code for Agent Beta"""
    print("\n=== Agent Beta Example ===\n")
    
    # Initialize communication channel
    channel = CommunicationChannel("beta")
    
    # 1. Report a blocker
    print("1. Reporting a blocker...")
    blocker_msg = Message(
        from_id="beta",
        to_id="central",
        msg_type=MessageType.BLOCKER_REPORT,
        payload={
            "blocker_id": "block_001",
            "task_id": "task_002",
            "description": "Waiting for database schema from Alpha",
            "blocking_agent": "alpha",
            "severity": "high"
        }
    )
    channel.send_message(blocker_msg)
    print("✓ Blocker reported\n")
    
    # 2. Check for messages (should receive Alpha's request)
    print("2. Checking inbox...")
    messages = channel.receive_messages()
    
    for msg in messages:
        if msg.type == MessageType.INFO_REQUEST.value:
            print(f"Received info request from {msg.from_id}:")
            print(f"Question: {msg.payload['question']}")
            
            # Send response
            print("\n3. Sending response...")
            response = Message(
                from_id="beta",
                to_id=msg.from_id,
                msg_type=MessageType.INFO_RESPONSE,
                payload={
                    "request_id": msg.payload["request_id"],
                    "answer": "Planning to use Alembic for database migrations with custom adapters",
                    "additional_notes": "See migration_tools.md for details"
                },
                correlation_id=msg.id
            )
            channel.send_message(response)
            print("✓ Response sent")
            
            # Acknowledge the request
            if msg.requires_ack:
                channel.acknowledge_message(msg)
    
    print("\n✓ Agent Beta example complete")

def central_dispatcher_example():
    """Example of central message routing"""
    print("\n=== Central Dispatcher Example ===\n")
    
    from agent_communication import CentralDispatcher
    
    # Initialize dispatcher
    dispatcher = CentralDispatcher()
    
    print("Routing messages between agents...")
    routed = dispatcher.route_messages()
    print(f"✓ Routed {routed} messages\n")
    
    # Get all agent statuses
    print("Current agent statuses:")
    statuses = dispatcher.get_agent_statuses()
    
    for agent_id, status in statuses.items():
        if status["heartbeat"]:
            print(f"  {agent_id}: {status['heartbeat']['payload']['status']}")
            last_seen = status['heartbeat']['timestamp']
            print(f"    Last seen: {last_seen}")

def main():
    """Run the examples"""
    print("Agent Communication System Examples")
    print("==================================\n")
    
    # Simulate Alpha sending messages
    agent_alpha_example()
    
    # Simulate message routing
    time.sleep(1)
    central_dispatcher_example()
    
    # Simulate Beta receiving and responding
    time.sleep(1)
    agent_beta_example()
    
    # Route messages again to deliver Beta's response
    time.sleep(1)
    print("\n=== Final Message Routing ===")
    central_dispatcher_example()
    
    print("\n✓ All examples complete!")
    print("\nTo use in your agent:")
    print("1. Import: from coordination_system.agent_communication import CommunicationChannel")
    print("2. Initialize: channel = CommunicationChannel('your_agent_id')")
    print("3. Check messages: messages = channel.receive_messages()")
    print("4. Send updates: channel.send_message(message)")
    print("5. Send heartbeats: channel.send_heartbeat(status, task)")

if __name__ == "__main__":
    main()