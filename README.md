# Health & Wellness Advisor Crew

A multi-agent coach that turns goals like "Lose 5 kg in 12 weeks while maintaining muscle" into personalized 12-week plans across training, nutrition, mindset, and accountability, updated weekly from real-world progress and wearable data.

## 🏗️ Architecture

- **Frontend**: Next.js 14 (React 18) with TypeScript, Tailwind CSS, and shadcn/ui
- **API Gateway**: NestJS with TypeORM, JWT auth, and WebSocket support
- **Orchestrator**: FastAPI with CrewAI for multi-agent coordination
- **Workers**: Python Celery workers for background processing
- **Database**: PostgreSQL with TimescaleDB for time-series data and pgvector for embeddings
- **Cache**: Redis for session management and caching
- **Event Bus**: NATS for real-time communication
- **Storage**: MinIO/S3 for file storage
- **Monitoring**: OpenTelemetry, Prometheus, Grafana, Sentry

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ and npm 8+
- Python 3.9+

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd health-wellness-advisory-crew
   ```

2. **Copy environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start the development environment**
   ```bash
   npm run dev
   ```

4. **Access the applications**
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:3001
   - API Docs: http://localhost:3001/api/docs
   - Orchestrator: http://localhost:8000
   - Orchestrator Docs: http://localhost:8000/api/docs
   - MinIO Console: http://localhost:9001
   - NATS Monitoring: http://localhost:8222

### Manual Setup (without Docker)

1. **Install dependencies**
   ```bash
   npm run install:all
   ```

2. **Start services individually**
   ```bash
   # Start PostgreSQL, Redis, NATS, MinIO
   docker-compose -f docker-compose.dev.yml up postgres redis nats minio
   
   # Start frontend
   cd apps/frontend && npm run dev
   
   # Start gateway
   cd apps/gateway && npm run start:dev
   
   # Start orchestrator
   cd apps/orchestrator && python -m uvicorn main:app --reload
   
   # Start workers
   cd apps/workers && celery -A celery_app worker --loglevel=info
   ```

## 📁 Project Structure

```
├── apps/
│   ├── frontend/          # Next.js 14 frontend application
│   ├── gateway/           # NestJS API gateway
│   ├── orchestrator/      # FastAPI + CrewAI orchestrator
│   └── workers/           # Python Celery workers
├── packages/
│   └── sdk/              # Shared TypeScript SDK
├── scripts/              # Database initialization and utilities
├── docker-compose.dev.yml # Development environment
├── env.example           # Environment variables template
└── README.md
```

## 🔧 Development

### Frontend (Next.js 14)

```bash
cd apps/frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run ESLint
npm run test         # Run tests
```

### API Gateway (NestJS)

```bash
cd apps/gateway
npm run start:dev    # Start development server
npm run build        # Build for production
npm run lint         # Run ESLint
npm run test         # Run tests
```

### Orchestrator (FastAPI)

```bash
cd apps/orchestrator
python -m uvicorn main:app --reload  # Start development server
pytest                               # Run tests
black .                             # Format code
isort .                             # Sort imports
```

### Workers (Python)

```bash
cd apps/workers
celery -A celery_app worker --loglevel=info  # Start Celery worker
pytest                                        # Run tests
```

## 🧪 Testing

```bash
# Run all tests
npm run test

# Run tests for specific app
npm run test:frontend
npm run test:gateway
npm run test:sdk

# Run Python tests
cd apps/orchestrator && pytest
cd apps/workers && pytest
```

## 🚀 Deployment

### Production Build

```bash
# Build all applications
npm run build

# Build Docker images
docker-compose -f docker-compose.prod.yml build
```

### Environment Variables

Copy `env.example` to `.env` and configure:

- Database credentials
- Redis connection
- NATS connection
- S3/MinIO credentials
- JWT secrets
- OAuth provider credentials
- AI/LLM API keys
- Monitoring configuration

## 📊 Monitoring & Observability

- **Application Metrics**: Prometheus + Grafana
- **Error Tracking**: Sentry
- **Logging**: Structured JSON logs with correlation IDs
- **Tracing**: OpenTelemetry distributed tracing
- **Health Checks**: Built-in health endpoints

## 🔒 Security

- JWT-based authentication
- Role-based access control (RBAC)
- Input validation with Zod/Pydantic
- CORS configuration
- Rate limiting
- SQL injection prevention with TypeORM
- XSS protection with helmet

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run linting and tests
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API documentation at `/api/docs`

## 🗺️ Roadmap

- [ ] Phase 1: Database & API contracts
- [ ] Phase 2: Intake & Safety gate
- [ ] Phase 3: Nutrition engine & meals
- [ ] Phase 4: Training & workout player
- [ ] Phase 5: Habits, mindset, nudges
- [ ] Phase 6: Weekly check-ins & adjustments
- [ ] Phase 7: Device integrations
- [ ] Phase 8: Reports & exports
- [ ] Phase 9: Analytics & hardening
- [ ] Phase 10: Testing & documentation
