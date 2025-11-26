"""Celery Configuration Module.

This module configures Celery for distributed task processing in the Color Correction System.
Supports both Redis and RabbitMQ as message brokers.

Usage:
    # Start Celery worker
    celery -A celery_config worker --loglevel=info
    
    # Start Celery flower monitoring
    celery -A celery_config flower
    
    # Queue a task
    from celery_config import celery_app
    result = celery_app.send_task('tasks.process_image', args=(image_id,))
"""

import os
from celery import Celery
from config import settings

# Create Celery app instance
celery_app = Celery(
    "color_correction",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task configuration
    task_track_started=True,  # Track task start
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit (allow cleanup)
    
    # Worker configuration
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    worker_prefetch_multiplier=4,  # Number of tasks to prefetch
    worker_max_memory_per_child=200000,  # 200MB memory limit
    
    # Result backend configuration
    result_expires=3600,  # Results expire after 1 hour
    result_extended=True,  # Store extra task metadata
    
    # Broker configuration
    broker_connection_retry_on_startup=True,  # Retry connection on startup
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    
    # Task routing for different queues
    task_routes={
        'tasks.process_image': {'queue': 'processing'},
        'tasks.detect_markers': {'queue': 'detection'},
        'tasks.correct_colors': {'queue': 'correction'},
        'tasks.generate_report': {'queue': 'reporting'},
    },
    
    # Queue configuration
    task_queues=(
        ('default', {'exchange': 'default', 'routing_key': 'default'}),
        ('processing', {'exchange': 'processing', 'routing_key': 'processing'}),
        ('detection', {'exchange': 'detection', 'routing_key': 'detection'}),
        ('correction', {'exchange': 'correction', 'routing_key': 'correction'}),
        ('reporting', {'exchange': 'reporting', 'routing_key': 'reporting'}),
    ),
)

# Configure logging for Celery tasks
from celery.signals import task_prerun, task_postrun, task_failure
import logging

logger = logging.getLogger(__name__)


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, **kwargs):
    """Log task start.
    
    Args:
        sender: The Celery task
        task_id: Unique task ID
        task: Task object
    """
    logger.info(f"Task {task.name} [ID: {task_id}] started")


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, result=None, **kwargs):
    """Log task completion.
    
    Args:
        sender: The Celery task
        task_id: Unique task ID
        task: Task object
        result: Task result
    """
    logger.info(f"Task {task.name} [ID: {task_id}] completed successfully")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    """Log task failure.
    
    Args:
        sender: The Celery task
        task_id: Unique task ID
        exception: Exception raised
    """
    logger.error(f"Task {sender.name} [ID: {task_id}] failed: {exception}")


# NOTE: Import tasks from tasks module to register them
# This should be done in __init__.py or main application
# Example: from .tasks import *
