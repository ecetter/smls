#!/usr/bin/env python3
"""
Gunicorn Configuration for SMLS Production Deployment

This configuration file defines the production settings for running SMLS
with Gunicorn WSGI server. It implements enterprise-grade performance
optimization, security hardening, and operational monitoring features.

Key Configuration Areas:
- Worker Process Management: Multi-process architecture for scalability
- Security Hardening: Request limits and security headers
- Performance Optimization: Connection pooling and resource management
- Monitoring and Logging: Comprehensive operational visibility
- Graceful Operations: Clean startup, shutdown, and worker recycling

Production Features:
- Automatic worker restarts to prevent memory leaks
- Request size limits to prevent DoS attacks
- Comprehensive logging for security and performance monitoring
- Graceful shutdown handling for zero-downtime deployments
- Resource optimization for high-throughput scenarios

Author: SMLS Development Team
Version: 1.0.0
License: MIT
"""

import os
import multiprocessing

# =============================================================================
# SERVER SOCKET CONFIGURATION
# =============================================================================

# Bind address and port for the Gunicorn server
# Using 0.0.0.0 to accept connections from all network interfaces
# Port 5000 is the standard internal port for the application
bind = "0.0.0.0:5000"

# Maximum number of pending connections in the listen queue
# Higher values allow more concurrent connection attempts
backlog = 2048

# =============================================================================
# WORKER PROCESS CONFIGURATION
# =============================================================================

# Number of worker processes for handling requests
# Formula: (2 x CPU cores) + 1, capped at 4 for resource efficiency
# This provides optimal balance between concurrency and resource usage
workers = min(4, multiprocessing.cpu_count() * 2 + 1)

# Worker class for request handling
# 'sync' workers are reliable and suitable for most applications
# Alternative: 'gevent' for I/O-bound applications with many concurrent connections
worker_class = "sync"

# Maximum number of simultaneous clients per worker
# Higher values allow more concurrent requests per worker process
worker_connections = 1000

# Request timeout in seconds
# Requests taking longer than this will be terminated
# 30 seconds provides reasonable timeout for most web operations
timeout = 30

# Keep-alive timeout in seconds
# How long to keep connections open for subsequent requests
# 2 seconds balances performance with resource usage
keepalive = 2

# =============================================================================
# WORKER LIFECYCLE MANAGEMENT
# =============================================================================

# Restart workers after processing this many requests
# Prevents memory leaks by recycling worker processes
# 1000 requests provides good balance between stability and performance
max_requests = 1000

# Random jitter for max_requests to prevent all workers restarting simultaneously
# Adds randomness to prevent thundering herd problems during worker recycling
max_requests_jitter = 50

# Preload the application for better performance
# Loads the application code once and shares it across all worker processes
# Reduces memory usage and improves startup time
preload_app = True

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Access log file path
# Records all HTTP requests with detailed information
accesslog = "persist/logs/gunicorn_access.log"

# Error log file path
# Records server errors, worker issues, and application exceptions
errorlog = "persist/logs/gunicorn_error.log"

# Log level for error messages
# 'info' provides good balance between detail and performance
loglevel = "info"

# Access log format string
# Custom format providing comprehensive request information:
# %(h)s - Remote host IP address
# %(l)s - Remote logname (usually '-')
# %(u)s - Remote user (usually '-')
# %(t)s - Request timestamp
# %(r)s - Request line (method, path, protocol)
# %(s)s - HTTP status code
# %(b)s - Response size in bytes
# %(f)s - Referer header
# %(a)s - User-Agent header
# %(D)s - Request duration in microseconds
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process name for system monitoring
# Helps identify SMLS processes in system monitoring tools
proc_name = "smls"

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# Maximum size of HTTP request line
# Prevents buffer overflow attacks and DoS via oversized requests
# 4094 bytes is the standard HTTP/1.1 limit
limit_request_line = 4094

# Maximum number of HTTP request header fields
# Prevents DoS attacks via header flooding
# 100 headers is reasonable for most applications
limit_request_fields = 100

# Maximum size of HTTP request header field
# Prevents buffer overflow attacks via oversized headers
# 8190 bytes allows for reasonable header sizes
limit_request_field_size = 8190

# =============================================================================
# PERFORMANCE OPTIMIZATION
# =============================================================================

# Worker temporary directory
# Use shared memory for better performance if available
# Falls back to default system temp directory if /dev/shm not available
worker_tmp_dir = "/dev/shm" if os.path.exists("/dev/shm") else None

# Graceful shutdown timeout
# Time to wait for workers to finish current requests before force termination
# 30 seconds provides reasonable time for request completion
graceful_timeout = 30

# =============================================================================
# USER AND GROUP CONFIGURATION
# =============================================================================

# User and group for running worker processes
# Uncomment and configure for production deployments with specific user requirements
# user = "nobody"
# group = "nogroup"

# =============================================================================
# WORKER LIFECYCLE HOOKS
# =============================================================================

def when_ready(server):
    """
    Called just after the server is started and ready to accept connections.
    
    This hook is useful for:
    - Logging server startup completion
    - Initializing external monitoring systems
    - Performing health checks
    - Notifying external systems of service availability
    
    Args:
        server: Gunicorn server instance
    """
    server.log.info("SMLS Gunicorn server is ready to serve requests")

def worker_int(worker):
    """
    Called just after a worker exited on SIGINT or SIGQUIT.
    
    This hook is useful for:
    - Logging worker termination events
    - Cleaning up worker-specific resources
    - Updating monitoring systems
    - Performing graceful shutdown procedures
    
    Args:
        worker: Gunicorn worker instance
    """
    worker.log.info("Worker received SIGINT or SIGQUIT")

def pre_fork(server, worker):
    """
    Called just before a worker is forked.
    
    This hook is useful for:
    - Logging worker creation events
    - Initializing worker-specific resources
    - Setting up monitoring for new workers
    - Performing pre-fork optimizations
    
    Args:
        server: Gunicorn server instance
        worker: Gunicorn worker instance
    """
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_fork(server, worker):
    """
    Called just after a worker has been forked.
    
    This hook is useful for:
    - Logging successful worker creation
    - Initializing worker-specific resources
    - Setting up monitoring for new workers
    - Performing post-fork optimizations
    
    Args:
        server: Gunicorn server instance
        worker: Gunicorn worker instance
    """
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def worker_abort(worker):
    """
    Called when a worker received the SIGABRT signal.
    
    This hook is useful for:
    - Logging worker abort events
    - Cleaning up worker resources
    - Updating monitoring systems
    - Performing emergency shutdown procedures
    
    Args:
        worker: Gunicorn worker instance
    """
    worker.log.info(f"Worker received SIGABRT (pid: {worker.pid})")