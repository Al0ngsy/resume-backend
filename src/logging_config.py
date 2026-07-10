import structlog
import logging
import sys

def setup_logging() -> None:
  """
    Configure structlog to output JSON to stdout.
    To be called ONCE at app startup to configure structlog.
  """
  # Set the stdlib root logger level so structlog's filter_by_level
  # actually lets INFO (and above) through. Without this, the default
  # WARNING level silently drops all our info() calls.
  logging.basicConfig(
      format="%(message)s",
      level=logging.INFO,
      stream=sys.stdout,
  )

  structlog.configure( 
    processors=[
      # chain of transformation top-down:
      structlog.stdlib.filter_by_level,                 # 1. Drop logs below configured level
      structlog.stdlib.add_logger_name,                 # 2. Add logger name
      structlog.stdlib.add_log_level,                   # 3. Add "level": "info"/"error"/etc.
      structlog.stdlib.PositionalArgumentsFormatter(),  # 4. Handle %s style formatting
      structlog.processors.TimeStamper(fmt="iso"),      # 5. Add "timestamp": "2026-..."
      structlog.processors.StackInfoRenderer(),         # 6. Add stack trace if exception
      structlog.processors.format_exc_info,             # 7. Format exception info
      structlog.processors.UnicodeDecoder(),            # 8. Decode bytes to strings
      structlog.dev.set_exc_info,                       # 9. Better exception formatting
      structlog.processors.JSONRenderer(),              # 10. Render as JSON string
    ],
    wrapper_class=structlog.stdlib.BoundLogger,       # Use stdlib-compatible logger
    context_class=dict,                               # Context is a plain dict
    logger_factory=structlog.stdlib.LoggerFactory(),  # Use stdlib logging under the hood
    cache_logger_on_first_use=True,                   # Create each logger once
  )

# for static context
# '->' pre-define return types of the function
def getLogger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
      Get a structlog logger. Pass __name__ to get a module-scoped logger.
    """
    return structlog.get_logger(name or __name__)

# for request-scoped context
def get_bound_logger(
    requestId: str,
    conversationId: str,
    clientId: str
) -> structlog.stdlib.BoundLogger:
    """
      Get a logger with request context pre-bound.
      Every log call from this logger automatically includes request_id,
      conversation_id, and client_ip — no need to pass them each time.
    """
    return structlog.get_logger().bind(
        # bind create a logger copy with following context permanently attached
        requestId=requestId,
        conversationId=conversationId,
        clientId=clientId
    )
