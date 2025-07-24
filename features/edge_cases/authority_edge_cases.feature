Feature: Authority Assignment Edge Cases
  As a coordination system
  I want to handle edge cases in authority assignment
  So that the system remains stable under all conditions

  Background:
    Given I have a coordination system
    And the mock agent system is active

  @authority @edge_case
  Scenario Outline: Authority assignment with varying agent availability
    Given I have <agent_count> active agents
    And each agent has <workload>% current workload
    When I request <authority_count> authority assignments
    Then <success_rate>% should be assigned successfully
    And the system should remain stable

    @normal_load
    Examples: Normal Load Conditions
      | agent_count | workload | authority_count | success_rate |
      | 6          | 30       | 10              | 100          |
      | 6          | 60       | 15              | 90           |
      | 6          | 80       | 20              | 70           |

    @high_load
    Examples: High Load Conditions
      | agent_count | workload | authority_count | success_rate |
      | 6          | 95       | 30              | 40           |
      | 6          | 100      | 25              | 20           |

  @authority @edge_case @critical
  Scenario: All agents busy - authority queuing
    Given I have 6 active agents
    And all agents are at 100% workload
    When I request authority assignment for "Critical Security Task"
    Then the authority should be queued
    And I should receive a queuing notification
    And the system should estimate wait time

  @authority @edge_case @failure
  Scenario: Agent goes offline during authority assignment
    Given I have 6 active agents
    And I am assigning authority to "shark"
    When "shark" goes offline during assignment
    Then the authority should be reassigned automatically
    And the system should log the failure
    And no data should be corrupted

  @authority @edge_case @conflict
  Scenario: Authority conflict during assignment
    Given I have 2 agents: "shark" and "dolphin"
    And both agents are qualified for "security" domain
    When I assign the same critical authority to both agents simultaneously
    Then only one agent should receive the authority
    And the other should receive a conflict notification
    And the system should resolve the conflict deterministically

  @authority @edge_case @invalid_input
  Scenario Outline: Invalid authority request handling
    Given I have a coordination system
    When I request authority for "<invalid_request>"
    Then I should receive an error message containing "<error_type>"
    And the system should remain stable

    Examples: Invalid Inputs
      | invalid_request          | error_type           |
      | ""                      | empty_description    |
      | "x" * 10000            | description_too_long |
      | "INVALID_DOMAIN"        | invalid_domain       |

  @authority @edge_case @timeout
  Scenario: Authority assignment timeout
    Given I have an agent "slow_agent" with high latency
    And the authority assignment timeout is set to 5 seconds
    When I request authority assignment to "slow_agent"
    And the assignment takes 10 seconds to respond
    Then the assignment should timeout
    And the authority should be reassigned to another agent
    And "slow_agent" should be marked as potentially unreliable

  @authority @edge_case @capacity
  Scenario: System capacity limits
    Given I have 6 active agents
    And the system authority limit is 50 concurrent authorities
    When I have 50 active authorities
    And I request 10 additional authority assignments
    Then 0 new authorities should be assigned
    And I should receive capacity limit notifications
    And the system should suggest waiting or prioritization

  @authority @edge_case @priority
  Scenario: Emergency authority override
    Given I have 6 active agents with normal workloads
    And there are 20 pending authority requests
    When an emergency authority request is submitted
    Then the emergency request should jump to the front of the queue
    And lower priority requests should be delayed
    And all agents should be notified of the emergency

  @authority @edge_case @network
  Scenario: Network partition during authority assignment
    Given I have 6 active agents across 2 network zones
    And zone A has agents: "shark", "dolphin", "whale"
    And zone B has agents: "octopus", "jellyfish", "seahorse"
    When the network between zones is partitioned
    And I request authority assignment for a cross-zone task
    Then the authority should be assigned within the available zone
    And cross-zone coordination should be deferred
    And the system should track the partition state

  @authority @edge_case @recovery
  Scenario: Authority recovery after system restart
    Given I have 6 active agents with assigned authorities
    And the coordination system is restarted
    When the system comes back online
    Then all previously assigned authorities should be restored
    And agent workload calculations should be accurate
    And no authorities should be lost or duplicated