Feature: Conflict Resolution Edge Cases
  As a coordination system
  I want to handle edge cases in conflict resolution
  So that the system can resolve disputes and maintain stability under all conditions

  Background:
    Given I have a coordination system
    And the mock agent system is active
    And the conflict resolution system is initialized

  @conflict @edge_case
  Scenario Outline: Conflict resolution with varying complexity
    Given I have <agent_count> active agents
    And there are <existing_conflicts> existing conflicts
    When I report a <conflict_type> conflict with <severity> severity
    Then the conflict should be resolved within <max_resolution_time> seconds
    And the resolution should have <success_rate>% success rate
    And the system should remain stable

    @normal_complexity
    Examples: Normal Complexity Conflicts
      | agent_count | existing_conflicts | conflict_type       | severity | max_resolution_time | success_rate |
      | 6          | 0                  | priority_conflict   | low      | 30                  | 95           |
      | 6          | 2                  | task_overlap        | medium   | 60                  | 90           |
      | 6          | 5                  | resource_contention | high     | 120                 | 85           |

    @high_complexity
    Examples: High Complexity Conflicts
      | agent_count | existing_conflicts | conflict_type       | severity | max_resolution_time | success_rate |
      | 6          | 10                 | authority_dispute   | critical | 300                 | 70           |
      | 6          | 15                 | voting_deadlock     | critical | 600                 | 60           |

  @conflict @edge_case @critical
  Scenario: Cascading conflict chain
    Given I have 6 active agents
    And "shark" and "dolphin" have a resource_contention conflict
    When the resource conflict triggers an authority_dispute between "whale" and "octopus"
    And the authority dispute causes a deadline_conflict for "jellyfish"
    Then all three conflicts should be tracked separately
    And the system should identify the cascading relationship
    And conflicts should be resolved in dependency order
    And the root cause should be identified

  @conflict @edge_case @simultaneous
  Scenario: Multiple simultaneous conflicts
    Given I have 6 active agents
    When 5 different conflicts are reported simultaneously
      | agent1  | agent2    | conflict_type       | severity |
      | shark   | dolphin   | resource_contention | high     |
      | whale   | octopus   | authority_dispute   | critical |
      | jellyfish| seahorse | task_overlap        | medium   |
      | shark   | whale     | priority_conflict   | high     |
      | dolphin | jellyfish | expertise_dispute   | low      |
    Then all conflicts should be registered
    And critical conflicts should be prioritized
    And no conflict should be lost or duplicated
    And the system should handle the load gracefully

  @conflict @edge_case @resolution_failure
  Scenario: Conflict resolution failure and escalation
    Given I have a critical authority_dispute between "shark" and "dolphin"
    And the primary resolution mechanism fails
    When the automatic retry also fails
    Then the conflict should be escalated to emergency resolution
    And a human intervention request should be generated
    And the system should log the failure details
    And affected agents should be notified of the escalation

  @conflict @edge_case @invalid_input
  Scenario Outline: Invalid conflict reporting
    Given I have a coordination system
    When I report a conflict with "<invalid_field>" as "<invalid_value>"
    Then I should receive an error message containing "<error_type>"
    And the system should remain stable
    And no partial conflict data should be stored

    Examples: Invalid Conflict Data
      | invalid_field    | invalid_value        | error_type           |
      | conflict_type    | "unknown_type"       | invalid_conflict_type|
      | severity         | "extreme"            | invalid_severity     |
      | reporting_agent  | ""                   | missing_reporter     |
      | description      | "x" * 10000         | description_too_long |
      | parties          | []                   | no_parties           |

  @conflict @edge_case @agent_offline
  Scenario: Conflict party goes offline during resolution
    Given I have a resource_contention conflict between "shark" and "dolphin"
    And the resolution process has started
    When "dolphin" goes offline during resolution
    Then the system should detect the offline status
    And attempt to resolve with available information
    And mark the resolution as "partial_resolution"
    And schedule re-evaluation when "dolphin" comes back online

  @conflict @edge_case @timeout
  Scenario: Conflict resolution timeout
    Given I have a complex voting_deadlock conflict
    And the resolution timeout is set to 300 seconds
    When the resolution process takes 400 seconds
    Then the resolution should timeout
    And the conflict should be escalated to manual intervention
    And participating agents should be notified of the timeout
    And the system should log timeout details for analysis

  @conflict @edge_case @rapid_sequence
  Scenario: Rapid conflict sequence from same agents
    Given I have agents "shark" and "dolphin"
    When "shark" reports 10 conflicts with "dolphin" within 30 seconds
    And the conflicts are of type priority_conflict with low severity
    Then the system should detect the rapid sequence
    And consolidate related conflicts into a single resolution session
    And apply rate limiting to prevent spam
    And notify both agents of the consolidation

  @conflict @edge_case @resolution_rejection
  Scenario: Agent rejects conflict resolution
    Given I have a task_overlap conflict between "shark" and "dolphin"
    And the system proposes a resolution
    When "shark" rejects the proposed resolution
    And provides a counter-proposal
    Then the system should enter negotiation mode
    And attempt to find a mutually acceptable solution
    And track rejection reasons for learning
    And escalate if no agreement is reached within 3 rounds

  @conflict @edge_case @cross_domain
  Scenario: Cross-domain expertise conflict
    Given I have agents specialized in different domains
    And "shark" (security expert) conflicts with "dolphin" (frontend expert)
    When they dispute the approach for a full-stack security feature
    Then the system should identify the cross-domain nature
    And involve agents with overlapping expertise
    And weight opinions based on domain relevance
    And create a balanced resolution considering both perspectives

  @conflict @edge_case @voting_system
  Scenario: Voting system edge cases
    Given I have 6 active agents
    And a voting_deadlock conflict requires agent voting
    When the voting results in a perfect tie (3-3)
    And the tie-breaking agent "whale" abstains
    Then the system should detect the persistent deadlock
    And apply hierarchical tie-breaking rules
    And escalate to authority-based resolution if needed
    And document the voting pattern for future reference

  @conflict @edge_case @resource_cleanup
  Scenario: Resource cleanup after conflict resolution
    Given I have a resource_contention conflict over "database_connection_pool"
    And the conflict is resolved by allocating resources to "shark"
    When the resolution is complete
    Then any temporarily allocated resources should be cleaned up
    And resource locks should be properly released
    And the resource state should be consistent
    And no orphaned resources should remain

  @conflict @edge_case @historical_data
  Scenario: Conflict resolution using historical data
    Given I have agents "shark" and "dolphin" with previous conflict history
    And they previously had 3 resolved resource_contention conflicts
    When they have a new authority_dispute conflict
    Then the system should consider their conflict history
    And apply learned patterns from previous resolutions
    And adjust resolution strategy based on past success rates
    And document new patterns for future use

  @conflict @edge_case @system_recovery
  Scenario: Conflict state recovery after system restart
    Given I have 5 active conflicts in various resolution stages
    And the coordination system is restarted
    When the system comes back online
    Then all active conflicts should be restored from persistent storage
    And resolution states should be accurately recovered
    And agents should be re-notified of pending conflicts
    And no conflict data should be lost or corrupted