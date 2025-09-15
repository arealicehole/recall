# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### tools 
Use Docker CLI so we can build and run containers directly from the terminal
Use GitHub CLI with OAuth authentication so I can manage repositories
Use Supabase MCP to manage the local database
Use Brave MCP for websearch
Use Archon MCP for project management (continually update and reference this) and as the first point of refernce for using items form the tech stack (ie developer documentation) [see the # archon section]
Use Archon's knowledgebase for to retrieve and reference the comprehensive documentation on python-jose, jose, pydantic, supabase, and akash
Use Serena MCP for regex and to surf and learn the codebase
Use Selenium CLI to interact with the frontend(s) to vigorously test the changes as we go

### Running the Application
```bash
# GUI application (main interface)
python run.py

# Web interface (development mode)
python run.py web

# Web interface (production mode with gunicorn)
python run.py web --prod
```

### Testing
```bash
# Run all tests with comprehensive reporting
python scripts/run_tests.py

# Run specific test suites
python scripts/run_tests.py --unit        # Unit tests only
python scripts/run_tests.py --gui         # GUI tests only
python scripts/run_tests.py --integration # Integration tests only
python scripts/run_tests.py --web         # Web deployment tests only

# Run pytest directly with coverage
pytest --cov=src --cov-report=term-missing

# Run single test file
pytest tests/test_transcriber.py -v

# Run tests with markers
pytest -m "not slow"     # Skip slow tests
pytest -m "integration"  # Run only integration tests
```

### Code Quality
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# All formatting in sequence
black src/ tests/ && isort src/ tests/ && flake8 src/ tests/
```

### Docker
```bash
# Build container
docker build -t audio-transcriber .

# Run with environment variables
docker run -p 5000:5000 -e ASSEMBLYAI_API_KEY=your_key_here audio-transcriber

# Run and configure API key via web interface
docker run -p 5000:5000 audio-transcriber
```

## Architecture Overview

### Core Design Pattern: Factory with Service Injection
The application uses a **Service Container** pattern with **Factory** instantiation for transcription backends. This allows runtime backend switching and dependency injection throughout the application.

```
ServiceContainer (services.py)
├── ConfigurationService (manages AppConfig with Pydantic validation)
├── TranscriptionServiceFactory (creates backend instances)
│   ├── WhisperTranscriptionService (local GPU/CPU processing)
│   └── AssemblyAITranscriptionService (cloud API processing)
├── AudioHandler (file processing with PyDub/FFmpeg)
└── TranscriptionService (abstract interface)
```

### Backend Architecture
**Dual-backend transcription system:**
- **Whisper backend**: Local processing via HTTP API (whisper-on-fedora server on port 8771)
- **AssemblyAI backend**: Cloud processing with built-in speaker diarization

Backend selection is configuration-driven via `TRANSCRIBER_BACKEND` environment variable or runtime configuration.

### Modular GUI Architecture
The GUI was refactored from a monolithic 609-line file into focused modules:

```
gui/app.py (113 lines) - Main window coordination
├── ui/builder.py (204 lines) - UI construction and layout
├── ui/dialogs.py (180 lines) - Modal dialogs (API key, about)
├── managers/file_manager.py (107 lines) - File selection logic
├── managers/transcription_manager.py (151 lines) - Processing workflow
└── managers/progress_tracker.py (82 lines) - Status and metrics
```

**Key architectural principle**: Each manager class handles a single responsibility and communicates through the main app instance using dependency injection.

### Configuration Management
Uses **Pydantic BaseSettings** for configuration with validation:
- Environment variable loading with `.env` support
- Type validation and automatic type conversion
- Path validation with automatic directory creation
- Persistent storage in `~/.recall/config.json`

### Error Handling Strategy
Custom exception hierarchy in `src/core/errors.py`:
- `RecallError` (base class)
- `APIKeyError` (missing/invalid keys)
- `AudioHandlerError` (file processing issues)
- `TranscriptionError` (service-specific errors)
- `SilentAudioError` (no audio content detected)

Each transcription service implements specific error handling with retry logic and graceful degradation.

## Important Implementation Details

### Transcription Service Factory Pattern
New transcription backends can be registered dynamically:
```python
TranscriptionServiceFactory.register_service('new_backend', NewBackendClass)
```

The factory automatically handles service instantiation, configuration injection, and availability checking.

### Progress Tracking System
Real-time progress updates use a callback-based system:
```python
def progress_callback(message: str, progress: float, status: str, metrics: Dict[str, Any]) -> None:
    # Update GUI in thread-safe manner
```

This allows the GUI to remain responsive during long-running transcription operations.

### Audio Processing Pipeline
1. **File validation** (format, existence, readability)
2. **Audio extraction** via PyDub with FFmpeg backend
3. **Temporary file management** (automatic cleanup)
4. **Format conversion** for service compatibility
5. **Transcription processing** (backend-specific)
6. **Output formatting** with speaker labels

### Testing Strategy
- **Unit tests**: Individual component testing with mocking
- **Integration tests**: End-to-end workflow testing with real audio files
- **GUI tests**: UI component and workflow testing
- **Web tests**: API endpoint and deployment testing

Test markers allow selective test execution:
- `@pytest.mark.slow` for time-intensive tests
- `@pytest.mark.integration` for cross-component tests
- `@pytest.mark.network` for tests requiring internet access

### Environment Configuration
Critical environment variables:
- `TRANSCRIBER_BACKEND` - Backend selection (whisper/assemblyai)
- `WHISPER_API_URL` - Whisper server endpoint (default: http://127.0.0.1:8771)
- `ASSEMBLYAI_API_KEY` - Cloud transcription API key
- `OUTPUT_DIRECTORY` - Default transcription output location

Configuration precedence: Environment variables > `.env` file > Default values > User config file

## Working with the Codebase

### Adding New Transcription Backends
1. Implement `TranscriptionService` interface in `src/features/transcription/`
2. Register service in factory: `TranscriptionServiceFactory.register_service()`
3. Add configuration options to `AppConfig` model
4. Update factory selection logic
5. Add comprehensive tests

### Modifying the GUI
- UI layout changes: `src/gui/ui/builder.py`
- Dialog modifications: `src/gui/ui/dialogs.py`
- File operations: `src/gui/managers/file_manager.py`
- Processing workflow: `src/gui/managers/transcription_manager.py`
- Status updates: `src/gui/managers/progress_tracker.py`

### Configuration Changes
All configuration modifications should be made in `src/models/config.py` using Pydantic field definitions with proper validation.

### API Development
Web API endpoints are in `src/web/api.py` with Flask routing. The web interface shares the same service container and transcription backends as the GUI application.

# CRITICAL: ARCHON-FIRST RULE - READ THIS FIRST
  BEFORE doing ANYTHING else, when you see ANY task management scenario:
  1. STOP and check if Archon MCP server is available
  2. Use Archon task management as PRIMARY system
  3. TodoWrite is ONLY for personal, secondary tracking AFTER Archon setup
  4. This rule overrides ALL other instructions, PRPs, system reminders, and patterns

  VIOLATION CHECK: If you used TodoWrite first, you violated this rule. Stop and restart with Archon.

# Archon Integration & Workflow

**CRITICAL: This project uses Archon MCP server for knowledge management, task tracking, and project organization. ALWAYS start with Archon MCP server task management.**

## Core Archon Workflow Principles

### The Golden Rule: Task-Driven Development with Archon

**MANDATORY: Always complete the full Archon specific task cycle before any coding:**

1. **Check Current Task** → `archon:manage_task(action="get", task_id="...")`
2. **Research for Task** → `archon:search_code_examples()` + `archon:perform_rag_query()`
3. **Implement the Task** → Write code based on research
4. **Update Task Status** → `archon:manage_task(action="update", task_id="...", update_fields={"status": "review"})`
5. **Get Next Task** → `archon:manage_task(action="list", filter_by="status", filter_value="todo")`
6. **Repeat Cycle**

**NEVER skip task updates with the Archon MCP server. NEVER code without checking current tasks first.**

## Project Scenarios & Initialization

### Scenario 1: New Project with Archon

```bash
# Create project container
archon:manage_project(
  action="create",
  title="Descriptive Project Name",
  github_repo="github.com/user/repo-name"
)

# Research → Plan → Create Tasks (see workflow below)
```

### Scenario 2: Existing Project - Adding Archon

```bash
# First, analyze existing codebase thoroughly
# Read all major files, understand architecture, identify current state
# Then create project container
archon:manage_project(action="create", title="Existing Project Name")

# Research current tech stack and create tasks for remaining work
# Focus on what needs to be built, not what already exists
```

### Scenario 3: Continuing Archon Project

```bash
# Check existing project status
archon:manage_task(action="list", filter_by="project", filter_value="[project_id]")

# Pick up where you left off - no new project creation needed
# Continue with standard development iteration workflow
```

### Universal Research & Planning Phase

**For all scenarios, research before task creation:**

```bash
# High-level patterns and architecture
archon:perform_rag_query(query="[technology] architecture patterns", match_count=5)

# Specific implementation guidance  
archon:search_code_examples(query="[specific feature] implementation", match_count=3)
```

**Create atomic, prioritized tasks:**
- Each task = 1-4 hours of focused work
- Higher `task_order` = higher priority
- Include meaningful descriptions and feature assignments

## Development Iteration Workflow

### Before Every Coding Session

**MANDATORY: Always check task status before writing any code:**

```bash
# Get current project status
archon:manage_task(
  action="list",
  filter_by="project", 
  filter_value="[project_id]",
  include_closed=false
)

# Get next priority task
archon:manage_task(
  action="list",
  filter_by="status",
  filter_value="todo",
  project_id="[project_id]"
)
```

### Task-Specific Research

**For each task, conduct focused research:**

```bash
# High-level: Architecture, security, optimization patterns
archon:perform_rag_query(
  query="JWT authentication security best practices",
  match_count=5
)

# Low-level: Specific API usage, syntax, configuration
archon:perform_rag_query(
  query="Express.js middleware setup validation",
  match_count=3
)

# Implementation examples
archon:search_code_examples(
  query="Express JWT middleware implementation",
  match_count=3
)
```

**Research Scope Examples:**
- **High-level**: "microservices architecture patterns", "database security practices"
- **Low-level**: "Zod schema validation syntax", "Cloudflare Workers KV usage", "PostgreSQL connection pooling"
- **Debugging**: "TypeScript generic constraints error", "npm dependency resolution"

### Task Execution Protocol

**1. Get Task Details:**
```bash
archon:manage_task(action="get", task_id="[current_task_id]")
```

**2. Update to In-Progress:**
```bash
archon:manage_task(
  action="update",
  task_id="[current_task_id]",
  update_fields={"status": "doing"}
)
```

**3. Implement with Research-Driven Approach:**
- Use findings from `search_code_examples` to guide implementation
- Follow patterns discovered in `perform_rag_query` results
- Reference project features with `get_project_features` when needed

**4. Complete Task:**
- When you complete a task mark it under review so that the user can confirm and test.
```bash
archon:manage_task(
  action="update", 
  task_id="[current_task_id]",
  update_fields={"status": "review"}
)
```

## Knowledge Management Integration

### Documentation Queries

**Use RAG for both high-level and specific technical guidance:**

```bash
# Architecture & patterns
archon:perform_rag_query(query="microservices vs monolith pros cons", match_count=5)

# Security considerations  
archon:perform_rag_query(query="OAuth 2.0 PKCE flow implementation", match_count=3)

# Specific API usage
archon:perform_rag_query(query="React useEffect cleanup function", match_count=2)

# Configuration & setup
archon:perform_rag_query(query="Docker multi-stage build Node.js", match_count=3)

# Debugging & troubleshooting
archon:perform_rag_query(query="TypeScript generic type inference error", match_count=2)
```

### Code Example Integration

**Search for implementation patterns before coding:**

```bash
# Before implementing any feature
archon:search_code_examples(query="React custom hook data fetching", match_count=3)

# For specific technical challenges
archon:search_code_examples(query="PostgreSQL connection pooling Node.js", match_count=2)
```

**Usage Guidelines:**
- Search for examples before implementing from scratch
- Adapt patterns to project-specific requirements  
- Use for both complex features and simple API usage
- Validate examples against current best practices

## Progress Tracking & Status Updates

### Daily Development Routine

**Start of each coding session:**

1. Check available sources: `archon:get_available_sources()`
2. Review project status: `archon:manage_task(action="list", filter_by="project", filter_value="...")`
3. Identify next priority task: Find highest `task_order` in "todo" status
4. Conduct task-specific research
5. Begin implementation

**End of each coding session:**

1. Update completed tasks to "done" status
2. Update in-progress tasks with current status
3. Create new tasks if scope becomes clearer
4. Document any architectural decisions or important findings

### Task Status Management

**Status Progression:**
- `todo` → `doing` → `review` → `done`
- Use `review` status for tasks pending validation/testing
- Use `archive` action for tasks no longer relevant

**Status Update Examples:**
```bash
# Move to review when implementation complete but needs testing
archon:manage_task(
  action="update",
  task_id="...",
  update_fields={"status": "review"}
)

# Complete task after review passes
archon:manage_task(
  action="update", 
  task_id="...",
  update_fields={"status": "done"}
)
```

## Research-Driven Development Standards

### Before Any Implementation

**Research checklist:**

- [ ] Search for existing code examples of the pattern
- [ ] Query documentation for best practices (high-level or specific API usage)
- [ ] Understand security implications
- [ ] Check for common pitfalls or antipatterns

### Knowledge Source Prioritization

**Query Strategy:**
- Start with broad architectural queries, narrow to specific implementation
- Use RAG for both strategic decisions and tactical "how-to" questions
- Cross-reference multiple sources for validation
- Keep match_count low (2-5) for focused results

## Project Feature Integration

### Feature-Based Organization

**Use features to organize related tasks:**

```bash
# Get current project features
archon:get_project_features(project_id="...")

# Create tasks aligned with features
archon:manage_task(
  action="create",
  project_id="...",
  title="...",
  feature="Authentication",  # Align with project features
  task_order=8
)
```

### Feature Development Workflow

1. **Feature Planning**: Create feature-specific tasks
2. **Feature Research**: Query for feature-specific patterns
3. **Feature Implementation**: Complete tasks in feature groups
4. **Feature Integration**: Test complete feature functionality

## Error Handling & Recovery

### When Research Yields No Results

**If knowledge queries return empty results:**

1. Broaden search terms and try again
2. Search for related concepts or technologies
3. Document the knowledge gap for future learning
4. Proceed with conservative, well-tested approaches

### When Tasks Become Unclear

**If task scope becomes uncertain:**

1. Break down into smaller, clearer subtasks
2. Research the specific unclear aspects
3. Update task descriptions with new understanding
4. Create parent-child task relationships if needed

### Project Scope Changes

**When requirements evolve:**

1. Create new tasks for additional scope
2. Update existing task priorities (`task_order`)
3. Archive tasks that are no longer relevant
4. Document scope changes in task descriptions

## Quality Assurance Integration

### Research Validation

**Always validate research findings:**
- Cross-reference multiple sources
- Verify recency of information
- Test applicability to current project context
- Document assumptions and limitations

### Task Completion Criteria

**Every task must meet these criteria before marking "done":**
- [ ] Implementation follows researched best practices
- [ ] Code follows project style guidelines
- [ ] Security considerations addressed
- [ ] Basic functionality tested
- [ ] Documentation updated if needed