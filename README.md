# OneEmployeeOrg

One human CEO, AI-powered operations.

## About

OneEmployeeOrg is a retail organization with:
- **Storefronts**: Multiple locations handling diverse products
- **Warehouse**: Central inventory management and distribution
- **Vendor Network**: Supplier relationships and procurement workflows

The organization operates with AI agents fulfilling operational roles traditionally held by multiple employees.

## AI Agent Architecture

### Hierarchy

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
            ├── Finance Coordinator
            └── Inventory Coordinator
```

### Agent Levels

- **L1: Orchestration Layer** - Chief of Staff (primary orchestrator) and AR Agent (hiring manager)
- **L2: Coordination Layer** - Domain coordinators managing ICs within their domain
- **L3: Individual Contributors** - Execution agents from [agency-agents](https://github.com/msitarzewski/agency-agents)

See [AGENTS.md](./AGENTS.md) for complete agent definitions and decision frameworks.

## Development

### Prerequisites
- OpenCode CLI
- Git (with submodule support)

### Getting Started
```bash
git clone --recurse-submodules https://github.com/ndng28/OneEmployeeOrg.git
cd OneEmployeeOrg
```

### Project Structure
```
OneEmployeeOrg/
├── AGENTS.md                # AI agent configuration and protocols
├── README.md               # This file
├── .gitignore              # Git ignore patterns
├── agents/
│   ├── L1/                 # L1 agent definitions (Chief of Staff, AR)
│   ├── L2/                 # L2 coordinator definitions
│   ├── L3/                 # L3 IC references (ephemeral)
│   └── roster.yaml         # Structured agent registry
└── vendor/
    └── agency-agents/      # Git submodule (IC pool)
```

## Superpowers Skills

This project uses a structured skill system for AI agent workflows:
- Brainstorming before creative work
- TDD for feature development  
- Systematic debugging for issues
- Verification before claiming completion

Full skill registry in [AGENTS.md](./AGENTS.md#superpowers-skills-registry).

Powered by [obra/superpowers](https://github.com/obra/superpowers).

## Roadmap

### Phase 1 (Current)
- OpenCode CLI support
- Core agentic scaffolding with L1/L2/L3 hierarchy
- Operations, Finance, and Inventory coordinators

### Phase 2 (Planned)
- Additional CLI support (Ollama, Claude, etc.)
- Extended coordinator roles (Sales, Support, Marketing)
- Vendor integration workflows

## License

MIT
