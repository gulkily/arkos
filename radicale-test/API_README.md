# ARK Calendar API Documentation

A comprehensive REST API for calendar management with Radicale CalDAV integration, natural language processing, and modern OpenAPI documentation.

## 🚀 Features

- **Full CRUD Operations**: Create, read, update, and delete calendar events
- **Calendar Management**: List and manage multiple calendars
- **Date Range Filtering**: Query events within specific time periods
- **Natural Language Interface**: Chat-based calendar operations
- **CalDAV Integration**: Full compatibility with Radicale server
- **Interactive Documentation**: Swagger UI with live testing
- **Async Operations**: High-performance async endpoints

## 📁 Files Overview

### Core API Files

1. **`calendar-api-spec.yaml`** - Complete OpenAPI 3.0.3 specification
2. **`enhanced_backend_api.py`** - Production-ready FastAPI implementation
3. **`api-documentation.html`** - Interactive Swagger UI documentation

### Integration Components

- **`radicale_calendar_manager.py`** - CalDAV server interface
- **`langchain_mcp_integration.py`** - Natural language processing
- **`mcp_radicale_server.py`** - MCP-compliant server

## 🛠️ Setup and Installation

### Prerequisites

```bash
# Install required packages
pip install fastapi uvicorn python-multipart caldav python-dotenv pydantic

# Optional: For natural language features
pip install langchain langchain-openai
```

### Environment Configuration

Create a `.env` file in the project root:

```env
# Radicale CalDAV Server Configuration
RADICALE_URL=http://localhost:5232
RADICALE_USERNAME=your_username
RADICALE_PASSWORD=your_password

# Optional: OpenAI API for enhanced chat features
OPENAI_API_KEY=your_openai_api_key
```

### Starting the API Server

```bash
# Method 1: Direct execution
python enhanced_backend_api.py

# Method 2: Using uvicorn (recommended for production)
uvicorn enhanced_backend_api:app --host 0.0.0.0 --port 8000 --reload

# Method 3: With custom configuration
uvicorn enhanced_backend_api:app --host 0.0.0.0 --port 8080 --workers 4
```

### Accessing Documentation

1. **Interactive Swagger UI**: Open `api-documentation.html` in your browser
2. **FastAPI Auto-docs**: Visit `http://localhost:8000/docs`
3. **ReDoc**: Visit `http://localhost:8000/redoc`

## 📚 API Endpoints

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API health check |

### Calendar Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/calendars` | List all available calendars |
| `GET` | `/api/calendars/{calendar_id}` | Get specific calendar details |

### Event Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/events` | List events (with filtering) |
| `POST` | `/api/events` | Create new event |
| `GET` | `/api/events/{event_id}` | Get specific event |
| `PUT` | `/api/events/{event_id}` | Update existing event |
| `DELETE` | `/api/events/{event_id}` | Delete event |

### Natural Language Interface

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat/message` | Process natural language requests |
| `GET` | `/api/chat/suggestions` | Get suggested commands |

## 🔍 Usage Examples

### 1. List Events

```bash
# Get all events
curl -X GET "http://localhost:8000/api/events"

# Filter by date range
curl -X GET "http://localhost:8000/api/events?start_date=2025-06-01T00:00:00Z&end_date=2025-06-30T23:59:59Z"

# Filter by calendar
curl -X GET "http://localhost:8000/api/events?calendar_name=Work%20Calendar"
```

### 2. Create Event

```bash
curl -X POST "http://localhost:8000/api/events" \
  -H "Content-Type: application/json" \
  -d '{
    "calendar_name": "Work Calendar",
    "summary": "Team Meeting",
    "description": "Weekly team synchronization",
    "start": "2025-06-15T14:00:00Z",
    "end": "2025-06-15T15:00:00Z",
    "location": "Conference Room A"
  }'
```

### 3. Update Event

```bash
curl -X PUT "http://localhost:8000/api/events/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Updated Team Meeting",
    "location": "Conference Room B"
  }'
```

### 4. Natural Language Request

```bash
curl -X POST "http://localhost:8000/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Schedule a meeting tomorrow at 2pm"
  }'
```

### 5. Delete Event

```bash
curl -X DELETE "http://localhost:8000/api/events/550e8400-e29b-41d4-a716-446655440000"
```

## 📊 Response Examples

### Successful Event Creation

```json
{
  "event": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "summary": "Team Meeting",
    "description": "Weekly team synchronization",
    "start": "2025-06-15T14:00:00Z",
    "end": "2025-06-15T15:00:00Z",
    "location": "Conference Room A",
    "calendar": "Work Calendar",
    "status": "confirmed",
    "visibility": "public",
    "created_at": "2025-06-01T10:00:00Z",
    "updated_at": "2025-06-01T10:00:00Z"
  },
  "message": "Event created successfully",
  "event_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Events List Response

```json
{
  "events": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "summary": "Team Standup",
      "start": "2025-06-15T09:00:00Z",
      "end": "2025-06-15T09:30:00Z",
      "location": "Conference Room A",
      "calendar": "Work Calendar"
    }
  ],
  "total_count": 1,
  "calendar": "Work Calendar",
  "date_range": {
    "start": "2025-06-01T00:00:00Z",
    "end": "2025-06-30T23:59:59Z"
  }
}
```

### Chat Response

```json
{
  "response": "I'll help you schedule a meeting for tomorrow at 2pm. What would you like to call this meeting?",
  "action": "create_event",
  "data": {
    "suggested_event": {
      "start": "2025-06-16T14:00:00Z",
      "end": "2025-06-16T15:00:00Z"
    }
  },
  "confidence": 0.95,
  "suggestions": [
    "Schedule a team meeting tomorrow at 2pm",
    "Add a project review meeting"
  ]
}
```

## 🔧 Configuration Options

### Query Parameters for Events

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `calendar_name` | string | Filter by calendar | `Work Calendar` |
| `start_date` | datetime | Filter start date | `2025-06-01T00:00:00Z` |
| `end_date` | datetime | Filter end date | `2025-06-30T23:59:59Z` |
| `limit` | integer | Max results (1-1000) | `50` |
| `offset` | integer | Skip results | `10` |

### Event Data Fields

#### Required Fields (for creation)
- `calendar_name`: Target calendar name
- `summary`: Event title
- `start`: Start datetime (ISO 8601)

#### Optional Fields
- `description`: Event description
- `end`: End datetime (defaults to start + 1 hour)
- `location`: Event location
- `status`: confirmed, tentative, cancelled
- `visibility`: public, private, confidential

## ⚠️ Error Handling

The API uses standard HTTP status codes and returns structured error responses:

```json
{
  "error": "ValidationError",
  "message": "Event summary is required",
  "details": {
    "field": "summary",
    "provided_value": null
  },
  "timestamp": "2025-06-15T10:00:00Z"
}
```

### Common Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `404` - Not Found
- `409` - Conflict (concurrent modification)
- `500` - Internal Server Error
- `503` - Service Unavailable (CalDAV server down)

## 🧪 Testing

### Using the Interactive Documentation

1. Open `api-documentation.html` in your browser
2. Select your server URL (development/production)
3. Use the "Try it out" feature for each endpoint
4. View real responses and examples

### Automated Testing

```bash
# Run the test suite
python test_langchain_integration.py
python test_mcp_compliance.py

# Enhanced client testing
python test_mcp_client.py
```

### Manual Testing with curl

See the usage examples above for curl commands to test each endpoint.

## 🔒 Security Considerations

- **Authentication**: Implement proper authentication for production
- **CORS**: Configure CORS origins appropriately
- **Rate Limiting**: Add rate limiting for production deployments
- **Input Validation**: All inputs are validated using Pydantic models
- **Error Handling**: Errors don't expose sensitive information

## 🌐 Integration with Frontend

The API is designed to work seamlessly with modern frontend frameworks:

### React/Vue.js Example

```javascript
// Fetch events
const response = await fetch('/api/events?start_date=2025-06-01T00:00:00Z');
const data = await response.json();

// Create event
const newEvent = await fetch('/api/events', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    calendar_name: 'Work Calendar',
    summary: 'Team Meeting',
    start: '2025-06-15T14:00:00Z',
    end: '2025-06-15T15:00:00Z'
  })
});
```

### Natural Language Interface

```javascript
// Send chat message
const chatResponse = await fetch('/api/chat/message', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Schedule a meeting tomorrow at 2pm'
  })
});

const result = await chatResponse.json();
// result.action tells you what action to take
// result.data contains suggested parameters
```

## 📈 Performance Notes

- **Async Operations**: All endpoints are async for better performance
- **Connection Pooling**: CalDAV connections are reused
- **Caching**: Consider implementing Redis for production caching
- **Pagination**: Use `limit` and `offset` for large datasets

## 🔄 Development Workflow

1. **Modify API**: Update `enhanced_backend_api.py`
2. **Update Spec**: Modify `calendar-api-spec.yaml`
3. **Test Changes**: Use interactive documentation
4. **Run Tests**: Execute test suites
5. **Deploy**: Use uvicorn for production deployment

## 📞 Support and Contributing

- **Issues**: Report bugs via GitHub issues
- **Documentation**: API docs are auto-generated from code
- **Contributing**: Follow the existing code style and add tests
- **Questions**: Contact the development team

---

**Note**: This API integrates with your existing Radicale CalDAV server and provides a modern REST interface for calendar operations. Make sure your Radicale server is running and accessible before starting the API server.