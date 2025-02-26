# Event Management API

This repository provides a minimal FastAPI-based Event Management API with JWT-based authentication (without a user model in the database). 

## Key Components

1. **Dockerfile**  
   - Contains instructions for building a Docker image that runs the FastAPI app on Uvicorn.
2. **app/main.py**  
   - Bootstraps the FastAPI application.
   - Initializes routes for event and attendee management (if you choose to add them).
3. **app/auth.py**  
   - Provides JWT-based authentication utilities (token creation, password hashing/verification).
   - Currently does not rely on any actual user database model.

## Quick Start

1. **Install dependencies (local development)**:   ```bash
   pip install -r requirements.txt   ```
2. **Build & run via Docker**:   ```bash
   docker build -t event-management-api .
   docker run -p 8000:8000 event-management-api   ```
   Your API will be available at http://localhost:8000.
3. **API Docs**:  
   Access the interactive documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

## Project Layout (Simplified)

```
event_management/
├── app/
│   ├── main.py            # Core FastAPI app setup
│   ├── auth.py            # JWT-based auth logic (no user DB model)
│   └── ...                # (Optional) Additional routes for events/attendees
├── Dockerfile             # Docker setup file
├── requirements.txt       # Python dependencies
└── README.md              # This documentation
```

## Notes

- **User Model Removed**: All references to a user model in the database have been removed. The `auth.py` module still contains logic for generating and validating JWT tokens, which you may integrate with any future or external user service.
- **Extend as Needed**: You can add event and attendee routes (and models) if you want to track events or participants. 

Happy coding!
