"""
Metrics collection for simulation monitoring
"""
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque


@dataclass
class ConnectorMetrics:
    """Metrics for a target connector"""
    connector_type: str
    total_attempts: int = 0
    successful_sends: int = 0
    failed_sends: int = 0
    connection_failures: int = 0
    total_bytes_sent: int = 0
    avg_response_time: float = 0.0
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    last_error: Optional[str] = None
    
    # Recent performance tracking (last 100 operations)
    recent_response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    recent_success_rate: float = 0.0
    
    def record_success(self, response_time: float, bytes_sent: int = 0):
        """Record a successful operation"""
        self.total_attempts += 1
        self.successful_sends += 1
        self.total_bytes_sent += bytes_sent
        self.last_success_time = datetime.utcnow()
        
        # Update response time metrics
        self.recent_response_times.append(response_time)
        self._update_avg_response_time()
        self._update_recent_success_rate()
    
    def record_failure(self, error: str, is_connection_error: bool = False):
        """Record a failed operation"""
        self.total_attempts += 1
        self.failed_sends += 1
        self.last_failure_time = datetime.utcnow()
        self.last_error = error
        
        if is_connection_error:
            self.connection_failures += 1
        
        self._update_recent_success_rate()
    
    def _update_avg_response_time(self):
        """Update average response time"""
        if self.recent_response_times:
            self.avg_response_time = sum(self.recent_response_times) / len(self.recent_response_times)
    
    def _update_recent_success_rate(self):
        """Update recent success rate based on last 100 operations"""
        if self.total_attempts > 0:
            recent_attempts = min(100, self.total_attempts)
            recent_successes = max(0, self.successful_sends - max(0, self.total_attempts - 100))
            self.recent_success_rate = recent_successes / recent_attempts
    
    def get_success_rate(self) -> float:
        """Get overall success rate"""
        if self.total_attempts == 0:
            return 0.0
        return self.successful_sends / self.total_attempts
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "connector_type": self.connector_type,
            "total_attempts": self.total_attempts,
            "successful_sends": self.successful_sends,
            "failed_sends": self.failed_sends,
            "connection_failures": self.connection_failures,
            "total_bytes_sent": self.total_bytes_sent,
            "success_rate": self.get_success_rate(),
            "recent_success_rate": self.recent_success_rate,
            "avg_response_time": self.avg_response_time,
            "last_success_time": self.last_success_time,
            "last_failure_time": self.last_failure_time,
            "last_error": self.last_error
        }


@dataclass
class DeviceMetrics:
    """Metrics for a device simulator"""
    device_id: str
    device_name: str
    messages_generated: int = 0
    messages_sent: int = 0
    payload_generation_failures: int = 0
    send_failures: int = 0
    total_retries: int = 0
    uptime_start: datetime = field(default_factory=datetime.utcnow)
    last_activity: Optional[datetime] = None
    
    def record_message_generated(self):
        """Record a message generation"""
        self.messages_generated += 1
        self.last_activity = datetime.utcnow()
    
    def record_message_sent(self):
        """Record a successful message send"""
        self.messages_sent += 1
        self.last_activity = datetime.utcnow()
    
    def record_payload_failure(self):
        """Record a payload generation failure"""
        self.payload_generation_failures += 1
        self.last_activity = datetime.utcnow()
    
    def record_send_failure(self):
        """Record a send failure"""
        self.send_failures += 1
        self.last_activity = datetime.utcnow()
    
    def record_retry(self):
        """Record a retry attempt"""
        self.total_retries += 1
    
    def get_uptime(self) -> timedelta:
        """Get device uptime"""
        return datetime.utcnow() - self.uptime_start
    
    def get_send_success_rate(self) -> float:
        """Get send success rate"""
        total_send_attempts = self.messages_sent + self.send_failures
        if total_send_attempts == 0:
            return 0.0
        return self.messages_sent / total_send_attempts
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "messages_generated": self.messages_generated,
            "messages_sent": self.messages_sent,
            "payload_generation_failures": self.payload_generation_failures,
            "send_failures": self.send_failures,
            "total_retries": self.total_retries,
            "send_success_rate": self.get_send_success_rate(),
            "uptime_seconds": self.get_uptime().total_seconds(),
            "last_activity": self.last_activity
        }


class MetricsCollector:
    """Central metrics collector for simulation monitoring"""
    
    def __init__(self):
        self.connector_metrics: Dict[str, ConnectorMetrics] = {}
        self.device_metrics: Dict[str, DeviceMetrics] = {}
        self.project_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.start_time = datetime.utcnow()
    
    def get_or_create_connector_metrics(self, connector_id: str, connector_type: str) -> ConnectorMetrics:
        """Get or create connector metrics"""
        if connector_id not in self.connector_metrics:
            self.connector_metrics[connector_id] = ConnectorMetrics(connector_type=connector_type)
        return self.connector_metrics[connector_id]
    
    def get_or_create_device_metrics(self, device_id: str, device_name: str) -> DeviceMetrics:
        """Get or create device metrics"""
        if device_id not in self.device_metrics:
            self.device_metrics[device_id] = DeviceMetrics(device_id=device_id, device_name=device_name)
        return self.device_metrics[device_id]
    
    def record_connector_success(self, connector_id: str, connector_type: str, response_time: float, bytes_sent: int = 0):
        """Record successful connector operation"""
        metrics = self.get_or_create_connector_metrics(connector_id, connector_type)
        metrics.record_success(response_time, bytes_sent)
    
    def record_connector_failure(self, connector_id: str, connector_type: str, error: str, is_connection_error: bool = False):
        """Record failed connector operation"""
        metrics = self.get_or_create_connector_metrics(connector_id, connector_type)
        metrics.record_failure(error, is_connection_error)
    
    def get_project_summary(self, project_id: str) -> Dict[str, Any]:
        """Get summary metrics for a project"""
        project_devices = [m for m in self.device_metrics.values() if m.device_id.startswith(project_id)]
        
        if not project_devices:
            return {
                "project_id": project_id,
                "total_devices": 0,
                "total_messages_sent": 0,
                "total_failures": 0,
                "avg_success_rate": 0.0
            }
        
        total_messages = sum(d.messages_sent for d in project_devices)
        total_failures = sum(d.send_failures + d.payload_generation_failures for d in project_devices)
        avg_success_rate = sum(d.get_send_success_rate() for d in project_devices) / len(project_devices)
        
        return {
            "project_id": project_id,
            "total_devices": len(project_devices),
            "total_messages_sent": total_messages,
            "total_failures": total_failures,
            "avg_success_rate": avg_success_rate,
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds()
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        return {
            "connectors": {k: v.to_dict() for k, v in self.connector_metrics.items()},
            "devices": {k: v.to_dict() for k, v in self.device_metrics.items()},
            "system": {
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "total_connectors": len(self.connector_metrics),
                "total_devices": len(self.device_metrics)
            }
        }
    
    def reset_metrics(self, project_id: Optional[str] = None):
        """Reset metrics for a project or all metrics"""
        if project_id:
            # Reset only metrics for specific project
            devices_to_remove = [k for k in self.device_metrics.keys() if k.startswith(project_id)]
            for device_id in devices_to_remove:
                del self.device_metrics[device_id]
        else:
            # Reset all metrics
            self.connector_metrics.clear()
            self.device_metrics.clear()
            self.project_metrics.clear()
            self.start_time = datetime.utcnow()


# Global metrics collector instance
metrics_collector = MetricsCollector()