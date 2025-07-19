#!/usr/bin/env python3
"""
Clean the coordination system to make it project-agnostic.
Removes all project-specific content and resets agents to initial state.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent

def clean_agent_status_file(agent_name, agent_info):
    """Reset an individual agent status file to initial state."""
    initial_status = {
        "agent_info": agent_info,
        "current_status": {
            "task": "Awaiting task assignment",
            "status": "🔵",
            "status_text": "Ready",
            "progress": 0,
            "progress_description": "Not started",
            "eta": "TBD",
            "last_update": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        },
        "activities": {
            "completed": [],
            "in_progress": [],
            "pending": []
        },
        "blockers": {
            "current": [],
            "resolved": []
        },
        "decisions": [],
        "next_steps": [
            "Await task assignment",
            "Review project requirements when available"
        ],
        "communication": {
            "notes": [
                "Agent initialized and ready for task assignment"
            ],
            "requests": [],
            "offers": []
        },
        "dependencies": {
            "blocking": [],
            "blocked_by": [],
            "completed_dependencies": []
        },
        "metrics": {
            "tasks_completed": 0,
            "tasks_total": 0,
            "completion_percentage": 0,
            "days_ahead_of_schedule": 0
        },
        "deliverables": []
    }
    
    return initial_status

def create_project_agnostic_coordination_md():
    """Create a project-agnostic AGENT_COORDINATION.md template."""
    template = """# Agent Coordination Hub

**Project:** [Project Name]  
**Start Date:** [Start Date]  
**Last Updated:** {timestamp}  
**Status:** Ready for Initialization

---

## 🚦 Global Status Dashboard

### **Overall Project Health**
- **Status:** 🔵 AWAITING PROJECT INITIALIZATION
- **Active Agents:** 6
- **Completed Tasks:** 0/0
- **Critical Path Status:** ⏳ Not Started
- **Next Milestone:** Project Kickoff

### **Daily Summary**
- **Tasks Started Today:** 0
- **Tasks Completed Today:** 0
- **Blockers:** None
- **Decisions Pending:** Project initialization

---

## 👥 Agent Status Updates

### 🔴 **Agent Alpha (Critical Path Lead)**
**Current Task:** Awaiting assignment  
**Status:** 🔵 Ready  
**Progress:** 0%  
**ETA:** TBD  
**Last Update:** {timestamp}

#### **Current Activities:**
- [ ] Awaiting project initialization
- [ ] Ready to receive task assignments

#### **Blockers & Issues:**
- None

#### **Next Steps:**
- Await project kickoff
- Review assigned tasks when available

---

### 🔵 **Agent Beta (Migration Specialist)**
**Current Task:** Awaiting assignment  
**Status:** 🔵 Ready  
**Progress:** 0%  
**ETA:** TBD  
**Last Update:** {timestamp}

#### **Current Activities:**
- [ ] Awaiting project initialization
- [ ] Ready to receive task assignments

#### **Blockers & Issues:**
- None

#### **Next Steps:**
- Await project kickoff
- Review assigned tasks when available

---

### 🟢 **Agent Gamma (Dashboard Developer)**
**Current Task:** Awaiting assignment  
**Status:** 🔵 Ready  
**Progress:** 0%  
**ETA:** TBD  
**Last Update:** {timestamp}

#### **Current Activities:**
- [ ] Awaiting project initialization
- [ ] Ready to receive task assignments

#### **Blockers & Issues:**
- None

#### **Next Steps:**
- Await project kickoff
- Review assigned tasks when available

---

### 🟡 **Agent Delta (DevOps Engineer)**
**Current Task:** Awaiting assignment  
**Status:** 🔵 Ready  
**Progress:** 0%  
**ETA:** TBD  
**Last Update:** {timestamp}

#### **Current Activities:**
- [ ] Awaiting project initialization
- [ ] Ready to receive task assignments

#### **Blockers & Issues:**
- None

#### **Next Steps:**
- Await project kickoff
- Review assigned tasks when available

---

### 🟠 **Agent Epsilon (Security Engineer)**
**Current Task:** Awaiting assignment  
**Status:** 🔵 Ready  
**Progress:** 0%  
**ETA:** TBD  
**Last Update:** {timestamp}

#### **Current Activities:**
- [ ] Awaiting project initialization
- [ ] Ready to receive task assignments

#### **Blockers & Issues:**
- None

#### **Next Steps:**
- Await project kickoff
- Review assigned tasks when available

---

### 🟣 **Agent Zeta (UX Engineer)**
**Current Task:** Awaiting assignment  
**Status:** 🔵 Ready  
**Progress:** 0%  
**ETA:** TBD  
**Last Update:** {timestamp}

#### **Current Activities:**
- [ ] Awaiting project initialization
- [ ] Ready to receive task assignments

#### **Blockers & Issues:**
- None

#### **Next Steps:**
- Await project kickoff
- Review assigned tasks when available

---

## 🔄 Cross-Agent Communication

### **Pending Discussions**
- Project initialization meeting

### **Completed Discussions**
- None yet

### **Integration Points**
- To be determined based on project requirements

### **Shared Resources**
- To be identified during project planning

---

## 📋 Decision Log

### **Decisions Needed**
| ID | Decision | Owner | Deadline | Status |
|----|----------|-------|----------|--------|
| D001 | Project scope and objectives | All | TBD | Pending |
| D002 | Technology stack selection | All | TBD | Pending |
| D003 | Timeline and milestones | All | TBD | Pending |

### **Decisions Made**
| ID | Decision | Owner | Date | Impact |
|----|----------|-------|------|--------|
| - | - | - | - | - |

---

## 🚨 Roadblock Escalation

### **Current Blockers**
| ID | Blocker | Affected Agent | Severity | Owner | ETA | Status |
|----|---------|----------------|----------|-------|-----|--------|
| - | None | - | - | - | - | - |

### **Escalation Process**
1. **Low Severity:** Update in agent section, continue work
2. **Medium Severity:** Add to roadblock table, notify relevant agents
3. **High Severity:** Add to roadblock table, schedule coordination meeting
4. **Critical Severity:** Stop work, escalate to project manager immediately

---

## 🎯 Dependency Tracker

### **Active Dependencies**
| Waiting Task | Depends On | Owner | Status | ETA |
|--------------|------------|-------|--------|-----|
| - | - | - | - | - |

### **Dependency Status**
- 🟢 **On Track:** N/A
- 🟡 **At Risk:** N/A
- 🔴 **Blocked:** N/A

---

## 📊 Daily Standups

### **Daily Standup Template**
Each agent should update their section daily with:
1. **What I completed yesterday**
2. **What I'm working on today**
3. **What blockers I'm facing**
4. **What help I need from other agents**

### **{date} Standup**
**Agent Alpha:** Awaiting project initialization  
**Agent Beta:** Awaiting project initialization  
**Agent Gamma:** Awaiting project initialization  
**Agent Delta:** Awaiting project initialization  
**Agent Epsilon:** Awaiting project initialization  
**Agent Zeta:** Awaiting project initialization  

---

## 📞 Communication Protocols

### **Update Frequency**
- **Agent Status:** Update your section at least twice daily
- **Roadblocks:** Update immediately when encountered
- **Decisions:** Log within 1 hour of making
- **Dependencies:** Update when status changes

### **Communication Channels**
- **This Document:** Primary coordination and status
- **Integration Points:** Scheduled sync meetings
- **Urgent Issues:** Immediate escalation protocols
- **Decision Making:** Collaborative discussion in relevant sections

### **Conflict Resolution**
1. **Minor Conflicts:** Discuss in communication notes
2. **Major Conflicts:** Add to roadblock escalation
3. **Critical Conflicts:** Immediate project manager involvement

---

## 📅 Milestone Schedule

### **Upcoming Milestones**
- **Project Kickoff:** TBD
- **Initial Planning:** TBD
- **First Sprint:** TBD

### **Success Criteria**
- To be defined based on project objectives

---

## 🔧 Quick Reference

### **Update Instructions**
1. **Find your agent section** (search for your color emoji)
2. **Update your status** using the provided template
3. **Add timestamp** to your last update
4. **Log any decisions** in the decision log
5. **Report blockers** in the roadblock section
6. **Communicate needs** in your communication notes

### **Emergency Contacts**
- **Project Manager:** [Contact info]
- **Technical Lead:** [Contact info]
- **DevOps Support:** [Contact info]

### **Document Rules**
- ✅ **DO:** Update your own agent section frequently
- ✅ **DO:** Log decisions and blockers immediately
- ✅ **DO:** Communicate needs clearly
- ❌ **DON'T:** Modify other agents' sections
- ❌ **DON'T:** Delete historical information
- ❌ **DON'T:** Make global changes without discussion

---

*This coordination document is the single source of truth for agent communication and project status. Keep it updated and refer to it daily.*
""".format(
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    return template

def clean_coordination_system():
    """Main function to clean the coordination system."""
    project_root = get_project_root()
    
    print("🧹 Cleaning Agent Coordination System...")
    print(f"Project root: {project_root}")
    
    # Agent information
    agents = {
        "alpha": {
            "name": "Alpha",
            "role": "Critical Path Lead",
            "color": "🔴",
            "id": "alpha"
        },
        "beta": {
            "name": "Beta", 
            "role": "Migration Specialist",
            "color": "🔵",
            "id": "beta"
        },
        "gamma": {
            "name": "Gamma",
            "role": "Dashboard Developer", 
            "color": "🟢",
            "id": "gamma"
        },
        "delta": {
            "name": "Delta",
            "role": "DevOps Engineer",
            "color": "🟡", 
            "id": "delta"
        },
        "epsilon": {
            "name": "Epsilon",
            "role": "Security Engineer",
            "color": "🟠",
            "id": "epsilon"
        },
        "zeta": {
            "name": "Zeta",
            "role": "UX Engineer",
            "color": "🟣",
            "id": "zeta"
        }
    }
    
    # Clean agent status files
    agent_status_dir = project_root / "agent_status"
    if agent_status_dir.exists():
        print("\n📁 Cleaning agent status files...")
        for agent_id, agent_info in agents.items():
            status_file = agent_status_dir / f"{agent_id}_status.json"
            if status_file.exists():
                initial_status = clean_agent_status_file(agent_id, agent_info)
                with open(status_file, 'w') as f:
                    json.dump(initial_status, f, indent=2)
                print(f"  ✅ Reset {agent_id}_status.json")
    
    # Create project-agnostic AGENT_COORDINATION.md
    print("\n📄 Creating project-agnostic AGENT_COORDINATION.md...")
    coord_md_path = project_root / "AGENT_COORDINATION.md"
    with open(coord_md_path, 'w') as f:
        f.write(create_project_agnostic_coordination_md())
    print("  ✅ Created AGENT_COORDINATION.md")
    
    # Create project-agnostic AGENT_COORDINATION_MASTER.json
    print("\n📄 Creating project-agnostic AGENT_COORDINATION_MASTER.json...")
    master_json = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_agents": 6,
            "active_agents": 0,
            "aggregator_version": "2.0"
        },
        "agents": {},
        "summary": {
            "completed_agents": [],
            "in_progress_agents": [],
            "blocked_agents": [],
            "starting_agents": []
        }
    }
    
    # Add each agent to master JSON
    for agent_id, agent_info in agents.items():
        master_json["agents"][agent_id] = clean_agent_status_file(agent_id, agent_info)
        master_json["summary"]["starting_agents"].append(agent_id)
    
    master_json_path = project_root / "AGENT_COORDINATION_MASTER.json"
    with open(master_json_path, 'w') as f:
        json.dump(master_json, f, indent=2)
    print("  ✅ Created AGENT_COORDINATION_MASTER.json")
    
    # Clean log files
    print("\n📄 Cleaning log files...")
    coordination_system_dir = project_root / "coordination_system"
    if coordination_system_dir.exists():
        log_files = [
            "agent_updates.log",
            "coordination_manager.log",
            "coordination_system.log"
        ]
        
        for log_file in log_files:
            log_path = coordination_system_dir / log_file
            if log_path.exists():
                # Create empty log file
                with open(log_path, 'w') as f:
                    f.write("")
                print(f"  ✅ Cleared {log_file}")
    
    # Clean agent communication directories
    print("\n📁 Cleaning agent communication directories...")
    agent_comm_dir = project_root / "agent_communication"
    if agent_comm_dir.exists():
        for agent_id in agents.keys():
            agent_dir = agent_comm_dir / agent_id
            if agent_dir.exists():
                # Clear inbox and outbox
                inbox_file = agent_dir / "input" / "inbox.json"
                outbox_file = agent_dir / "output" / "outbox.json"
                
                if inbox_file.exists():
                    with open(inbox_file, 'w') as f:
                        json.dump({"messages": []}, f, indent=2)
                    print(f"  ✅ Cleared {agent_id}/input/inbox.json")
                
                if outbox_file.exists():
                    with open(outbox_file, 'w') as f:
                        json.dump({"messages": []}, f, indent=2)
                    print(f"  ✅ Cleared {agent_id}/output/outbox.json")
                
                # Reset lifecycle status
                lifecycle_file = agent_dir / "status" / "lifecycle.json"
                if lifecycle_file.exists():
                    with open(lifecycle_file, 'w') as f:
                        json.dump({
                            "status": "stopped",
                            "last_update": datetime.now(timezone.utc).isoformat()
                        }, f, indent=2)
                    print(f"  ✅ Reset {agent_id}/status/lifecycle.json")
    
    print("\n✅ Coordination system successfully cleaned!")
    print("\n📝 Next steps:")
    print("1. Update AGENT_COORDINATION.md with your new project details")
    print("2. Assign tasks to agents using the update scripts")
    print("3. Start the coordination manager to monitor progress")
    print("4. Launch agents as needed for your project")

if __name__ == "__main__":
    clean_coordination_system()