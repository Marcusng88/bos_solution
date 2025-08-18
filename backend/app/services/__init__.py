"""
Services package for business logic
"""

from .user.user_service import UserService
from .competitor.competitor_service import CompetitorService

# Try to import monitoring services, but don't fail if dependencies are missing
try:
    from .monitoring import MonitoringService, AgentMonitoringService
    monitoring_available = True
except ImportError as e:
    print(f"Warning: Monitoring services not available due to missing dependencies: {e}")
    MonitoringService = None
    AgentMonitoringService = None
    monitoring_available = False

__all__ = [
    "UserService",
    "CompetitorService"
]

if monitoring_available:
    __all__.extend(["MonitoringService", "AgentMonitoringService"])
