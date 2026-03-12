# OneEmployeeOrg

One human CEO, AI-powered operations.

## About

OneEmployeeOrg is a retail organization with:
- **Storefronts**: Multiple locations handling diverse products
- **Warehouse**: Central inventory management and distribution
- **Vendor Network**: Supplier relationships and procurement workflows

The organization operates with AI agents fulfilling operational roles traditionally held by multiple employees.

## AI Agent Architecture

The organization uses an agentic scaffolding system where AI agents operate as:
- **Chief of Staff** (this agent): Advisor, executor, coordination
- Additional agent roles to be defined based on operational needs

See [AGENTS.md](./AGENTS.md) for the complete agent guide and decision frameworks.

## Development

### Prerequisites
- OpenCode CLI

### Getting Started
```bash
git clone https://github.com/ndng28/OneEmployeeOrg.git
cd OneEmployeeOrg
```

### Project Structure
```
OneEmployeeOrg/
├── AGENTS.md          # AI agent configuration and protocols
├── README.md          # This file
└── .gitignore         # Git ignore patterns
```

## Superpowers Skills

This project uses a structured skill system for AI agent workflows:
- Brainstorming before creative work
- TDD for feature development  
- Systematic debugging for issues
- Verification before claiming completion

Full skill registry in [AGENTS.md](./AGENTS.md#superpowers-skills-registry).

## Roadmap

### Phase 1 (Current)
- OpenCode CLI support
- Core agentic scaffolding
- Basic agent roles

### Phase 2 (Planned)
- Additional CLI support (Ollama, Claude, etc.)
- Extended agent role definitions
- Vendor integration workflows

## License

MIT
