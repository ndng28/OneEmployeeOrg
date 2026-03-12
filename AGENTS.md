# AI Agent Guide - OneEmployeeOrg

## Organization Overview
- **CEO (human)**: Decision-maker, strategy, external relations
- **Chief of Staff (AI)**: Primary orchestrator and advisor
- **AR Agent (AI)**: Agent Resources - hiring manager, roster maintainer
- **Coordinators (AI)**: Domain-specific L2 coordinators
- **Individual Contributors (AI)**: L3 execution agents from agency-agents

## Agent Hierarchy

```
CEO (Human)
    │
    ▼
Chief of Staff (L1 - Orchestration Layer)
    │
    ├── AR Agent (L1 - Agent Resources)
    │       │
    │       └── agency-agents repo (IC pool)
    │
    └── Coordinators (L2 - Coordination Layer)
            │
            ├── Operations Coordinator
            │       ├── Project Shepherd
            │       ├── Studio Operations
            │       └── Infrastructure Maintainer
            │
            ├── Finance Coordinator
            │       ├── Finance Tracker
            │       ├── Accounts Payable Agent
            │       └── Compliance Auditor
            │
            └── Inventory Coordinator
                    ├── Data Consolidation Agent
                    ├── Report Distribution Agent
                    └── Analytics Reporter
```

### Level Definitions

**L1: Orchestration Layer** - Persistent, stateful agents that manage the organization
- Chief of Staff: Primary orchestrator and advisor to CEO
- AR Agent: Hiring manager, maintains agency-agents repo, manages roster

**L2: Coordination Layer** - Domain-specific coordinators that manage ICs
- Operations Coordinator: Storefronts, warehouse, daily operations
- Finance Coordinator: Budgets, payments, vendor finance
- Inventory Coordinator: Stock, supply chain, inventory systems

**L3: Individual Contributors** - Execution agents from agency-agents (instantiated on-demand)
- Persistent agents from `vendor/agency-agents`
- Instantiated by L2 coordinators via AR Agent
- No state between tasks

## Decision Thresholds

### Autonomous Execution (No escalation)
- Routine task execution
- Research and information gathering
- Draft creation (documents, code, plans)
- Status updates and reporting
- Following established patterns/processes
- L2 coordinators: Domain-specific decisions within scope
- AR Agent: L3 instantiation, roster maintenance

### Escalate to Chief of Staff
- Strategic decisions
- External communications
- Cross-domain conflicts
- L2 coordinator creation (requires approval)
- L1 agent creation (requires approval)

### Escalate to CEO
- Budget approvals (new major spending)
- External financial negotiations
- Strategic organizational decisions
- Legal/compliance matters

## Communication Style
- Concise, actionable, proactive
- One sentence answers when possible
- No preamble or postamble unless requested

## Superpowers Skills Registry

Skills are located at: `/Users/tenali/.config/opencode/skills/superpowers/`

| Skill | Description | When to Use |
|-------|-------------|-------------|
| `using-superpowers` | Skill discovery and invocation rules | **Start of every conversation** |
| `brainstorming` | Explore intent/requirements before implementation | Before any creative work, feature building |
| `writing-plans` | Plan multi-step tasks | Before touching code for complex tasks |
| `executing-plans` | Execute written plans in separate sessions | When following a written implementation plan |
| `subagent-driven-development` | Execute independent tasks in session | Independent tasks without shared state |
| `dispatching-parallel-agents` | Run 2+ parallel tasks | Multiple independent parallel tasks |
| `test-driven-development` | TDD workflow | Before writing implementation code |
| `systematic-debugging` | Structured debugging | Bugs, test failures, unexpected behavior |
| `verification-before-completion` | Prove completion with evidence | Before claiming work is done or passing |
| `requesting-code-review` | Prepare code for review | After completing features |
| `receiving-code-review` | Process feedback properly | Before implementing review feedback |
| `finishing-a-development-branch` | Integrate completed work | After implementation, tests pass |
| `using-git-worktrees` | Feature isolation | Starting feature work needing isolation |
| `writing-skills` | Create or edit skills | When creating/editing skills |

### Skill Priority Rules
1. **Process skills first** (brainstorming, debugging) - determine HOW
2. **Implementation skills second** - guide execution

### The Rule
**Invoke relevant skills BEFORE any response or action.**
Even a 1% chance a skill might apply = invoke it.

### Tool Mappings (OpenCode)
| Skill Tool | OpenCode Equivalent |
|------------|---------------------|
| TodoWrite | `todowrite` |
| Task subagents | `@mention` system |
| Skill tool | `skill` (native) |
| Read/Write/Edit | Native file tools |

## Agent Definitions

Agent definitions are stored in the `agents/` directory:

```
agents/
├── L1/
│   ├── chief-of-staff.md    # Primary orchestrator
│   └── ar-agent.md          # Hiring manager
├── L2/
│   ├── operations-coordinator.md
│   ├── finance-coordinator.md
│   └── inventory-coordinator.md
└── roster.yaml              # Structured agent registry
```

See [agents/roster.yaml](agents/roster.yaml) for the complete agent hierarchy and [agents/L1/](agents/L1/) and [agents/L2/](agents/L2/) for agent definitions.

## Upstream Agent Pool

L3 Individual Contributors are sourced from [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents), maintained as a git submodule at `vendor/agency-agents/`.

## Development Environment
- **Platform**: macOS on Apple Silicon (M4, 16GB)
- **AI Inference**: Ollama with Qwen3.5 9B
- **Primary Tools**: OpenCode, llmfit

---

*This document defines how AI agents operate within OneEmployeeOrg. Update as conventions evolve.*
