# Nomadly3 Clean Architecture

This directory contains the clean architecture implementation of the Nomadly3 Domain Registration Bot.

## Architecture Overview

The application follows clean architecture principles with clear separation of concerns:

```
app/
├── api/                 # API Layer - FastAPI routes and endpoints
│   └── routes/         # Route modules for different domains
├── core/               # Core Layer - Configuration, security, database
├── models/             # Entity Layer - Database models and domain entities  
├── repositories/       # Data Access Layer - Database operations
├── schemas/           # Interface Layer - Pydantic schemas for validation
├── services/          # Business Logic Layer - Application services
└── main.py           # Application entry point
```

## Layer Responsibilities

### 1. API Layer (`api/`)
- FastAPI routes and endpoints
- Request/response handling
- HTTP-specific logic
- Dependency injection setup

### 2. Core Layer (`core/`)
- Application configuration (`config.py`)
- Security utilities (`security.py`) 
- Database connection management (`database.py`)
- External API integrations (`cloudflare.py`, `openprovider.py`)

### 3. Models Layer (`models/`)
- SQLAlchemy database models
- Domain entities and business objects
- Database relationships and constraints

### 4. Repositories Layer (`repositories/`)
- Data access patterns
- Database query operations
- Data persistence logic
- Repository pattern implementation

### 5. Schemas Layer (`schemas/`)
- Pydantic models for API validation
- Request/response schemas
- Data transfer objects (DTOs)

### 6. Services Layer (`services/`)
- Business logic implementation
- Use case orchestration
- Integration between repositories
- External service communication

## Key Features

### Clean Architecture Benefits
- **Separation of Concerns**: Each layer has a single responsibility
- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Testability**: Business logic isolated from frameworks and external concerns
- **Maintainability**: Changes in one layer don't affect others
- **Scalability**: Easy to add new features and modify existing ones

### Database Models
- **User**: User accounts with language preferences and wallet balance
- **UserState**: Conversation state management for bot interactions
- **RegisteredDomain**: Domain registrations with DNS and nameserver management
- **OpenProviderContact**: Contact information for domain registration  
- **DNSRecord**: DNS records for registered domains
- **WalletTransaction**: Transaction history and payment tracking
- **Order**: Order management for domain registrations and services

### Repository Pattern
- Centralized data access through repository interfaces
- Database operations abstracted from business logic
- Support for unit testing with mock repositories

### Service Layer Architecture
- **UserService**: User management and authentication
- **DomainService**: Domain registration and management
- **DNSService**: DNS record management and Cloudflare integration
- **WalletService**: Payment processing and wallet operations

## Configuration

The application uses environment-based configuration through `core/config.py`:

```python
from app.core.config import config

# Access configuration values
bot_token = config.TELEGRAM_BOT_TOKEN
database_url = config.DATABASE_URL
```

## Database Integration

Database operations use SQLAlchemy with the repository pattern:

```python
from app.core.database import get_db_session
from app.repositories.user_repo import UserRepository

# Get database session
with get_db_session() as db:
    user_repo = UserRepository(db)
    user = user_repo.get_by_telegram_id(123456)
```

## API Usage

FastAPI endpoints follow RESTful conventions:

```bash
# Get all users
GET /api/users/

# Get specific user
GET /api/users/{telegram_id}

# Create new user
POST /api/users/

# Update user
PUT /api/users/{telegram_id}
```

## Migration from Monolithic Architecture

This clean architecture implementation provides:

1. **Improved Maintainability**: Code is organized by responsibility rather than technical concerns
2. **Better Testability**: Business logic can be tested independently of frameworks
3. **Enhanced Scalability**: New features can be added without affecting existing code
4. **Clearer Dependencies**: Dependencies flow inward from external to internal layers
5. **Framework Independence**: Business logic is not coupled to FastAPI, SQLAlchemy, or Telegram

## Development Guidelines

### Adding New Features

1. **Define Models**: Add database models in `models/`
2. **Create Repositories**: Implement data access in `repositories/`
3. **Build Services**: Add business logic in `services/`
4. **Design Schemas**: Create validation schemas in `schemas/`
5. **Implement Routes**: Add API endpoints in `api/routes/`

### Testing Strategy

- **Unit Tests**: Test business logic in services layer
- **Integration Tests**: Test repository layer with database
- **API Tests**: Test endpoints with mock services
- **End-to-End Tests**: Test complete user workflows

### Code Organization

- Keep imports within layer boundaries
- Use dependency injection for external dependencies
- Follow single responsibility principle
- Implement proper error handling at each layer

## Future Enhancements

- Add comprehensive unit tests for all services
- Implement caching layer for improved performance
- Add event-driven architecture for domain events
- Implement CQRS pattern for read/write separation
- Add API versioning and documentation
- Implement monitoring and logging infrastructure