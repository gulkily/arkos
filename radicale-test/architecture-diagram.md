# Radicale Calendar Integration - Architecture Diagram

## System Architecture

```mermaid
graph TB
    %% External Systems
    subgraph "External Systems"
        GCal[Google Calendar API]
        OpenAI[OpenAI API]
        RadicaleServer[Radicale CalDAV Server]
    end

    %% Core Layer
    subgraph "Core Calendar Management"
        RCM[RadicaleCalendarManager<br/>radicale_calendar_manager.py]
    end

    %% Integration Layer
    subgraph "Integration Bridges"
        MCPBridge[MCP Radicale Bridge<br/>mcp_radicale_bridge.py]
        LCAdapter[LangChain Tool Adapter<br/>langchain_tool_adapter.py]
        GSync[Google Calendar Sync<br/>google_radicale_sync.py]
    end

    %% Application Layer
    subgraph "Applications & Examples"
        LCExample[LangChain Example<br/>langchain_example.py]
        MCPClient[MCP Test Client<br/>test_mcp_client.py]
        TestScripts[Test Scripts<br/>test_new_event_*.py<br/>test_read_event.py]
    end

    %% Testing Layer
    subgraph "Testing Framework"
        MainTests[Main Test Suite<br/>test_radicale_calendar_manager.py]
        EdgeTests[Edge Case Tests<br/>test_radicale_calendar_manager_edge_cases.py]
    end

    %% Configuration
    subgraph "Configuration"
        EnvConfig[Environment Variables<br/>.env file]
        ServiceConfig[Systemd Service<br/>mcp-radicale.service]
        HowTo[Setup Guide<br/>radicale_howto.txt]
    end

    %% Data Flow Connections
    RCM --> RadicaleServer
    
    MCPBridge --> RCM
    LCAdapter --> RCM
    GSync --> RCM
    GSync --> GCal
    
    LCExample --> LCAdapter
    LCExample --> OpenAI
    MCPClient --> MCPBridge
    TestScripts --> RCM
    
    MainTests --> RCM
    EdgeTests --> MainTests
    
    EnvConfig -.-> RCM
    EnvConfig -.-> MCPBridge
    EnvConfig -.-> LCExample
    EnvConfig -.-> GSync
    
    ServiceConfig -.-> MCPBridge
    HowTo -.-> RadicaleServer

    %% WebSocket connection
    MCPBridge -.->|WebSocket<br/>localhost:8765| MCPClient

    %% Legend
    classDef coreClass fill:#e1f5fe
    classDef bridgeClass fill:#f3e5f5
    classDef appClass fill:#e8f5e8
    classDef testClass fill:#fff3e0
    classDef configClass fill:#fce4ec
    classDef externalClass fill:#f1f8e9

    class RCM coreClass
    class MCPBridge,LCAdapter,GSync bridgeClass
    class LCExample,MCPClient,TestScripts appClass
    class MainTests,EdgeTests testClass
    class EnvConfig,ServiceConfig,HowTo configClass
    class GCal,OpenAI,RadicaleServer externalClass
```

## Component Interaction Flow

### 1. Direct Calendar Operations
```
TestScripts → RadicaleCalendarManager → Radicale Server
```

### 2. LangChain AI Calendar Assistant
```
User Query → LangChain Example → OpenAI API
           ↓
LangChain Tool Adapter → RadicaleCalendarManager → Radicale Server
```

### 3. MCP Bridge Communication
```
MCP Client → WebSocket → MCP Bridge → RadicaleCalendarManager → Radicale Server
```

### 4. Google Calendar Sync
```
Google Calendar API ↔ Google Sync ↔ RadicaleCalendarManager ↔ Radicale Server
```

## Key Integration Points

1. **RadicaleCalendarManager**: Central hub for all calendar operations
2. **Environment Configuration**: Shared across all components via .env
3. **WebSocket Protocol**: MCP Bridge communication standard
4. **LangChain Tools**: AI-powered natural language interface
5. **Testing Framework**: Comprehensive validation of all components

## Data Flow Patterns

- **Synchronous**: Direct calendar operations, testing
- **Asynchronous**: MCP WebSocket communication
- **Bi-directional**: Google Calendar synchronization
- **AI-Enhanced**: LangChain natural language processing