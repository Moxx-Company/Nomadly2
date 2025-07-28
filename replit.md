# Nomadly3 Bot - Architecture Overview

## Overview
Nomadly3 is a comprehensive Telegram bot system for domain registration and management, built with Python and featuring integration with OpenProvider for domain registration, Cloudflare for DNS management, and BlockBee for cryptocurrency payments. The system is designed with a modular architecture supporting multilingual operations and automated domain lifecycle management.

## User Preferences
Preferred communication style: Simple, everyday language.

## Recent Critical Security Fixes (July 25, 2025)
- **Payment System Vulnerability Discovered & Fixed**: Found dangerous payment monitor logic creating false blockchain confirmations without real payments
- **Root Cause**: System was processing payments based on database status rather than actual blockchain verification via BlockBee API
- **Security Impact**: Could have allowed domain registrations without payment 
- **Fix Applied**: Removed database-based payment confirmation logic, now only accepts genuine BlockBee webhook confirmations
- **Domain Service Fixed**: Created missing identity_generator module for WHOIS privacy protection

## System Architecture

### Backend Architecture
- **Framework**: Python-based Telegram bot using python-telegram-bot library
- **Database**: PostgreSQL with SQLAlchemy ORM for data persistence
- **API Layer**: FastAPI for webhook handling and external integrations
- **Payment Processing**: BlockBee integration for cryptocurrency payments (BTC, ETH, LTC, DOGE)
- **Domain Management**: OpenProvider API for domain registration and management
- **DNS Management**: Cloudflare API for DNS record management and zone creation

### Database Design
The system uses a well-structured relational database with the following core entities:
- **Users**: Customer accounts with language preferences and wallet balances
- **RegisteredDomains**: Domain records with OpenProvider and Cloudflare integration data
- **Orders**: Payment tracking and order management
- **WalletTransactions**: Financial transaction history
- **DNSRecords**: DNS record management for domains
- **UserState**: Conversation state management for bot interactions

### Service Layer Architecture
The application follows a clean service-oriented architecture:
- **Repository Layer**: Data access abstraction (DOMAIN_BOT_REPOSITORY_LAYER.py)
- **Service Layer**: Business logic implementation (DOMAIN_BOT_SERVICE_LAYER.py)
- **Database Models**: Clean SQLAlchemy models (DOMAIN_BOT_DATABASE_MODELS.py)

## Key Components

### Domain Registration Workflow
1. **Domain Search**: Real-time availability checking via OpenProvider API
2. **Payment Processing**: Cryptocurrency payment validation through BlockBee
3. **DNS Setup**: Automatic Cloudflare zone creation with default A records
4. **Domain Registration**: OpenProvider registration with pre-configured nameservers
5. **Confirmation**: Multi-channel notification system (Telegram + Email)

### Payment System
- **Supported Cryptocurrencies**: Bitcoin, Ethereum, Litecoin, Dogecoin
- **Real-time Monitoring**: Background payment monitoring service
- **Address Generation**: Dynamic payment address creation per order
- **Webhook Integration**: BlockBee webhook processing for payment confirmation

### Admin Panel
- **Web Interface**: Flask-based admin dashboard for system management
- **User Management**: Customer overview and domain management
- **Revenue Tracking**: Financial reporting and analytics
- **System Monitoring**: Health checks and performance metrics

### Bot Interaction System
- **Multilingual Support**: English, French, Spanish, Hindi, Chinese
- **Callback Routing**: Comprehensive callback handler system with namespaced routing
- **State Management**: Persistent conversation state tracking
- **Button Responsiveness**: Optimized for instant user feedback

## Data Flow

### Domain Registration Flow
1. User initiates domain search through Telegram bot
2. System queries OpenProvider for availability and pricing
3. User selects payment method (cryptocurrency)
4. BlockBee generates payment address and monitors blockchain
5. Upon payment confirmation, Cloudflare zone is created
6. Domain is registered with OpenProvider using Cloudflare nameservers
7. User receives confirmation via Telegram and email

### DNS Management Flow
1. User accesses domain management interface
2. System retrieves current DNS records from Cloudflare
3. User can add/edit/delete DNS records through bot interface
4. Changes are applied to Cloudflare zone in real-time
5. System provides propagation status updates

## External Dependencies

### Core API Integrations
- **OpenProvider API**: Domain registration, customer management, domain lifecycle
- **Cloudflare API**: DNS zone management, record manipulation, nameserver configuration
- **BlockBee API**: Cryptocurrency payment processing and monitoring
- **Telegram Bot API**: User interaction and notification delivery

### Database Dependencies
- **PostgreSQL**: Primary data storage with ACID compliance
- **SQLAlchemy**: ORM for database interactions and schema management
- **Alembic**: Database migration management (if implemented)

### Infrastructure Dependencies
- **Redis**: Session state management and background job queuing (optional)
- **Background Workers**: Celery for asynchronous task processing
- **Email Service**: SMTP integration for email notifications

## Deployment Strategy

### Production Configuration
- **Environment Variables**: Secure API credential management
- **Database Connections**: Connection pooling and timeout configuration
- **Error Handling**: Comprehensive logging and error tracking
- **Health Monitoring**: API status checking and automated alerts

### Scalability Considerations
- **Background Processing**: Queue-based domain registration to handle timeouts
- **API Rate Limiting**: Proper request throttling for external APIs
- **Database Optimization**: Indexed queries and connection management
- **Webhook Processing**: Asynchronous payment confirmation handling

### Security Implementation
- **API Authentication**: Bearer token management for external services
- **Data Validation**: Input sanitization and SQL injection prevention
- **User Privacy**: WHOIS privacy protection and secure data handling
- **Payment Security**: Secure cryptocurrency address generation and validation

The system demonstrates a mature architecture with proper separation of concerns, comprehensive error handling, and robust integration patterns suitable for production deployment in a domain registration service environment.