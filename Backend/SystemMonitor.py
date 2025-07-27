# Advanced System Monitoring and Performance Analysis
# Provides comprehensive system resource monitoring and analytics

import psutil
import platform
import json
import datetime
import threading
import time
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import subprocess
import socket
import requests

@dataclass
class SystemInfo:
    os_name: str
    os_version: str
    architecture: str
    hostname: str
    processor: str
    cpu_cores: int
    cpu_threads: int
    total_memory: int
    available_memory: int
    disk_usage: Dict[str, Dict]
    network_interfaces: Dict[str, Dict]
    boot_time: str
    uptime: str

@dataclass
class PerformanceMetrics:
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: Dict[str, float]
    network_io: Dict[str, int]
    temperature: Optional[Dict[str, float]]
    battery: Optional[Dict[str, any]]
    processes_count: int
    top_processes: List[Dict]

class SystemMonitor:
    def __init__(self):
        self.data_dir = "Data/SystemMonitor"
        self.metrics_file = f"{self.data_dir}/metrics.json"
        self.alerts_file = f"{self.data_dir}/alerts.json"
        self.config_file = f"{self.data_dir}/config.json"
        
        # Create directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Monitoring data
        self.metrics_history = []
        self.alerts = []
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Alert thresholds
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "temperature": 80.0,
            "battery_low": 20.0
        }
        
        # Load existing data
        self._load_metrics()
        self._load_alerts()
    
    def get_system_info(self) -> SystemInfo:
        """Get comprehensive system information"""
        try:
            # Basic system info
            uname = platform.uname()
            
            # CPU information
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            # Memory information
            memory = psutil.virtual_memory()
            
            # Disk information
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": (usage.used / usage.total) * 100
                    }
                except PermissionError:
                    continue
            
            # Network interfaces
            network_interfaces = {}
            for interface, addresses in psutil.net_if_addrs().items():
                interface_info = {
                    "addresses": [],
                    "is_up": interface in psutil.net_if_stats() and psutil.net_if_stats()[interface].isup
                }
                
                for address in addresses:
                    interface_info["addresses"].append({
                        "family": str(address.family),
                        "address": address.address,
                        "netmask": getattr(address, 'netmask', None),
                        "broadcast": getattr(address, 'broadcast', None)
                    })
                
                network_interfaces[interface] = interface_info
            
            # Boot time and uptime
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.datetime.now() - boot_time
            
            return SystemInfo(
                os_name=uname.system,
                os_version=f"{uname.release} {uname.version}",
                architecture=uname.machine,
                hostname=uname.node,
                processor=uname.processor or platform.processor(),
                cpu_cores=cpu_count,
                cpu_threads=cpu_count_logical,
                total_memory=memory.total,
                available_memory=memory.available,
                disk_usage=disk_usage,
                network_interfaces=network_interfaces,
                boot_time=boot_time.isoformat(),
                uptime=str(uptime)
            )
            
        except Exception as e:
            print(f"❌ Error getting system info: {e}")
            return None
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk_usage_percent = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage_percent[partition.device] = (usage.used / usage.total) * 100
                except PermissionError:
                    continue
            
            # Network I/O
            network_io = psutil.net_io_counters()._asdict()
            
            # Temperature (if available)
            temperature = None
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    temperature = {}
                    for name, entries in temps.items():
                        for entry in entries:
                            temperature[f"{name}_{entry.label or 'unknown'}"] = entry.current
            except (AttributeError, OSError):
                pass
            
            # Battery (if available)
            battery = None
            try:
                battery_info = psutil.sensors_battery()
                if battery_info:
                    battery = {
                        "percent": battery_info.percent,
                        "power_plugged": battery_info.power_plugged,
                        "seconds_left": getattr(battery_info, 'secsleft', None)
                    }
            except (AttributeError, OSError):
                pass
            
            # Process information
            processes = list(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']))
            processes.sort(key=lambda x: x.info['cpu_percent'] or 0, reverse=True)
            
            top_processes = []
            for proc in processes[:10]:  # Top 10 processes
                try:
                    top_processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu_percent": proc.info['cpu_percent'] or 0,
                        "memory_percent": proc.info['memory_percent'] or 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return PerformanceMetrics(
                timestamp=datetime.datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage_percent=disk_usage_percent,
                network_io=network_io,
                temperature=temperature,
                battery=battery,
                processes_count=len(processes),
                top_processes=top_processes
            )
            
        except Exception as e:
            print(f"❌ Error getting performance metrics: {e}")
            return None
    
    def start_monitoring(self, interval: int = 60):
        """Start continuous system monitoring"""
        if self.is_monitoring:
            print("⚠️ Monitoring is already running")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(interval,), 
            daemon=True
        )
        self.monitor_thread.start()
        
        print(f"📊 System monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop continuous system monitoring"""
        if not self.is_monitoring:
            print("⚠️ Monitoring is not running")
            return
        
        self.is_monitoring = False
        print("🛑 System monitoring stopped")
    
    def get_metrics_history(self, hours: int = 24) -> List[PerformanceMetrics]:
        """Get metrics history for the specified number of hours"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
        
        filtered_metrics = []
        for metric in self.metrics_history:
            metric_time = datetime.datetime.fromisoformat(metric["timestamp"])
            if metric_time >= cutoff_time:
                filtered_metrics.append(metric)
        
        return filtered_metrics
    
    def get_performance_summary(self, hours: int = 24) -> Dict:
        """Get performance summary for the specified period"""
        metrics = self.get_metrics_history(hours)
        
        if not metrics:
            return {}
        
        cpu_values = [m["cpu_percent"] for m in metrics]
        memory_values = [m["memory_percent"] for m in metrics]
        
        return {
            "period_hours": hours,
            "data_points": len(metrics),
            "cpu_usage": {
                "average": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values)
            },
            "memory_usage": {
                "average": sum(memory_values) / len(memory_values),
                "max": max(memory_values),
                "min": min(memory_values)
            },
            "alerts_count": len([a for a in self.alerts if self._is_within_period(a["timestamp"], hours)])
        }
    
    def get_running_processes(self, sort_by: str = "cpu") -> List[Dict]:
        """Get detailed information about running processes"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                           'memory_info', 'create_time', 'status', 'username']):
                try:
                    process_info = proc.info.copy()
                    process_info['memory_mb'] = proc.info['memory_info'].rss / 1024 / 1024
                    process_info['create_time'] = datetime.datetime.fromtimestamp(
                        proc.info['create_time']
                    ).isoformat()
                    processes.append(process_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort processes
            if sort_by == "cpu":
                processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            elif sort_by == "memory":
                processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
            elif sort_by == "name":
                processes.sort(key=lambda x: x['name'].lower())
            
            return processes
            
        except Exception as e:
            print(f"❌ Error getting processes: {e}")
            return []
    
    def kill_process(self, pid: int, force: bool = False) -> bool:
        """Kill a process by PID"""
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            if force:
                process.kill()
            else:
                process.terminate()
            
            print(f"🔄 Process killed: {process_name} (PID: {pid})")
            return True
            
        except psutil.NoSuchProcess:
            print(f"❌ Process not found: PID {pid}")
            return False
        except psutil.AccessDenied:
            print(f"❌ Access denied: Cannot kill PID {pid}")
            return False
        except Exception as e:
            print(f"❌ Error killing process: {e}")
            return False
    
    def get_network_connections(self) -> List[Dict]:
        """Get active network connections"""
        try:
            connections = []
            
            for conn in psutil.net_connections(kind='inet'):
                connection_info = {
                    "fd": conn.fd,
                    "family": conn.family.name if conn.family else "unknown",
                    "type": conn.type.name if conn.type else "unknown",
                    "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "",
                    "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "",
                    "status": conn.status,
                    "pid": conn.pid
                }
                
                # Try to get process name
                if conn.pid:
                    try:
                        process = psutil.Process(conn.pid)
                        connection_info["process_name"] = process.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        connection_info["process_name"] = "unknown"
                
                connections.append(connection_info)
            
            return connections
            
        except Exception as e:
            print(f"❌ Error getting network connections: {e}")
            return []
    
    def get_disk_io_stats(self) -> Dict:
        """Get disk I/O statistics"""
        try:
            disk_io = psutil.disk_io_counters(perdisk=True)
            
            stats = {}
            for device, counters in disk_io.items():
                stats[device] = {
                    "read_count": counters.read_count,
                    "write_count": counters.write_count,
                    "read_bytes": counters.read_bytes,
                    "write_bytes": counters.write_bytes,
                    "read_time": counters.read_time,
                    "write_time": counters.write_time
                }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting disk I/O stats: {e}")
            return {}
    
    def get_system_services(self) -> List[Dict]:
        """Get system services status (Windows only)"""
        if platform.system() != "Windows":
            return []
        
        try:
            services = []
            
            # Use Windows SC command to get services
            result = subprocess.run(
                ["sc", "query"], 
                capture_output=True, 
                text=True, 
                shell=True
            )
            
            if result.returncode == 0:
                # Parse the output (simplified)
                lines = result.stdout.split('\n')
                current_service = {}
                
                for line in lines:
                    line = line.strip()
                    if line.startswith("SERVICE_NAME:"):
                        if current_service:
                            services.append(current_service)
                        current_service = {"name": line.split(":", 1)[1].strip()}
                    elif line.startswith("DISPLAY_NAME:"):
                        current_service["display_name"] = line.split(":", 1)[1].strip()
                    elif line.startswith("STATE"):
                        current_service["state"] = line.split()[3] if len(line.split()) > 3 else "unknown"
                
                if current_service:
                    services.append(current_service)
            
            return services
            
        except Exception as e:
            print(f"❌ Error getting system services: {e}")
            return []
    
    def check_internet_connectivity(self) -> Dict:
        """Check internet connectivity"""
        connectivity = {
            "dns_resolution": False,
            "http_connectivity": False,
            "ping_google": False,
            "ping_cloudflare": False,
            "response_times": {}
        }
        
        # Test DNS resolution
        try:
            socket.gethostbyname("google.com")
            connectivity["dns_resolution"] = True
        except socket.gaierror:
            pass
        
        # Test HTTP connectivity
        try:
            start_time = time.time()
            response = requests.get("https://httpbin.org/get", timeout=5)
            if response.status_code == 200:
                connectivity["http_connectivity"] = True
                connectivity["response_times"]["http"] = (time.time() - start_time) * 1000
        except requests.RequestException:
            pass
        
        # Test ping to Google DNS
        try:
            if platform.system() == "Windows":
                result = subprocess.run(["ping", "-n", "1", "8.8.8.8"], 
                                      capture_output=True, text=True, timeout=5)
            else:
                result = subprocess.run(["ping", "-c", "1", "8.8.8.8"], 
                                      capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                connectivity["ping_google"] = True
        except subprocess.TimeoutExpired:
            pass
        
        # Test ping to Cloudflare DNS
        try:
            if platform.system() == "Windows":
                result = subprocess.run(["ping", "-n", "1", "1.1.1.1"], 
                                      capture_output=True, text=True, timeout=5)
            else:
                result = subprocess.run(["ping", "-c", "1", "1.1.1.1"], 
                                      capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                connectivity["ping_cloudflare"] = True
        except subprocess.TimeoutExpired:
            pass
        
        return connectivity
    
    def _monitoring_loop(self, interval: int):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self.get_current_metrics()
                if metrics:
                    # Add to history
                    self.metrics_history.append(asdict(metrics))
                    
                    # Keep only last 24 hours of data
                    cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=24)
                    self.metrics_history = [
                        m for m in self.metrics_history 
                        if datetime.datetime.fromisoformat(m["timestamp"]) >= cutoff_time
                    ]
                    
                    # Check for alerts
                    self._check_alerts(metrics)
                    
                    # Save metrics
                    self._save_metrics()
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def _check_alerts(self, metrics: PerformanceMetrics):
        """Check for performance alerts"""
        alerts = []
        
        # CPU usage alert
        if metrics.cpu_percent > self.alert_thresholds["cpu_usage"]:
            alerts.append({
                "type": "cpu_high",
                "message": f"High CPU usage: {metrics.cpu_percent:.1f}%",
                "value": metrics.cpu_percent,
                "threshold": self.alert_thresholds["cpu_usage"]
            })
        
        # Memory usage alert
        if metrics.memory_percent > self.alert_thresholds["memory_usage"]:
            alerts.append({
                "type": "memory_high",
                "message": f"High memory usage: {metrics.memory_percent:.1f}%",
                "value": metrics.memory_percent,
                "threshold": self.alert_thresholds["memory_usage"]
            })
        
        # Disk usage alerts
        for device, usage_percent in metrics.disk_usage_percent.items():
            if usage_percent > self.alert_thresholds["disk_usage"]:
                alerts.append({
                    "type": "disk_high",
                    "message": f"High disk usage on {device}: {usage_percent:.1f}%",
                    "value": usage_percent,
                    "threshold": self.alert_thresholds["disk_usage"]
                })
        
        # Temperature alerts
        if metrics.temperature:
            for sensor, temp in metrics.temperature.items():
                if temp > self.alert_thresholds["temperature"]:
                    alerts.append({
                        "type": "temperature_high",
                        "message": f"High temperature on {sensor}: {temp:.1f}°C",
                        "value": temp,
                        "threshold": self.alert_thresholds["temperature"]
                    })
        
        # Battery alert
        if metrics.battery and not metrics.battery["power_plugged"]:
            if metrics.battery["percent"] < self.alert_thresholds["battery_low"]:
                alerts.append({
                    "type": "battery_low",
                    "message": f"Low battery: {metrics.battery['percent']:.1f}%",
                    "value": metrics.battery["percent"],
                    "threshold": self.alert_thresholds["battery_low"]
                })
        
        # Add alerts to history
        for alert in alerts:
            alert["timestamp"] = datetime.datetime.now().isoformat()
            self.alerts.append(alert)
            print(f"🚨 ALERT: {alert['message']}")
        
        if alerts:
            self._save_alerts()
    
    def _is_within_period(self, timestamp: str, hours: int) -> bool:
        """Check if timestamp is within the specified period"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
        item_time = datetime.datetime.fromisoformat(timestamp)
        return item_time >= cutoff_time
    
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)
    
    def _load_metrics(self):
        """Load metrics history from file"""
        if os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                self.metrics_history = json.load(f)
    
    def _save_metrics(self):
        """Save metrics history to file"""
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics_history, f, indent=4)
    
    def _load_alerts(self):
        """Load alerts from file"""
        if os.path.exists(self.alerts_file):
            with open(self.alerts_file, 'r', encoding='utf-8') as f:
                self.alerts = json.load(f)
    
    def _save_alerts(self):
        """Save alerts to file"""
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump(self.alerts, f, indent=4)

# Global system monitor instance
system_monitor = SystemMonitor()

# Voice command functions for system monitoring
def get_system_status_voice(command: str):
    """Get system status from voice command"""
    metrics = system_monitor.get_current_metrics()
    
    if not metrics:
        return "Unable to retrieve system status"
    
    return (f"System Status:\n"
            f"CPU Usage: {metrics.cpu_percent:.1f}%\n"
            f"Memory Usage: {metrics.memory_percent:.1f}%\n"
            f"Running Processes: {metrics.processes_count}\n"
            f"Battery: {metrics.battery['percent']:.1f}%" if metrics.battery else "")

def get_top_processes_voice(command: str):
    """Get top processes from voice command"""
    processes = system_monitor.get_running_processes(sort_by="cpu")
    
    if not processes:
        return "Unable to retrieve process information"
    
    result = "Top CPU-using processes:\n"
    for i, proc in enumerate(processes[:5], 1):
        result += f"{i}. {proc['name']} - {proc['cpu_percent']:.1f}% CPU\n"
    
    return result

def get_network_status_voice(command: str):
    """Get network status from voice command"""
    connectivity = system_monitor.check_internet_connectivity()
    
    status = "🌐 " if connectivity["http_connectivity"] else "❌ "
    status += "Internet: Connected" if connectivity["http_connectivity"] else "Internet: Disconnected"
    
    if connectivity["dns_resolution"]:
        status += "\n✅ DNS resolution working"
    else:
        status += "\n❌ DNS resolution failed"
    
    return status