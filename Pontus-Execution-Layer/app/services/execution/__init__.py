"""
Execution Layer Services
"""
# Lazy imports to avoid circular dependencies
from app.services.execution.simulator import Simulator

__all__ = ["Simulator"]

# ExecutionService is imported lazily to avoid routing service dependencies during testing
def get_execution_service():
    """Lazy import of ExecutionService"""
    from app.services.execution.execution_service import ExecutionService
    return ExecutionService

