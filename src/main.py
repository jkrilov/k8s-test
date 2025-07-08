"""
FastAPI Kubernetes Testing Application

A comprehensive FastAPI application for testing various Kubernetes features.
"""

import asyncio
import logging
import os
import platform
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
import psutil
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENVIRONMENT = os.getenv("APP_ENVIRONMENT", "development")
DEPLOYMENT_VERSION = os.getenv("DEPLOYMENT_VERSION", "blue")

# Security
security = HTTPBearer()

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"]
)
REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP request duration")
ACTIVE_CONNECTIONS = Gauge("active_connections", "Number of active connections")


# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None


class UserInDB(User):
    hashed_password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    environment: str
    deployment_version: str
    system_info: Dict[str, Any]


class VersionResponse(BaseModel):
    version: str
    environment: str
    deployment_version: str
    build_timestamp: str


class LoadTestResponse(BaseModel):
    instance_id: str
    hostname: str
    cpu_percent: float
    memory_percent: float
    timestamp: datetime


# Mock user database
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": bcrypt.hashpw(
            "testpassword".encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8"),
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using bcrypt"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Generate a password hash using bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def get_user(username: str) -> Optional[UserInDB]:
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    return User(username=user.username, email=user.email)


# FastAPI app
app = FastAPI(
    title="Kubernetes Test API",
    description="A FastAPI application for testing Kubernetes features",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware to track metrics
@app.middleware("http")
async def track_requests(request, call_next):
    start_time = time.time()
    ACTIVE_CONNECTIONS.inc()

    try:
        response = await call_next(request)

        # Record metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
        ).inc()

        REQUEST_DURATION.observe(time.time() - start_time)

        return response
    finally:
        ACTIVE_CONNECTIONS.dec()


# Health and Basic Endpoints
@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "FastAPI Kubernetes Test Application",
        "version": APP_VERSION,
        "environment": APP_ENVIRONMENT,
        "deployment_version": DEPLOYMENT_VERSION,
        "docs_url": "/docs",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ping")
async def ping():
    """Simple ping endpoint for basic connectivity tests"""
    return {"message": "pong", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint"""
    # Get disk usage based on OS
    if platform.system() != "Windows":
        disk_usage = psutil.disk_usage("/").percent
    else:
        disk_usage = psutil.disk_usage("C:").percent

    system_info = {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "disk_usage": disk_usage,
    }

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version=APP_VERSION,
        environment=APP_ENVIRONMENT,
        deployment_version=DEPLOYMENT_VERSION,
        system_info=system_info,
    )


@app.get("/version", response_model=VersionResponse)
async def get_version():
    """Get application version information"""
    return VersionResponse(
        version=APP_VERSION,
        environment=APP_ENVIRONMENT,
        deployment_version=DEPLOYMENT_VERSION,
        build_timestamp=datetime.now(timezone.utc).isoformat(),
    )


# Authentication Endpoints
@app.post("/auth/login", response_model=Token)
async def login(login_request: LoginRequest):
    """Authenticate user and return JWT token"""
    user = authenticate_user(login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    """Protected endpoint that requires authentication"""
    return {
        "message": f"Hello {current_user.username}! This is a protected endpoint.",
        "user": current_user.model_dump(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Blue/Green Deployment Testing
@app.get("/deployment/version")
async def get_deployment_version():
    """Get current deployment version"""
    return {
        "deployment_version": DEPLOYMENT_VERSION,
        "app_version": APP_VERSION,
        "environment": APP_ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/deployment/blue")
async def blue_deployment():
    """Blue deployment endpoint"""
    return {
        "deployment": "blue",
        "message": "This is the BLUE deployment",
        "version": APP_VERSION,
        "color": "#0066CC",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/deployment/green")
async def green_deployment():
    """Green deployment endpoint"""
    return {
        "deployment": "green",
        "message": "This is the GREEN deployment",
        "version": APP_VERSION,
        "color": "#00CC66",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Load Balancing Test Endpoints
@app.get("/load-test/info", response_model=LoadTestResponse)
async def load_test_info():
    """Get instance information for load balancing tests"""
    return LoadTestResponse(
        instance_id=f"{platform.node()}-{os.getpid()}",
        hostname=platform.node(),
        cpu_percent=psutil.cpu_percent(),
        memory_percent=psutil.virtual_memory().percent,
        timestamp=datetime.now(timezone.utc),
    )


@app.get("/load-test/cpu")
async def cpu_intensive_task():
    """CPU intensive task for load testing"""
    start_time = time.time()

    # Simulate CPU intensive work
    result = 0
    for i in range(1000000):
        result += i * i

    end_time = time.time()

    return {
        "message": "CPU intensive task completed",
        "duration": end_time - start_time,
        "result": result,
        "instance_id": f"{platform.node()}-{os.getpid()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/load-test/memory")
async def memory_usage():
    """Get detailed memory usage information"""
    memory = psutil.virtual_memory()
    return {
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free,
        },
        "instance_id": f"{platform.node()}-{os.getpid()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/load-test/async")
async def async_task():
    """Async task for testing concurrent request handling"""
    start_time = time.time()

    # Simulate async work
    await asyncio.sleep(0.1)

    end_time = time.time()

    return {
        "message": "Async task completed",
        "duration": end_time - start_time,
        "instance_id": f"{platform.node()}-{os.getpid()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Monitoring and Observability
@app.get("/metrics", response_class=PlainTextResponse)
async def get_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


@app.get("/observability/logs")
async def generate_logs():
    """Generate test logs for observability testing"""
    logger.info("Info log generated via API")
    logger.warning("Warning log generated via API")
    logger.error("Error log generated via API")

    return {
        "message": "Test logs generated",
        "levels": ["info", "warning", "error"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/observability/trace")
async def trace_endpoint():
    """Endpoint for testing distributed tracing"""
    # Simulate some processing with multiple steps
    await asyncio.sleep(0.05)  # Simulate database call
    await asyncio.sleep(0.02)  # Simulate external API call

    return {
        "message": "Trace endpoint completed",
        "trace_id": f"trace-{int(time.time() * 1000)}",
        "span_count": 3,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Error Testing
@app.get("/error/500")
async def internal_server_error():
    """Endpoint that always returns 500 error"""
    raise HTTPException(status_code=500, detail="Internal Server Error - Test endpoint")


@app.get("/error/404")
async def not_found_error():
    """Endpoint that always returns 404 error"""
    raise HTTPException(status_code=404, detail="Not Found - Test endpoint")


@app.get("/error/timeout")
async def timeout_simulation():
    """Simulate a timeout scenario"""
    await asyncio.sleep(30)  # Long running task
    return {"message": "This should timeout"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )
