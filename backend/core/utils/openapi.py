"""OpenAPI schema customization"""

def get_openapi_schema(app):
    """Get customized OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = {
        "openapi": "3.0.2",
        "info": {
            "title": "My Agent API",
            "description": "AI-powered Software Engineering Agent API",
            "version": "1.0.0-alpha",
            "contact": {
                "name": "Savaş Aldemir",
                "url": "https://github.com/savasaldemir",
                "email": "savas@example.com",
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT",
            },
        },
        "servers": [
            {
                "url": "http://localhost:8000",
                "description": "Development Server"
            },
            {
                "url": "https://api.myagent.dev",
                "description": "Production Server"
            }
        ],
        "paths": {},
        "components": {
            "securitySchemes": {
                "HTTPBearer": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JWT token authentication"
                }
            }
        },
        "tags": [
            {
                "name": "auth",
                "description": "Authentication endpoints"
            },
            {
                "name": "users",
                "description": "User management"
            },
            {
                "name": "projects",
                "description": "Project management"
            },
            {
                "name": "analyses",
                "description": "Code analysis"
            },
            {
                "name": "sessions",
                "description": "Session management"
            },
            {
                "name": "health",
                "description": "Health checks"
            }
        ]
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema
