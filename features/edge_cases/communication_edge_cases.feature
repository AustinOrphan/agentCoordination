Feature: Communication Edge Cases
  As a coordination system
  I want to handle edge cases in inter-agent communication
  So that agents can coordinate effectively under all network and system conditions

  Background:
    Given I have a coordination system
    And the mock agent system is active
    And the communication channels are initialized

  @communication @edge_case
  Scenario Outline: Communication with varying network conditions
    Given I have <agent_count> active agents
    And the network has <latency>ms latency and <packet_loss>% packet loss
    When I send <message_count> messages of size <message_size>KB
    Then <delivery_rate>% of messages should be delivered
    And the average delivery time should be under <max_delivery_time>ms
    And the system should handle retries appropriately

    @normal_network
    Examples: Normal Network Conditions
      | agent_count | latency | packet_loss | message_count | message_size | delivery_rate | max_delivery_time |
      | 6          | 10      | 0           | 100           | 1            | 100           | 50                |
      | 6          | 50      | 1           | 200           | 10           | 99            | 200               |
      | 6          | 100     | 2           | 500           | 50           | 98            | 500               |

    @degraded_network
    Examples: Degraded Network Conditions
      | agent_count | latency | packet_loss | message_count | message_size | delivery_rate | max_delivery_time |
      | 6          | 500     | 5           | 100           | 100          | 95            | 2000              |
      | 6          | 1000    | 10          | 50            | 500          | 90            | 5000              |

  @communication @edge_case @critical
  Scenario: Message queue overflow during high traffic
    Given I have 6 active agents
    And each agent has a message queue capacity of 1000
    When 10000 messages are sent within 10 seconds
    Then the system should activate flow control
    And high priority messages should be preserved
    And low priority messages may be dropped with notifications
    And agents should receive overflow warnings
    And the system should recover gracefully after traffic subsides

  @communication @edge_case @ordering
  Scenario: Message ordering under concurrent sends
    Given I have agents "shark", "dolphin", and "whale"
    When "shark" sends 5 sequential messages to "dolphin"
    And "whale" sends 5 sequential messages to "dolphin" simultaneously
    Then each sender's messages should arrive in order
    And the system should handle interleaving correctly
    And message timestamps should reflect actual order
    And no messages should be lost or duplicated

  @communication @edge_case @broadcast_failure
  Scenario: Broadcast message with partial delivery
    Given I have 6 active agents
    And agents "octopus" and "jellyfish" have network issues
    When "shark" broadcasts a critical update to all agents
    Then 4 agents should receive the message immediately
    And the system should detect the failed deliveries
    And retry delivery to unreachable agents
    And track acknowledgments from all recipients
    And provide delivery status report to sender

  @communication @edge_case @invalid_message
  Scenario Outline: Invalid message handling
    Given I have a coordination system
    When an agent sends a message with "<invalid_field>" as "<invalid_value>"
    Then the message should be rejected with error "<error_type>"
    And the sender should be notified of the rejection
    And no partial message data should be transmitted

    Examples: Invalid Message Data
      | invalid_field | invalid_value    | error_type          |
      | recipient     | "unknown_agent"  | invalid_recipient   |
      | message_type  | "invalid_type"   | unknown_message_type|
      | payload       | "x" * 10000000  | payload_too_large   |
      | priority      | -1               | invalid_priority    |
      | sender        | ""               | missing_sender      |

  @communication @edge_case @encryption_failure
  Scenario: Message encryption/decryption failures
    Given I have secure communication enabled between agents
    And "shark" has an outdated encryption key
    When "dolphin" sends an encrypted message to "shark"
    Then "shark" should fail to decrypt the message
    And request a key refresh from the coordination system
    And the message should be re-encrypted with the new key
    And delivered successfully after key synchronization

  @communication @edge_case @agent_disconnection
  Scenario: Agent disconnects during message exchange
    Given I have a multi-step message exchange between "shark" and "dolphin"
    And they are on step 3 of 5 in the protocol
    When "dolphin" unexpectedly disconnects
    Then "shark" should detect the disconnection within 30 seconds
    And store the partial exchange state
    And attempt to resume when "dolphin" reconnects
    And complete the exchange from the last successful step

  @communication @edge_case @circular_messaging
  Scenario: Circular message forwarding detection
    Given I have 4 agents in a communication chain
    When a message is forwarded in a circle:
      | sender   | recipient | action  |
      | shark    | dolphin   | forward |
      | dolphin  | whale     | forward |
      | whale    | octopus   | forward |
      | octopus  | shark     | forward |
    Then the system should detect the circular forwarding
    And break the loop after one complete cycle
    And log the circular path for debugging
    And notify involved agents of the loop

  @communication @edge_case @priority_inversion
  Scenario: Message priority inversion in congested network
    Given I have 6 active agents with congested communication channels
    And there are 100 low priority messages in transit
    When 5 emergency priority messages are sent
    Then emergency messages should bypass the queue
    And be delivered within 100ms despite congestion
    And low priority messages should be delayed but not lost
    And the system should prevent priority starvation

  @communication @edge_case @multicast_groups
  Scenario: Dynamic multicast group management
    Given I have agents organized in multicast groups:
      | group       | members                          |
      | security    | shark, octopus                   |
      | frontend    | dolphin, seahorse                |
      | backend     | whale, jellyfish                 |
    When "shark" leaves the security group during a multicast
    And "dolphin" joins the security group simultaneously
    Then the multicast should complete with the original members
    And subsequent multicasts should use the updated membership
    And group changes should be atomic and consistent

  @communication @edge_case @message_replay
  Scenario: Message replay attack prevention
    Given I have secure communication with message sequence numbers
    When an attacker attempts to replay a captured message from "shark"
    Then the system should detect the duplicate sequence number
    And reject the replayed message
    And alert both sender and intended recipient
    And log the security incident for analysis

  @communication @edge_case @bandwidth_throttling
  Scenario: Adaptive bandwidth throttling
    Given I have 6 active agents sharing limited bandwidth
    And total available bandwidth is 10MB/s
    When one agent "whale" starts consuming 8MB/s
    Then the system should detect the bandwidth hogging
    And throttle "whale" to a fair share (2MB/s)
    And distribute remaining bandwidth fairly
    And adjust throttling dynamically as usage changes

  @communication @edge_case @message_fragmentation
  Scenario: Large message fragmentation and reassembly
    Given I have agents "shark" and "dolphin"
    And the maximum message size is 64KB
    When "shark" sends a 1MB message to "dolphin"
    Then the message should be fragmented into 16 parts
    And each fragment should be transmitted independently
    And "dolphin" should reassemble fragments correctly
    And handle out-of-order fragment delivery
    And request retransmission of missing fragments

  @communication @edge_case @protocol_mismatch
  Scenario: Communication protocol version mismatch
    Given I have agents running different protocol versions:
      | agent    | protocol_version |
      | shark    | 2.0             |
      | dolphin  | 1.5             |
      | whale    | 2.0             |
    When agents attempt to communicate across versions
    Then the system should negotiate compatible protocol features
    And use the highest common version capabilities
    And warn about deprecated features
    And maintain backward compatibility

  @communication @edge_case @deadlock_prevention
  Scenario: Communication deadlock prevention
    Given I have 4 agents in potential deadlock scenario:
      | agent   | waiting_for_response_from | holding_resource |
      | shark   | dolphin                   | database_lock    |
      | dolphin | whale                     | file_lock        |
      | whale   | octopus                   | network_lock     |
      | octopus | shark                     | memory_lock      |
    When all agents send synchronous requests simultaneously
    Then the system should detect the potential deadlock
    And break the deadlock using timeout mechanisms
    And force asynchronous communication patterns
    And log the deadlock scenario for prevention

  @communication @edge_case @system_recovery
  Scenario: Communication state recovery after system restart
    Given I have 6 active agents with ongoing communications:
      | type              | count | state      |
      | pending_messages  | 200   | queued     |
      | active_exchanges  | 50    | in_progress|
      | multicast_groups  | 10    | active     |
    And the coordination system is restarted
    When the system comes back online
    Then all pending messages should be recovered from persistent queue
    And active exchanges should resume from last checkpoint
    And multicast group memberships should be restored
    And no communication data should be lost or corrupted