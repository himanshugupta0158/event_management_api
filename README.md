# Event Management API

This repository provides a FastAPI-based Event Management API with JWT-based authentication (without a user model in the database).

## Key Components

1. **Dockerfile**
   - Contains instructions for building a Docker image that runs the FastAPI app on Uvicorn.
2. **app/main.py**
   - Bootstraps the FastAPI application.
   - Initializes routes for auth, event and attendee management.
3. **app/routes/auth.py**
   - Provides JWT-based authentication utilities (token creation, password hashing/verification).
   - Create new user, login and logout.

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
   Access the interactive documentation at [http://localhost:8100/docs](http://localhost:8100/docs).

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
DATABASE_URL=postgresql://user:password@db:5432/dbname
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
```

## Notes
- **Make Commands**: The Makefile provides shortcuts for common Docker operations. View the Makefile for all available commands.

