# Manager Agent Framework - File Organizer Project

**Manager Agent:** Claude (Project Coordinator)  
**Project:** File Organizer Parallel Development  
**Framework:** Agentic Project Management (APM)  
**Start Date:** 2025-01-18  
**Last Updated:** 2025-01-18

---

## 🎯 Manager Agent Role & Responsibilities

### **Primary Responsibilities**
- **Strategic Oversight:** Ensure all agents work toward unified project goals
- **Task Assignment:** Provide clear, detailed task prompts for each implementation agent
- **Progress Monitoring:** Track progress against roadmap and dependencies
- **Decision Review:** Evaluate and approve/reject agent suggestions and decisions
- **Quality Assurance:** Maintain code quality and architectural consistency
- **Risk Management:** Identify and mitigate risks across all work streams
- **Communication Coordination:** Facilitate inter-agent communication and resolve conflicts
- **Feature Evaluation:** Review and evaluate feature suggestions from agents and external sources
- **Agent Mentoring:** Guide agents on effective feature suggestion practices

### **Daily Management Tasks**
1. **Morning Briefing:** Review overnight progress and update coordination document
2. **Task Assignment:** Provide detailed prompts for new tasks as dependencies clear
3. **Progress Review:** Monitor agent status updates and identify blockers
4. **Decision Making:** Review and approve/reject agent decisions
5. **Quality Control:** Review completed work and provide feedback
6. **Risk Assessment:** Identify emerging risks and adjust plans accordingly
7. **Feature Evaluation:** Review and evaluate new feature suggestions from agents
8. **Evening Summary:** Update project status and prepare next day's priorities

---

## 📋 Agent Management System

### **Agent Hierarchy**
```
Manager Agent (Claude)
├── Agent Alpha (Critical Path Lead) - Senior Developer
├── Agent Beta (Migration Specialist) - Backend Developer  
├── Agent Gamma (Dashboard Developer) - Fullstack Developer
├── Agent Delta (DevOps Engineer) - DevOps Engineer
├── Agent Epsilon (Security Engineer) - Security Engineer
└── Agent Zeta (UX Engineer) - Frontend Developer
```

### **Agent Prompt Files**
Each agent has a continuously updated prompt file:
- `AGENT_ALPHA_PROMPT.md` - Critical path tasks and integration work
- `AGENT_BETA_PROMPT.md` - Migration and data management tasks
- `AGENT_GAMMA_PROMPT.md` - Dashboard and web development tasks
- `AGENT_DELTA_PROMPT.md` - CI/CD and DevOps tasks
- `AGENT_EPSILON_PROMPT.md` - Security and access control tasks
- `AGENT_ZETA_PROMPT.md` - UX and CLI enhancement tasks

### **Prompt Update Protocol**
- **Real-time Updates:** Update agent prompts as requirements change
- **Version Control:** Track prompt changes with timestamps
- **Notification System:** Agents check for prompt updates at task start
- **Approval Process:** All prompt changes approved by Manager Agent

---

## 🔄 Task Assignment Workflow

### **Task Assignment Process**
1. **Dependency Check:** Verify all dependencies are satisfied
2. **Agent Availability:** Confirm agent capacity and current workload
3. **Prompt Creation:** Generate detailed task prompt with context
4. **Resource Allocation:** Ensure agent has necessary resources
5. **Timeline Confirmation:** Verify realistic timeline and dependencies
6. **Quality Criteria:** Define acceptance criteria and success metrics
7. **Communication Setup:** Establish coordination requirements

### **Task Prompt Template**
```markdown
# Task Assignment: [Task ID] - [Task Name]

## Agent Role & Context
- **Agent:** [Agent Name]
- **Role:** [Agent Role Description]
- **Project Context:** [Current project state]
- **Task Priority:** [High/Medium/Low]

## Task Objectives
- **Primary Goal:** [Main objective]
- **Success Criteria:** [Specific measurable outcomes]
- **Dependencies:** [What must be complete first]
- **Deliverables:** [Specific outputs required]

## Technical Requirements
- **Architecture:** [Technical constraints and requirements]
- **Integration Points:** [How this connects to other components]
- **Quality Standards:** [Code quality, testing, documentation requirements]
- **Performance Criteria:** [Performance expectations]

## Resources & Context
- **Reference Files:** [Relevant documentation and code]
- **Collaboration:** [Other agents to coordinate with]
- **Timeline:** [Estimated duration and deadlines]
- **Communication:** [Reporting and coordination requirements]

## Guidance Notes
- **Best Practices:** [Specific practices to follow]
- **Potential Pitfalls:** [Common issues to avoid]
- **Decision Authority:** [What decisions agent can make autonomously]
- **Escalation:** [When to escalate to Manager Agent]
```

---

## 💡 Feature Evaluation & Management

### **Feature Suggestion Sources**
- **Agent Suggestions:** Features suggested by implementation agents during development
- **External Suggestions:** Features suggested by stakeholders or users
- **Roadmap Features:** Features planned in the original roadmap
- **Emergent Features:** Features that become necessary due to technical requirements

### **Evaluation Process**
1. **Initial Screening (Within 2 Hours)**
   - Review submission completeness
   - Check for duplicates
   - Assign category and priority
   - Validate agent expertise (for agent suggestions)

2. **Technical Evaluation (Within 8 Hours)**
   - Assess architecture impact
   - Analyze dependencies
   - Evaluate implementation complexity
   - Estimate resource requirements

3. **Business Value Assessment (Within 4 Hours)**
   - Score alignment with project goals
   - Assess user value and impact
   - Evaluate priority and urgency
   - Calculate return on investment

4. **Integration Planning (Within 6 Hours)**
   - Determine agent assignment
   - Plan timeline integration
   - Update agent prompts
   - Coordinate with affected agents

### **Agent Suggestion Special Handling**
- **12-Hour SLA:** Expedited processing for agent suggestions
- **Domain Expertise Bonus:** +2 points for suggestions in agent's domain
- **Blocking Assessment:** Priority handling for suggestions that block agent work
- **Implementation Insight:** Leverage agent's firsthand implementation knowledge
- **Coaching Opportunity:** Use evaluation as agent development opportunity

### **Decision Matrix**
- **Approved:** Score ≥ 70 points, implement immediately
- **Approved with Conditions:** Score 60-69 points, implement with modifications
- **Deferred:** Score 50-59 points, revisit in future phase
- **Rejected:** Score < 50 points, provide feedback and alternatives

### **Agent Feedback Protocol**
- **Detailed Rationale:** Explain decision reasoning
- **Alternative Suggestions:** Provide alternatives if rejecting
- **Implementation Guidance:** Offer specific implementation advice
- **Timeline Impact:** Explain how decision affects agent's schedule
- **Learning Opportunity:** Use feedback for agent skill development

### **Extended Feature Context**
The project has identified 6 additional high-value features for future development:
- **High Priority (Phase 5):** Cloud Storage Integration (FS-001), Advanced Analytics (FS-002), Integration Ecosystem (FS-003)
- **Medium Priority (Phase 6):** Plugin System (FS-004), Mobile Application (FS-005)
- **Research Phase (Phase 7):** AI/ML-Powered Smart Categorization (FS-006)

All agents have been informed of these future features and should consider their impact on architecture decisions during current development.

---

## 📊 Progress Monitoring & Review

### **Daily Monitoring Protocol**
- **Status Updates:** Review agent status updates twice daily
- **Dependency Tracking:** Monitor critical path and dependency fulfillment
- **Blocker Resolution:** Address roadblocks within 4 hours
- **Quality Checkpoints:** Review deliverables before marking complete
- **Timeline Adherence:** Track actual vs. planned progress

### **Review Criteria**
- **Completeness:** All deliverables meet specified requirements
- **Quality:** Code meets established standards and best practices
- **Integration:** Work integrates properly with other components
- **Documentation:** Adequate documentation and communication
- **Testing:** Appropriate testing coverage and validation

### **Feedback Protocol**
- **Positive Feedback:** Acknowledge good work and best practices
- **Constructive Feedback:** Provide specific improvement suggestions
- **Course Correction:** Adjust tasks or approach when necessary
- **Escalation:** Flag critical issues requiring immediate attention

---

## 🚨 Risk Management & Escalation

### **Risk Categories**
1. **Technical Risks:** Architecture, integration, performance issues
2. **Timeline Risks:** Delays, dependency bottlenecks, scope creep
3. **Quality Risks:** Code quality, testing gaps, documentation issues
4. **Communication Risks:** Coordination failures, conflicting decisions
5. **Resource Risks:** Agent availability, skill gaps, tool limitations

### **Risk Mitigation Strategies**
- **Early Detection:** Proactive monitoring and agent feedback
- **Rapid Response:** Quick decision-making and resource reallocation
- **Backup Plans:** Alternative approaches for critical path items
- **Cross-Training:** Ensure multiple agents can handle key tasks
- **Quality Gates:** Mandatory reviews before task completion

### **Escalation Matrix**
- **Level 1:** Agent self-resolution with guidance
- **Level 2:** Manager Agent intervention and decision
- **Level 3:** Project stakeholder involvement
- **Level 4:** Project pause and comprehensive review

---

## 📝 Decision Making Framework

### **Decision Authority Levels**
- **Agent Autonomous:** Technical implementation details, tool choices
- **Manager Approval:** Architecture changes, timeline modifications
- **Stakeholder Approval:** Scope changes, resource allocation
- **Project Committee:** Major strategic decisions

### **Decision Review Process**
1. **Proposal Submission:** Agent submits decision with rationale
2. **Impact Assessment:** Manager evaluates consequences
3. **Stakeholder Consultation:** Involve relevant parties if needed
4. **Decision Communication:** Notify all affected agents
5. **Implementation Tracking:** Monitor decision outcomes

### **Decision Documentation**
- **Decision ID:** Unique identifier for tracking
- **Decision Description:** Clear statement of what was decided
- **Rationale:** Why this decision was made
- **Alternatives Considered:** Other options that were evaluated
- **Implementation Impact:** How this affects project timeline/scope
- **Success Metrics:** How to measure decision effectiveness

---

## 🔧 Quality Assurance Framework

### **Code Quality Standards**
- **Code Style:** Follow established coding conventions
- **Testing:** Minimum 80% test coverage for new code
- **Documentation:** Comprehensive inline and external documentation
- **Security:** Follow security best practices and guidelines
- **Performance:** Meet established performance benchmarks

### **Review Process**
1. **Self-Review:** Agent reviews own work against standards
2. **Peer Review:** Cross-agent review for integration points
3. **Manager Review:** Quality and architecture review
4. **Automated Testing:** All tests must pass before acceptance
5. **Integration Testing:** Verify component interactions

### **Quality Metrics**
- **Code Coverage:** Automated test coverage reporting
- **Performance Benchmarks:** Standardized performance tests
- **Security Scanning:** Automated security vulnerability scans
- **Documentation Coverage:** Completeness of documentation
- **Integration Success:** Successful integration with other components

---

## 📅 Project Coordination Calendar

### **Daily Standups (Async)**
- **Time:** 09:00 UTC daily
- **Format:** Agent status updates in coordination document
- **Duration:** 30 minutes for all agents to update
- **Focus:** Progress, blockers, dependencies, decisions needed

### **Weekly Sync Meetings**
- **Time:** Mondays 14:00 UTC
- **Participants:** All agents
- **Duration:** 60 minutes
- **Agenda:** Progress review, upcoming milestones, risk assessment

### **Milestone Reviews**
- **Frequency:** Every 3-4 days
- **Focus:** Deliverable review, quality assessment, next phase planning
- **Participants:** Relevant agents based on milestone
- **Output:** Go/no-go decision for next phase

---

## 🔄 Continuous Improvement

### **Retrospective Process**
- **Weekly Retrospectives:** What worked well, what didn't, improvements
- **Milestone Retrospectives:** Deeper analysis of process effectiveness
- **Agent Feedback:** Regular feedback on management and coordination
- **Process Optimization:** Continuous refinement of workflows

### **Learning Integration**
- **Best Practices Sharing:** Capture and share effective approaches
- **Lessons Learned:** Document and apply lessons from challenges
- **Skill Development:** Identify and address agent skill gaps
- **Tool Optimization:** Improve tools and processes based on experience

---

## 📞 Communication Protocols

### **Manager Agent Availability**
- **Response Time:** Within 2 hours during business hours
- **Escalation Response:** Within 30 minutes for critical issues
- **Decision Turnaround:** Within 4 hours for most decisions
- **Review Turnaround:** Within 24 hours for deliverable reviews

### **Agent-to-Manager Communication**
- **Status Updates:** Required twice daily minimum
- **Decision Requests:** Use structured decision request format
- **Escalations:** Follow escalation matrix and protocols
- **Feedback:** Provide regular feedback on management effectiveness

### **Inter-Agent Communication**
- **Coordination Document:** Primary communication channel
- **Direct Communication:** Encouraged for technical collaboration
- **Conflict Resolution:** Escalate to Manager Agent if needed
- **Knowledge Sharing:** Share learnings and best practices

---

## 🎯 Success Metrics

### **Project Success Metrics**
- **Timeline Adherence:** Complete within planned 28-day timeline
- **Quality Standards:** All deliverables meet defined quality criteria
- **Integration Success:** Zero critical integration failures
- **Team Coordination:** Effective collaboration across all agents

### **Management Success Metrics**
- **Agent Satisfaction:** High satisfaction with management and coordination
- **Decision Effectiveness:** Decisions lead to positive outcomes
- **Risk Mitigation:** Successful identification and resolution of risks
- **Process Efficiency:** Continuous improvement in workflows and communication

---

## 📚 Reference Documents

### **Core Project Documents**
- `FILE_ORGANIZER_ROADMAP.md` - Overall project roadmap
- `PARALLEL_EXECUTION_PLAN.md` - Parallel execution strategy
- `AGENT_COORDINATION.md` - Agent communication hub
- `DEPENDENCY_ANALYSIS.json` - Detailed dependency data
- `FEATURE_SUGGESTIONS.md` - Feature suggestion system
- `FEATURE_EVALUATION_PROCESS.md` - Feature evaluation process and criteria
- `AGENT_FEATURE_SUGGESTION_GUIDELINES.md` - Agent feature suggestion guidelines
- `ADDITIONAL_FEATURE_SUGGESTIONS.md` - Extended feature roadmap and analysis
- `ADDITIONAL_FEATURE_SUGGESTIONS.json` - Structured additional feature data

### **Agent Management Documents**
- `AGENT_[NAME]_PROMPT.md` - Individual agent prompts (6 files)
- `TASK_ASSIGNMENT_TEMPLATES.md` - Task assignment templates
- `REVIEW_PROTOCOLS.md` - Review and feedback protocols
- `QUALITY_STANDARDS.md` - Quality assurance guidelines
- `AGENT_FEATURE_SUGGESTION_GUIDELINES.md` - Guidelines for agent feature suggestions

### **Project Artifacts**
- Implementation Plan (this framework)
- Memory Bank (coordination document)
- Task Assignment Prompts (individual agent files)
- Review and Feedback Logs (coordination document)

---

*This framework serves as the foundation for managing the 6-agent parallel development project. All agents should reference their individual prompt files and the coordination document for current instructions and status.*