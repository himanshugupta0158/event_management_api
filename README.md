# Event Management API

This repository provides a FastAPI-based Event Management API with JWT-based authentication (without a user model in the database).

## Key Components

1. **Dockerfile**
   - Contains instructions for building a Docker image that runs the FastAPI app on Uvicorn.
2. **app/main.py**
   - Bootstraps the FastAPI application.
   - Initializes routes for event and attendee management.
3. **app/auth.py**
   - Provides JWT-based authentication utilities (token creation, password hashing/verification).
   - Currently does not rely on any actual user database model.

## Quick Start

1. **Install dependencies (local development)**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Using Make Commands**:

   ```bash
   # Build the Docker containers
   make build

   # Start the application
   make up

   # Stop the application
   make down
   ```

3. **API Docs**:  
   Access the interactive documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

## Database Migrations with Alembic

### Initial Setup

```bash
# Initialize Alembic
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "description_of_changes"
```

### Migration Commands

```bash
# Apply all pending migrations
alembic upgrade head

# Upgrade to a specific version
alembic upgrade <revision_id>

# Downgrade to previous version
alembic downgrade -1

# Downgrade to base (removes all migrations)
alembic downgrade base

# View migration history
alembic history

# View current migration version
alembic current
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
DATABASE_URL=postgresql://user:password@db:5432/dbname
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
```

## Development Workflow

1. Make changes to SQLAlchemy models in `app/models/`
2. Create a new migration:
   ```bash
   alembic revision --autogenerate -m "describe_your_changes"
   ```
3. Review the generated migration in `alembic/versions/`
4. Apply the migration:
   ```bash
   alembic upgrade head
   ```
5. If something goes wrong, you can rollback:
   ```bash
   alembic downgrade -1
   ```

## Notes

- **User Model Removed**: All references to a user model in the database have been removed. The `auth.py` module still contains logic for generating and validating JWT tokens, which you may integrate with any future or external user service.
- **Database Migrations**: Always backup your database before running migrations in production.
- **Make Commands**: The Makefile provides shortcuts for common Docker operations. View the Makefile for all available commands.

## Troubleshooting

- If migrations fail, check the database connection string in your `.env` file
- Ensure PostgreSQL is running and accessible before applying migrations
- For migration errors, check the alembic logs and version history
