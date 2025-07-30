# Pytest Implementation Plan for ARK2.0 Backend

## Current State Analysis

### Backend Structure
The ARK2.0 project has multiple Python modules:
- **backend/**: FastAPI application (`main.py`) with calendar API endpoints
- **model_module/**: LLM integration with LangChain (`main.py`)
- **base_module/**: MCP (Model Context Protocol) clients and weather server
- **calendar_module/**: Calendar functionality
- **radicale-test/**: CalDAV server integration with existing unittest-based tests

### Existing Test Infrastructure
- Currently uses **unittest** framework (not pytest)
- Tests are primarily in `radicale-test/` directory
- Main test files: `test_radicale_calendar_manager.py`, `test_radicale_calendar_manager_edge_cases.py`
- Tests focus on Radicale CalDAV server integration
- No tests for FastAPI backend or model modules

## Implementation Plan

### Phase 1: Setup and Configuration

#### 1.1 Install pytest and dependencies
```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx
```

#### 1.2 Create pytest configuration
- Create `pytest.ini` in project root
- Configure test discovery, async support, and coverage reporting
- Set up test markers for different test types

#### 1.3 Update requirements.txt
Add pytest dependencies to requirements.txt for CI/CD

### Phase 2: Event Endpoints Testing

#### 2.1 Test Event API endpoints (`/api/events/`)
- **Unit tests**: Test individual event CRUD operations
- **Integration tests**: Test complete event workflows
- **Test coverage areas**:
  - Event creation, retrieval, updating, deletion
  - Event validation and error handling
  - Event filtering and search functionality

### Phase 3: Chat Endpoints Testing

#### 3.1 Test Chat API endpoints (`/api/chat/`)
- **Unit tests**: Test individual chat message processing
- **Integration tests**: Test complete chat workflows
- **Test coverage areas**:
  - Chat message handling and response generation
  - Chat session management
  - Chat error handling and edge cases

### Phase 4: Authentication and Models Testing

#### 4.1 Test Authentication and User Management
- **Unit tests**: Test authentication mechanisms
- **Integration tests**: Test user session management
- **Test coverage areas**:
  - User authentication and authorization
  - Session management and security
  - Permission and access control

#### 4.2 Test Pydantic Models and Helpers
- **Unit tests**: Test data models and helper functions
- **Test coverage areas**:
  - Model validation and serialization
  - Helper function logic
  - Error handling and edge cases

#### 4.3 Test structure
```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── test_backend/
│   ├── test_api_events.py   # Event endpoint tests
│   ├── test_api_chat.py     # Chat endpoint tests
│   ├── test_models.py       # Pydantic model tests
│   └── test_helpers.py      # Helper function tests
├── test_model_module/
│   ├── test_main.py         # LLM integration tests
│   └── test_chat_models.py  # Chat model tests
├── test_base_module/
│   ├── test_mcp_client.py   # MCP client tests
│   └── test_weather.py      # Weather server tests
└── test_calendar_module/
    └── test_main.py         # Calendar module tests
```

### Phase 5: Model Module Testing

#### 5.1 Test LLM integration (`model_module/main.py`)
- Mock external LLM calls to avoid API costs
- Test configuration loading from YAML
- Test different endpoint types (LlamaCpp, OpenAI)
- Test message handling and response generation

#### 5.2 Test considerations
- Use pytest-mock for mocking external dependencies
- Test both sync and async operations
- Validate configuration parsing and error handling

### Phase 6: Migrate Existing Tests

#### 6.1 Convert unittest to pytest
- Migrate existing `test_radicale_calendar_manager.py` tests
- Convert unittest.TestCase classes to pytest functions
- Replace unittest assertions with pytest assertions
- Maintain existing test coverage

### Phase 7: Improve Test Organization

#### 7.1 Reorganize migrated tests
- Separate unit tests from integration tests
- Use pytest fixtures for test data and setup
- Add parametrized tests for better coverage
- Refactor test structure for better maintainability

### Phase 8: Testing Infrastructure

#### 8.1 Test fixtures and utilities
- Create reusable fixtures for:
  - FastAPI test client
  - Mock database data
  - Mock LLM responses
  - Test user authentication

#### 8.2 Test configuration
- Environment-specific test configurations
- Database isolation for tests
- Mock external services (CalDAV, LLM APIs)

### Phase 9: CI/CD Integration

#### 9.1 GitHub Actions workflow
- Run pytest on pull requests
- Generate coverage reports
- Test against multiple Python versions
- Cache dependencies for faster builds

#### 9.2 Coverage reporting
- Set coverage thresholds
- Generate HTML coverage reports
- Integrate with code quality tools

## Implementation Steps

### Step 1: Basic Setup (Phase 1)
1. Install pytest dependencies
2. Create `pytest.ini` configuration
3. Set up basic test directory structure
4. Create `conftest.py` with basic fixtures

### Step 2: Event Endpoints Testing (Phase 2)
1. Create FastAPI test client fixture
2. Write unit tests for event CRUD operations
3. Write integration tests for event workflows
4. Add event validation and error handling tests

### Step 3: Chat Endpoints Testing (Phase 3)
1. Write unit tests for chat message processing
2. Write integration tests for chat workflows
3. Add chat session management tests
4. Test chat error handling and edge cases

### Step 4: Authentication and Models Testing (Phase 4)
1. Write authentication and user management tests
2. Test Pydantic models and validation
3. Test helper functions and utilities
4. Add comprehensive error handling tests

### Step 5: Model Module Testing (Phase 5)
1. Create mock fixtures for LLM calls
2. Test configuration loading from YAML
3. Test model initialization and routing
4. Add integration tests with mocked responses

### Step 6: Migrate Existing Tests (Phase 6)
1. Convert existing unittest tests to pytest
2. Replace unittest assertions with pytest assertions
3. Maintain existing test coverage
4. Validate migration completeness

### Step 7: Improve Test Organization (Phase 7)
1. Reorganize migrated tests
2. Separate unit tests from integration tests
3. Add parametrized tests for better coverage
4. Refactor test structure for maintainability

### Step 8: Testing Infrastructure (Phase 8)
1. Create comprehensive test fixtures
2. Set up environment-specific configurations
3. Configure database isolation for tests
4. Mock external services (CalDAV, LLM APIs)

### Step 9: CI/CD Setup (Phase 9)
1. Create GitHub Actions workflow
2. Configure coverage reporting
3. Set up automated testing triggers
4. Test against multiple Python versions

## Benefits of Migration

1. **Better Test Organization**: Pytest's fixture system and test discovery
2. **Improved Async Support**: Better async/await testing with pytest-asyncio
3. **Enhanced Mocking**: Superior mocking capabilities with pytest-mock
4. **Better Coverage**: More comprehensive test coverage reporting
5. **CI/CD Integration**: Easier integration with GitHub Actions
6. **Developer Experience**: Better test output and debugging capabilities

## Required Dependencies

```
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
httpx>=0.24.0
```
