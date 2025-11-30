"""
Safe mode tools for AI agents.
Mock implementations of system operations for safety.
"""
from typing import Dict, Any, List
import json
from datetime import datetime


class SafeModeTools:
    """Safe mode tools for system operations."""
    
    @staticmethod
    def check_system_status(service_name: str) -> Dict[str, Any]:
        """
        Mock check of system service status.
        In production, this would check actual system services.
        """
        # Mock response
        mock_statuses = {
            "database": {"status": "running", "uptime": "99.9%", "connections": 45},
            "api_server": {"status": "running", "uptime": "99.8%", "requests": 15234},
            "cache": {"status": "running", "uptime": "99.7%", "hit_rate": "85%"},
            "email": {"status": "degraded", "uptime": "98.5%", "queue": 23}
        }
        
        return {
            "service": service_name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": mock_statuses.get(service_name.lower(), {"status": "unknown"})
        }
    
    @staticmethod
    def check_logs(service_name: str, lines: int = 10) -> List[str]:
        """
        Mock check of service logs.
        In production, this would read actual log files.
        """
        # Mock logs
        mock_logs = [
            f"[INFO] {service_name} service started successfully",
            f"[INFO] Processing requests normally",
            f"[WARN] High memory usage detected: 78%",
            f"[INFO] Cache cleared successfully",
            f"[ERROR] Connection timeout to external service",
            f"[INFO] Retry successful",
            f"[INFO] Request processed in 245ms",
            f"[WARN] Slow query detected: 3.2s",
            f"[INFO] Health check passed",
            f"[INFO] {service_name} status: operational"
        ]
        
        return mock_logs[:lines]
    
    @staticmethod
    def restart_service(service_name: str) -> Dict[str, Any]:
        """
        Mock service restart.
        In production, requires proper authorization and would actually restart services.
        """
        return {
            "action": "restart",
            "service": service_name,
            "status": "simulated",
            "message": f"[SAFE MODE] Would restart {service_name} service",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "This is a mock operation. Actual restart requires admin privileges."
        }
    
    @staticmethod
    def check_disk_space() -> Dict[str, Any]:
        """
        Mock disk space check.
        In production, this would check actual disk usage.
        """
        return {
            "total_gb": 500,
            "used_gb": 342,
            "available_gb": 158,
            "usage_percent": 68.4,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def check_network_connectivity(target: str = "8.8.8.8") -> Dict[str, Any]:
        """
        Mock network connectivity check.
        In production, this would perform actual ping/connection tests.
        """
        return {
            "target": target,
            "reachable": True,
            "latency_ms": 23,
            "packet_loss": 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def get_available_tools() -> List[Dict[str, str]]:
        """Get list of available safe mode tools."""
        return [
            {
                "name": "check_system_status",
                "description": "Check status of a system service",
                "parameters": "service_name: str"
            },
            {
                "name": "check_logs",
                "description": "Check recent logs for a service",
                "parameters": "service_name: str, lines: int"
            },
            {
                "name": "restart_service",
                "description": "Restart a service (SAFE MODE - simulation only)",
                "parameters": "service_name: str"
            },
            {
                "name": "check_disk_space",
                "description": "Check disk space usage",
                "parameters": "None"
            },
            {
                "name": "check_network_connectivity",
                "description": "Check network connectivity to a target",
                "parameters": "target: str"
            }
        ]


# Create global instance
safe_tools = SafeModeTools()
