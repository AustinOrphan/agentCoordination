# Agent Communication Protocol

## Overview

This document defines the bidirectional communication protocol between the central coordination system and individual agents using file-based message passing.

## File Structure

Each agent has dedicated communication channels:

```
agent_communication/
├── <agent_name>/
│   ├── input/           # Messages TO the agent
│   │   ├── inbox.json   # Current unread messages
│   │   └── archive/     # Processed messages
│   ├── output/          # Messages FROM the agent
│   │   ├── outbox.json  # Pending messages
│   │   └── sent/        # Delivered messages
│   └── status/
│       ├── lifecycle.json    # Running/stopped/blocked status
│       └── heartbeat.json    # Last activity timestamp
```

## Message Format

### Standard Message Structure
```json
{
  "id": "unique_message_id",
  "timestamp": "2024-01-01T12:00:00Z",
  "from": "sender_id",
  "to": "recipient_id",
  "type": "message_type",
  "priority": "high|normal|low",
  "payload": {},
  "requires_ack": true,
  "correlation_id": "original_message_id"
}
```

### Message Types

#### 1. Task Assignment (Central → Agent)
```json
{
  "type": "task_assignment",
  "payload": {
    "task_id": "task_123",
    "title": "Implement feature X",
    "description": "Detailed task description",
    "dependencies": ["task_100", "task_101"],
    "priority": "high",
    "estimated_hours": 4
  }
}
```

#### 2. Status Update (Agent → Central)
```json
{
  "type": "status_update",
  "payload": {
    "task_id": "task_123",
    "status": "in_progress",
    "progress": 75,
    "message": "Completed unit tests, working on integration",
    "eta": "2024-01-01T16:00:00Z"
  }
}
```

#### 3. Blocker Report (Agent → Central)
```json
{
  "type": "blocker_report",
  "payload": {
    "blocker_id": "block_456",
    "task_id": "task_123",
    "description": "Waiting for API documentation from Agent Beta",
    "blocking_agent": "beta",
    "severity": "high"
  }
}
```

#### 4. Blocker Resolution (Central → Agent)
```json
{
  "type": "blocker_resolved",
  "payload": {
    "blocker_id": "block_456",
    "resolution": "API documentation now available",
    "resolved_by": "beta",
    "resources": ["link_to_docs"]
  }
}
```

#### 5. Information Request (Agent → Agent via Central)
```json
{
  "type": "info_request",
  "payload": {
    "request_id": "req_789",
    "question": "What is the database schema for user profiles?",
    "context": "Needed for migration task",
    "requested_from": "alpha",
    "deadline": "2024-01-01T14:00:00Z"
  }
}
```

#### 6. Information Response (Agent → Agent via Central)
```json
{
  "type": "info_response",
  "payload": {
    "request_id": "req_789",
    "answer": "Schema details...",
    "attachments": ["schema.sql"],
    "additional_notes": "See also the migration guide"
  }
}
```

#### 7. Lifecycle Control (Central → Agent)
```json
{
  "type": "lifecycle_control",
  "payload": {
    "action": "start|stop|pause|resume",
    "reason": "Dependencies met|Blocked|Resource constraints",
    "scheduled_time": "2024-01-01T12:00:00Z"
  }
}
```

#### 8. Heartbeat (Agent → Central)
```json
{
  "type": "heartbeat",
  "payload": {
    "status": "active|idle|working",
    "current_task": "task_123",
    "cpu_usage": 45,
    "memory_usage": 1024,
    "last_activity": "2024-01-01T11:59:00Z"
  }
}
```

## Communication Flow

### 1. Agent Startup
1. Agent creates/clears its communication directories
2. Agent sends initial heartbeat
3. Agent reads any pending messages from inbox
4. Central system detects agent is online

### 2. Task Assignment
1. Central writes task to agent's inbox.json
2. Agent polls inbox (every 10 seconds)
3. Agent acknowledges receipt
4. Agent moves message to archive
5. Agent begins work and sends status updates

### 3. Blocker Management
1. Agent detects blocker
2. Agent writes blocker report to outbox
3. Central reads outbox and updates coordination
4. Central monitors for resolution
5. When resolved, Central sends blocker_resolved message
6. Agent receives notification and resumes work

### 4. Agent Shutdown
1. Agent sends final status update
2. Agent marks lifecycle status as "stopped"
3. Agent completes any pending outbox messages
4. Central detects agent offline and manages dependencies

## File Locking Protocol

To prevent race conditions:

1. Use `.lock` files when writing
2. Atomic moves for file updates
3. Implement exponential backoff for retries
4. Maximum lock duration: 5 seconds

Example:
```bash
# Acquire lock
touch inbox.json.lock

# Write to temporary file
echo "$message" > inbox.json.tmp

# Atomic move
mv inbox.json.tmp inbox.json

# Release lock
rm inbox.json.lock
```

## Implementation Guidelines

### For Agents
1. Poll inbox every 10 seconds
2. Send heartbeat every 30 seconds
3. Acknowledge messages within 1 minute
4. Archive processed messages
5. Batch outbox messages when possible

### For Central System
1. Monitor all agent heartbeats
2. Detect blocked agents within 1 minute
3. Route inter-agent messages
4. Maintain message delivery guarantees
5. Clean up old archived messages (>7 days)

## Error Handling

1. **Lost Messages**: Implement message IDs and acknowledgments
2. **Agent Crash**: Detect via missing heartbeats
3. **File Corruption**: Validate JSON, maintain backups
4. **Deadlocks**: Implement timeout mechanisms
5. **Network Issues**: Local file system resilience

## Security Considerations

1. Validate all message payloads
2. Sanitize file paths
3. Implement message size limits (10MB)
4. Use file permissions for access control
5. Log all communication for audit