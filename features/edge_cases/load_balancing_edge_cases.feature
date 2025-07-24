Feature: Load Balancing Edge Cases
  As a coordination system
  I want to handle edge cases in load balancing
  So that tasks are efficiently distributed and the system remains stable under all conditions

  Background:
    Given I have a coordination system
    And the mock agent system is active
    And the load balancer is initialized

  @load_balancing @edge_case
  Scenario Outline: Load balancing with varying strategies and loads
    Given I have <agent_count> active agents
    And each agent has <current_load>% current workload
    When I assign <task_count> tasks using <strategy> strategy
    And each task has <priority> priority
    Then the tasks should be distributed with <efficiency>% efficiency
    And no agent should exceed <max_load>% workload
    And the system should remain stable

    @normal_distribution
    Examples: Normal Distribution Scenarios
      | agent_count | current_load | task_count | strategy           | priority | efficiency | max_load |
      | 6          | 20           | 30         | round_robin        | medium   | 90         | 80       |
      | 6          | 40           | 50         | least_connections  | medium   | 85         | 90       |
      | 6          | 60           | 40         | resource_aware     | high     | 80         | 95       |

    @high_load_distribution
    Examples: High Load Distribution Scenarios
      | agent_count | current_load | task_count | strategy           | priority | efficiency | max_load |
      | 6          | 80           | 60         | expertise_based    | critical | 70         | 100      |
      | 6          | 90           | 100        | adaptive           | emergency| 60         | 100      |

  @load_balancing @edge_case @critical
  Scenario: All agents at capacity - task queuing
    Given I have 6 active agents
    And all agents are at 100% workload capacity
    When I submit 20 new critical priority tasks
    Then all tasks should be queued properly
    And tasks should be ordered by priority within the queue
    And I should receive queue position notifications
    And the system should estimate completion times

  @load_balancing @edge_case @agent_failure
  Scenario: Agent goes offline during task assignment
    Given I have 6 active agents using round_robin strategy
    And I am assigning a critical task to "shark"
    When "shark" goes offline during task assignment
    Then the task should be automatically reassigned to the next available agent
    And the load balancing rotation should skip the offline agent
    And the system should log the failure and reassignment
    And no tasks should be lost

  @load_balancing @edge_case @strategy_switching
  Scenario: Dynamic strategy switching under load
    Given I have 6 active agents using adaptive strategy
    And the system is under normal load (40% average)
    When the system load increases to 90% average
    Then the load balancer should automatically switch to resource_aware strategy
    And existing task assignments should not be disrupted
    And new tasks should use the updated strategy
    And the strategy change should be logged

  @load_balancing @edge_case @invalid_input
  Scenario Outline: Invalid task assignment requests
    Given I have a coordination system
    When I submit a task with "<invalid_field>" as "<invalid_value>"
    Then I should receive an error message containing "<error_type>"
    And the system should remain stable
    And no partial task data should be stored

    Examples: Invalid Task Data
      | invalid_field          | invalid_value     | error_type           |
      | task_id               | ""                | missing_task_id      |
      | domain                | "unknown_domain"  | invalid_domain       |
      | priority              | 10                | invalid_priority     |
      | estimated_duration    | -5                | negative_duration    |
      | resource_requirements | "invalid_json"    | malformed_resources  |

  @load_balancing @edge_case @expertise_mismatch
  Scenario: No agents with required expertise
    Given I have 6 active agents
    And no agents have "quantum_computing" expertise
    When I assign a task requiring "quantum_computing" domain expertise
    Then the system should detect the expertise gap
    And either queue the task for future skilled agents
    Or assign to the most closely related expertise ("security" or "backend")
    And log the expertise mismatch for capacity planning
    And notify administrators of the skill gap

  @load_balancing @edge_case @resource_constraints
  Scenario: Task requires more resources than any single agent has
    Given I have 6 active agents
    And each agent has maximum 4GB memory capacity
    When I assign a task requiring 8GB memory
    Then the system should detect the resource constraint violation
    And either split the task into smaller subtasks
    Or schedule the task for when resources become available
    And suggest scaling up agent resources
    And log the resource constraint for capacity planning

  @load_balancing @edge_case @priority_inversion
  Scenario: Priority inversion in task queue
    Given I have 6 active agents at 95% capacity
    And there are 50 low priority tasks in the queue
    When 5 emergency priority tasks are submitted
    Then the emergency tasks should jump to the front of the queue
    And lower priority tasks should be delayed accordingly
    And the system should prevent starvation of low priority tasks
    And priority aging should be applied after 24 hours

  @load_balancing @edge_case @cascading_failures
  Scenario: Cascading agent failures during high load
    Given I have 6 active agents at 80% capacity each
    When 3 agents fail simultaneously due to external issues
    Then the remaining 3 agents should absorb the redistributed load
    And the system should prevent overloading the surviving agents
    And emergency load shedding should be activated if needed
    And administrator alerts should be triggered
    And task queue priorities should be automatically adjusted

  @load_balancing @edge_case @circular_dependencies
  Scenario: Task with circular dependencies
    Given I have 6 active agents
    When I submit tasks with circular dependencies:
      | task_id | depends_on |
      | TASK-A  | TASK-B     |
      | TASK-B  | TASK-C     |
      | TASK-C  | TASK-A     |
    Then the system should detect the circular dependency
    And reject the task submission with appropriate error
    And suggest dependency resolution strategies
    And no tasks should be partially assigned

  @load_balancing @edge_case @rapid_submissions
  Scenario: Rapid task submission burst
    Given I have 6 active agents
    When 1000 tasks are submitted within 10 seconds
    Then the system should handle the submission burst gracefully
    And implement rate limiting if necessary
    And maintain task ordering and priority
    And not overwhelm the assignment algorithm
    And provide feedback on submission queue status

  @load_balancing @edge_case @agent_heterogeneity
  Scenario: Extreme agent capability differences
    Given I have agents with vastly different capabilities:
      | agent    | cpu_cores | memory_gb | expertise_domains | max_concurrent_tasks |
      | shark    | 16        | 64        | security,backend  | 50                   |
      | dolphin  | 2         | 8         | frontend          | 5                    |
      | whale    | 32        | 128       | infrastructure    | 100                  |
      | octopus  | 4         | 16        | fullstack         | 20                   |
    When I assign 200 mixed tasks across all domains
    Then the load balancer should account for capability differences
    And distribute tasks proportionally to agent capabilities
    And prevent overwhelming weaker agents
    And maximize utilization of powerful agents

  @load_balancing @edge_case @task_cancellation
  Scenario: Task cancellation during assignment process
    Given I have 6 active agents
    And I am assigning a task "LONG-TASK" to "shark"
    When the task is cancelled mid-assignment
    Then the assignment process should be cleanly terminated
    And agent resources should be properly released
    And the task should be removed from all queues
    And no orphaned task state should remain
    And the agent should be notified of the cancellation

  @load_balancing @edge_case @system_recovery
  Scenario: Load balancer state recovery after system restart
    Given I have 6 active agents with assigned tasks
    And there are 100 queued tasks in various priority levels
    And the coordination system is restarted
    When the system comes back online
    Then all task queues should be restored from persistent storage
    And agent workload states should be accurately recovered
    And load balancing should resume without disruption
    And no tasks should be lost, duplicated, or corrupted