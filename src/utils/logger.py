"""
Structured logging utility for OSOrganicAI.

This module provides consistent, structured logging across the application.
Follows Single Responsibility Principle - only handles logging configuration.
"""

import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime
import structlog
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter with additional fields.

    Adds timestamp, level, and other metadata to every log entry.
    """

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any]
    ) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add timestamp in ISO format
        log_record["timestamp"] = datetime.utcnow().isoformat() + "Z"

        # Add log level
        log_record["level"] = record.levelname

        # Add logger name
        log_record["logger"] = record.name

        # Add source location (file, line, function)
        log_record["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }


def configure_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    service_name: str = "osorganicai"
) -> None:
    """
    Configure application-wide logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Output format ('json' or 'text')
        service_name: Name of the service for log identification

    Example:
        >>> configure_logging(log_level="DEBUG", log_format="json")
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)

    # Set formatter based on format type
    if log_format == "json":
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s"
        )
    else:
        # Text format for development
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(numeric_level)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer() if log_format == "json"
            else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str, **context) -> structlog.BoundLogger:
    """
    Get a structured logger instance with optional context.

    Args:
        name: Logger name (typically __name__ of the module)
        **context: Additional context to bind to all log entries

    Returns:
        structlog.BoundLogger: Configured logger instance

    Example:
        >>> logger = get_logger(__name__, agent_type="ProductOwner")
        >>> logger.info("Processing issue", issue_id=123)
    """
    logger = structlog.get_logger(name)
    if context:
        logger = logger.bind(**context)
    return logger


class LoggerMixin:
    """
    Mixin class to add logging capabilities to any class.

    Automatically creates a logger with the class name.
    Follows Open/Closed Principle - classes can extend without modification.

    Example:
        >>> class MyAgent(LoggerMixin):
        ...     def process(self):
        ...         self.logger.info("Processing started")
    """

    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger instance for this class."""
        if not hasattr(self, "_logger"):
            self._logger = get_logger(
                self.__class__.__name__,
                class_name=self.__class__.__name__
            )
        return self._logger


def log_function_call(func):
    """
    Decorator to log function entry and exit.

    Logs function name, arguments, execution time, and return value.

    Example:
        >>> @log_function_call
        ... def my_function(x, y):
        ...     return x + y
    """
    import functools
    import time

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)

        # Log function entry
        logger.debug(
            "Function called",
            function=func.__name__,
            args=args if args else None,
            kwargs=kwargs if kwargs else None
        )

        # Execute function and measure time
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time

            # Log successful completion
            logger.debug(
                "Function completed",
                function=func.__name__,
                elapsed_time_ms=round(elapsed_time * 1000, 2),
                result_type=type(result).__name__
            )
            return result

        except Exception as e:
            elapsed_time = time.time() - start_time

            # Log error
            logger.error(
                "Function failed",
                function=func.__name__,
                elapsed_time_ms=round(elapsed_time * 1000, 2),
                error_type=type(e).__name__,
                error_message=str(e),
                exc_info=True
            )
            raise

    return wrapper


class RequestLogger:
    """
    Context manager for logging request lifecycle.

    Automatically logs request start, end, and duration.
    Useful for API endpoints and long-running operations.

    Example:
        >>> with RequestLogger("github_api_call", issue_id=123):
        ...     # Your code here
        ...     pass
    """

    def __init__(self, operation: str, **context):
        """
        Initialize request logger.

        Args:
            operation: Name of the operation being logged
            **context: Additional context for the operation
        """
        self.operation = operation
        self.context = context
        self.logger = get_logger("RequestLogger")
        self.start_time = None

    def __enter__(self):
        """Log operation start."""
        self.start_time = datetime.utcnow()
        self.logger.info(
            "Operation started",
            operation=self.operation,
            **self.context
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Log operation completion or failure."""
        elapsed_time = (datetime.utcnow() - self.start_time).total_seconds()

        if exc_type is None:
            # Success
            self.logger.info(
                "Operation completed",
                operation=self.operation,
                elapsed_time_ms=round(elapsed_time * 1000, 2),
                **self.context
            )
        else:
            # Failure
            self.logger.error(
                "Operation failed",
                operation=self.operation,
                elapsed_time_ms=round(elapsed_time * 1000, 2),
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                **self.context,
                exc_info=True
            )

        # Don't suppress exceptions
        return False


# Convenience functions for common log patterns
def log_agent_action(
    agent_name: str,
    action: str,
    **details
) -> None:
    """
    Log an agent action with standardized format.

    Args:
        agent_name: Name of the agent performing the action
        action: Action being performed
        **details: Additional action details
    """
    logger = get_logger("AgentAction")
    logger.info(
        "Agent action",
        agent_name=agent_name,
        action=action,
        **details
    )


def log_api_call(
    service: str,
    endpoint: str,
    method: str = "GET",
    status_code: Optional[int] = None,
    **details
) -> None:
    """
    Log an external API call.

    Args:
        service: Name of the external service
        endpoint: API endpoint called
        method: HTTP method
        status_code: Response status code (if available)
        **details: Additional call details
    """
    logger = get_logger("APICall")
    logger.info(
        "API call",
        service=service,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        **details
    )


def log_database_operation(
    operation: str,
    table: str,
    **details
) -> None:
    """
    Log a database operation.

    Args:
        operation: Type of operation (insert, update, delete, select)
        table: Database table name
        **details: Additional operation details
    """
    logger = get_logger("DatabaseOperation")
    logger.info(
        "Database operation",
        operation=operation,
        table=table,
        **details
    )
