"""
IoT Control Dashboard — v1.0
OpenCode Bot Feature

Telegram Mini App + bot commands to control IoT devices:
- ESP32/Arduino relay control
- Sensor monitoring (temperature, humidity, light, motion)
- GPIO pin management
- Multi-device management
- Alert notifications
- Data logging & history
- Scheduled automation
- Dashboard via Mini App
"""

import json
import os
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IOT_DATA_FILE = os.path.join(BASE_DIR, "iot_data.json")
IOT_DEVICES_FILE = os.path.join(BASE_DIR, "iot_devices.json")
IOT_LOGS_FILE = os.path.join(BASE_DIR, "iot_logs.json")


class DeviceType(Enum):
    ESP32 = "esp32"
    ARDUINO = "arduino"
    RASPBERRY_PI = "raspberry_pi"
    CUSTOM = "custom"


class PinMode(Enum):
    INPUT = "input"
    OUTPUT = "output"
    INPUT_PULLUP = "input_pullup"
    ANALOG = "analog"


class PinState(Enum):
    HIGH = 1
    LOW = 0


class SensorType(Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    LIGHT = "light"
    MOTION = "motion"
    PRESSURE = "pressure"
    GAS = "gas"
    SOIL_MOISTURE = "soil_moisture"
    ULTRASONIC = "ultrasonic"
    CAMERA = "camera"
    CUSTOM = "custom"


@dataclass
class PinConfig:
    pin: int
    mode: PinMode
    state: int = 0
    label: str = ""
    last_changed: float = 0.0
    history: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "pin": self.pin,
            "mode": self.mode.value,
            "state": self.state,
            "label": self.label,
            "last_changed": self.last_changed,
            "history": self.history[-20:]
        }


@dataclass
class SensorReading:
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: float
    device_id: str = ""

    def to_dict(self) -> Dict:
        return {
            "sensor_type": self.sensor_type.value,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp,
            "device_id": self.device_id
        }


@dataclass
class AlertRule:
    sensor_type: str
    condition: str  # "above", "below", "equals"
    threshold: float
    message: str
    enabled: bool = True
    last_triggered: float = 0.0

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ScheduleTask:
    name: str
    action: str
    params: Dict
    cron: str  # "HH:MM" or "everyNs"
    enabled: bool = True
    last_run: float = 0.0

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class IoTDevice:
    device_id: str
    name: str
    device_type: DeviceType
    ip_address: str = ""
    api_key: str = ""
    pins: Dict[int, PinConfig] = field(default_factory=dict)
    sensors: List[str] = field(default_factory=list)
    alerts: List[AlertRule] = field(default_factory=list)
    schedules: List[ScheduleTask] = field(default_factory=list)
    readings: List[SensorReading] = field(default_factory=list)
    status: str = "offline"
    last_seen: float = 0.0
    created_at: float = 0.0
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "device_type": self.device_type.value,
            "ip_address": self.ip_address,
            "api_key": self.api_key,
            "pins": {str(k): v.to_dict() for k, v in self.pins.items()},
            "sensors": self.sensors,
            "alerts": [a.to_dict() for a in self.alerts],
            "schedules": [s.to_dict() for s in self.schedules],
            "readings": [r.to_dict() for r in self.readings[-50:]],
            "status": self.status,
            "last_seen": self.last_seen,
            "created_at": self.created_at,
            "tags": self.tags
        }


class IoTManager:
    def __init__(self):
        self.devices: Dict[str, IoTDevice] = {}
        self.logs: List[Dict] = []
        self._load_data()

    def _load_data(self):
        for path, attr, default in [
            (IOT_DEVICES_FILE, "devices", {}),
            (IOT_LOGS_FILE, "logs", [])
        ]:
            try:
                if os.path.exists(path):
                    with open(path, encoding="utf-8") as f:
                        data = json.load(f)
                    setattr(self, attr, data if isinstance(data, type(default)) else default)
            except Exception:
                pass

        if isinstance(self.devices, dict):
            restored = {}
            for did, ddata in self.devices.items():
                try:
                    device = IoTDevice(
                        device_id=ddata.get("device_id", did),
                        name=ddata.get("name", did),
                        device_type=DeviceType(ddata.get("device_type", "custom")),
                        ip_address=ddata.get("ip_address", ""),
                        api_key=ddata.get("api_key", ""),
                        status=ddata.get("status", "offline"),
                        last_seen=ddata.get("last_seen", 0),
                        created_at=ddata.get("created_at", 0),
                        tags=ddata.get("tags", [])
                    )
                    for pin_str, pdata in ddata.get("pins", {}).items():
                        pin_num = int(pin_str)
                        device.pins[pin_num] = PinConfig(
                            pin=pin_num,
                            mode=PinMode(pdata.get("mode", "output")),
                            state=pdata.get("state", 0),
                            label=pdata.get("label", ""),
                            last_changed=pdata.get("last_changed", 0),
                            history=pdata.get("history", [])
                        )
                    for adata in ddata.get("alerts", []):
                        device.alerts.append(AlertRule(**adata))
                    for sdata in ddata.get("schedules", []):
                        device.schedules.append(ScheduleTask(**sdata))
                    for rdata in ddata.get("readings", []):
                        device.readings.append(SensorReading(
                            sensor_type=SensorType(rdata.get("sensor_type", "custom")),
                            value=rdata.get("value", 0),
                            unit=rdata.get("unit", ""),
                            timestamp=rdata.get("timestamp", 0),
                            device_id=rdata.get("device_id", "")
                        ))
                    restored[did] = device
                except Exception as e:
                    logger.warning(f"Failed to restore device {did}: {e}")
            self.devices = restored

    def _save_data(self):
        try:
            with open(IOT_DEVICES_FILE, "w", encoding="utf-8") as f:
                json.dump({did: d.to_dict() for did, d in self.devices.items()}, f, indent=2)
            with open(IOT_LOGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.logs[-500:], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save IoT data: {e}")

    def _log(self, action: str, device_id: str, details: str = ""):
        entry = {
            "time": time.time(),
            "action": action,
            "device_id": device_id,
            "details": details
        }
        self.logs.append(entry)
        if len(self.logs) > 500:
            self.logs = self.logs[-500:]

    def add_device(self, name: str, device_type: str, ip: str = "",
                   api_key: str = "", tags: List[str] = None) -> IoTDevice:
        device_id = f"dev_{int(time.time()*1000) % 100000}"
        device = IoTDevice(
            device_id=device_id,
            name=name,
            device_type=DeviceType(device_type),
            ip_address=ip,
            api_key=api_key,
            created_at=time.time(),
            tags=tags or []
        )
        self.devices[device_id] = device
        self._log("add_device", device_id, name)
        self._save_data()
        return device

    def remove_device(self, device_id: str) -> bool:
        if device_id in self.devices:
            name = self.devices[device_id].name
            del self.devices[device_id]
            self._log("remove_device", device_id, name)
            self._save_data()
            return True
        return False

    def get_device(self, device_id: str) -> Optional[IoTDevice]:
        return self.devices.get(device_id)

    def list_devices(self) -> List[IoTDevice]:
        return list(self.devices.values())

    def set_pin(self, device_id: str, pin: int, state: int,
                label: str = "") -> bool:
        device = self.devices.get(device_id)
        if not device:
            return False
        if pin not in device.pins:
            device.pins[pin] = PinConfig(
                pin=pin, mode=PinMode.OUTPUT, label=label
            )
        device.pins[pin].state = state
        device.pins[pin].last_changed = time.time()
        device.pins[pin].history.append({
            "state": state,
            "time": time.time()
        })
        if len(device.pins[pin].history) > 20:
            device.pins[pin].history = device.pins[pin].history[-20:]
        device.last_seen = time.time()
        device.status = "online"
        self._log("set_pin", device_id,
                  f"Pin {pin} -> {'HIGH' if state else 'LOW'}")
        self._save_data()
        return True

    def add_sensor_reading(self, device_id: str, sensor_type: str,
                           value: float, unit: str = "") -> bool:
        device = self.devices.get(device_id)
        if not device:
            return False
        reading = SensorReading(
            sensor_type=SensorType(sensor_type),
            value=value,
            unit=unit,
            timestamp=time.time(),
            device_id=device_id
        )
        device.readings.append(reading)
        if len(device.readings) > 100:
            device.readings = device.readings[-100:]
        device.last_seen = time.time()
        device.status = "online"
        self._check_alerts(device, reading)
        self._save_data()
        return True

    def _check_alerts(self, device: IoTDevice, reading: SensorReading):
        for alert in device.alerts:
            if not alert.enabled:
                continue
            if alert.sensor_type != reading.sensor_type.value:
                continue
            triggered = False
            if alert.condition == "above" and reading.value > alert.threshold:
                triggered = True
            elif alert.condition == "below" and reading.value < alert.threshold:
                triggered = True
            elif alert.condition == "equals" and reading.value == alert.threshold:
                triggered = True
            if triggered:
                alert.last_triggered = time.time()
                self._log("alert_triggered", device.device_id,
                          f"{alert.message} ({reading.value}{reading.unit})")

    def add_alert(self, device_id: str, sensor_type: str, condition: str,
                  threshold: float, message: str) -> bool:
        device = self.devices.get(device_id)
        if not device:
            return False
        device.alerts.append(AlertRule(
            sensor_type=sensor_type,
            condition=condition,
            threshold=threshold,
            message=message
        ))
        self._log("add_alert", device_id,
                  f"{sensor_type} {condition} {threshold}: {message}")
        self._save_data()
        return True

    def add_schedule(self, device_id: str, name: str, action: str,
                     params: Dict, cron: str) -> bool:
        device = self.devices.get(device_id)
        if not device:
            return False
        device.schedules.append(ScheduleTask(
            name=name, action=action, params=params, cron=cron
        ))
        self._log("add_schedule", device_id,
                  f"{name}: {action} at {cron}")
        self._save_data()
        return True

    def get_sensor_history(self, device_id: str, sensor_type: str,
                           limit: int = 20) -> List[SensorReading]:
        device = self.devices.get(device_id)
        if not device:
            return []
        filtered = [r for r in device.readings
                    if r.sensor_type.value == sensor_type]
        return filtered[-limit:]

    def get_device_status(self, device_id: str) -> Dict:
        device = self.devices.get(device_id)
        if not device:
            return {"error": "Device not found"}
        return {
            "device_id": device.device_id,
            "name": device.name,
            "type": device.device_type.value,
            "status": device.status,
            "ip": device.ip_address,
            "pins": {str(k): {"state": v.state, "label": v.label}
                     for k, v in device.pins.items()},
            "sensors": device.sensors,
            "last_seen": device.last_seen,
            "uptime": time.time() - device.last_seen if device.last_seen else 0,
            "alerts": len([a for a in device.alerts if a.enabled]),
            "schedules": len([s for s in device.schedules if s.enabled]),
            "total_readings": len(device.readings)
        }

    def get_all_status(self) -> List[Dict]:
        return [self.get_device_status(did) for did in self.devices]

    def get_logs(self, device_id: str = None, limit: int = 20) -> List[Dict]:
        if device_id:
            filtered = [l for l in self.logs if l["device_id"] == device_id]
        else:
            filtered = self.logs
        return filtered[-limit:]

    def simulate_reading(self, device_id: str, sensor_type: str) -> float:
        import random
        ranges = {
            "temperature": (18.0, 35.0, "°C"),
            "humidity": (20.0, 90.0, "%"),
            "light": (0.0, 1000.0, "lux"),
            "motion": (0.0, 1.0, ""),
            "pressure": (980.0, 1050.0, "hPa"),
            "soil_moisture": (0.0, 100.0, "%"),
        }
        if sensor_type in ranges:
            lo, hi, unit = ranges[sensor_type]
            value = round(random.uniform(lo, hi), 1)
            self.add_sensor_reading(device_id, sensor_type, value, unit)
            return value
        return 0.0


_iot_manager = None

def get_iot_manager() -> IoTManager:
    global _iot_manager
    if _iot_manager is None:
        _iot_manager = IoTManager()
    return _iot_manager


def build_iot_commands() -> str:
    return """
📡 IoT Control Commands:
/iot add <name> <type> <ip> — Add device (esp32/arduino/rpi)
/iot list — List all devices
/iot status [device_id] — Device status
/iot pin <device> <pin> <0/1> — Set GPIO pin
/iot sensor <device> <type> — Add sensor reading
/iot history <device> <sensor> — Sensor history
/iot alert <device> <sensor> <above/below> <value> <msg> — Set alert
/iot schedule <device> <name> <cron> <action> — Add schedule
/iot logs [device_id] — View logs
/iot simulate <device> <sensor> — Simulate reading
/iot dashboard — Open Mini App dashboard
/iot help — Show this help
"""


def handle_iot_command(update, context) -> str:
    if not context.args:
        return build_iot_commands()

    subcmd = context.args[0].lower()
    mgr = get_iot_manager()

    if subcmd == "add":
        if len(context.args) < 3:
            return "Usage: /iot add <name> <type> [ip]"
        name = context.args[1]
        dtype = context.args[2].lower()
        ip = context.args[3] if len(context.args) > 3 else ""
        device = mgr.add_device(name, dtype, ip)
        return (f"✅ Device added: {device.name}\n"
                f"ID: `{device.device_id}`\n"
                f"Type: {device.device_type.value}")

    elif subcmd == "list":
        devices = mgr.list_devices()
        if not devices:
            return "No devices registered. Use /iot add to add one."
        lines = ["📡 **Devices:**\n"]
        for d in devices:
            status_icon = "🟢" if d.status == "online" else "🔴"
            lines.append(
                f"{status_icon} `{d.device_id}` — {d.name} "
                f"({d.device_type.value})"
            )
        return "\n".join(lines)

    elif subcmd == "status":
        if len(context.args) < 2:
            statuses = mgr.get_all_status()
            if not statuses:
                return "No devices. Use /iot add first."
            lines = ["📊 **Device Status:**\n"]
            for s in statuses:
                icon = "🟢" if s["status"] == "online" else "🔴"
                lines.append(
                    f"{icon} **{s['name']}** (`{s['device_id']}`)\n"
                    f"   Type: {s['type']} | Pins: {len(s['pins'])} | "
                    f"Alerts: {s['alerts']}"
                )
            return "\n".join(lines)
        device_id = context.args[1]
        status = mgr.get_device_status(device_id)
        if "error" in status:
            return f"❌ {status['error']}"
        icon = "🟢" if status["status"] == "online" else "🔴"
        return (
            f"{icon} **{status['name']}** (`{status['device_id']}`)\n\n"
            f"Type: {status['type']}\n"
            f"IP: {status['ip'] or 'N/A'}\n"
            f"Status: {status['status']}\n"
            f"Pins: {len(status['pins'])}\n"
            f"Active alerts: {status['alerts']}\n"
            f"Active schedules: {status['schedules']}\n"
            f"Total readings: {status['total_readings']}"
        )

    elif subcmd == "pin":
        if len(context.args) < 4:
            return "Usage: /iot pin <device_id> <pin> <0/1>"
        device_id = context.args[1]
        try:
            pin = int(context.args[2])
            state = int(context.args[3])
        except ValueError:
            return "Pin and state must be numbers."
        if state not in (0, 1):
            return "State must be 0 (LOW) or 1 (HIGH)."
        ok = mgr.set_pin(device_id, pin, state)
        if ok:
            return f"✅ Pin {pin} set to {'HIGH ⚡' if state else 'LOW ⚫'}"
        return "❌ Device not found."

    elif subcmd == "sensor":
        if len(context.args) < 3:
            return "Usage: /iot sensor <device_id> <type> [value]"
        device_id = context.args[1]
        stype = context.args[2].lower()
        if len(context.args) > 3:
            try:
                value = float(context.args[3])
            except ValueError:
                return "Value must be a number."
            unit = context.args[4] if len(context.args) > 4 else ""
            mgr.add_sensor_reading(device_id, stype, value, unit)
            return f"✅ Reading added: {stype} = {value}{unit}"
        value = mgr.simulate_reading(device_id, stype)
        return f"✅ Simulated {stype}: {value}"

    elif subcmd == "history":
        if len(context.args) < 3:
            return "Usage: /iot history <device_id> <sensor_type>"
        device_id = context.args[1]
        stype = context.args[2].lower()
        readings = mgr.get_sensor_history(device_id, stype)
        if not readings:
            return f"No {stype} readings for this device."
        lines = [f"📈 **{stype.title()} History:**\n"]
        for r in readings[-10:]:
            ts = datetime.fromtimestamp(r.timestamp).strftime("%H:%M:%S")
            lines.append(f"`{ts}` — {r.value}{r.unit}")
        return "\n".join(lines)

    elif subcmd == "alert":
        if len(context.args) < 6:
            return "Usage: /iot alert <device> <sensor> <above/below> <value> <message>"
        device_id = context.args[1]
        stype = context.args[2].lower()
        cond = context.args[3].lower()
        try:
            threshold = float(context.args[4])
        except ValueError:
            return "Threshold must be a number."
        msg = " ".join(context.args[5:])
        ok = mgr.add_alert(device_id, stype, cond, threshold, msg)
        return f"✅ Alert set: {stype} {cond} {threshold} → {msg}" if ok else "❌ Device not found."

    elif subcmd == "schedule":
        if len(context.args) < 5:
            return "Usage: /iot schedule <device> <name> <cron> <action>"
        device_id = context.args[1]
        name = context.args[2]
        cron = context.args[3]
        action = context.args[4]
        params = {}
        if len(context.args) > 5:
            params = {"args": context.args[5:]}
        ok = mgr.add_schedule(device_id, name, action, params, cron)
        return f"✅ Schedule added: {name} at {cron}" if ok else "❌ Device not found."

    elif subcmd == "logs":
        device_id = context.args[1] if len(context.args) > 1 else None
        logs = mgr.get_logs(device_id)
        if not logs:
            return "No logs yet."
        lines = ["📋 **Recent Activity:**\n"]
        for log in logs[-10:]:
            ts = datetime.fromtimestamp(log["time"]).strftime("%H:%M:%S")
            lines.append(f"`{ts}` {log['action']}: {log['details']}")
        return "\n".join(lines)

    elif subcmd == "simulate":
        if len(context.args) < 3:
            return "Usage: /iot simulate <device_id> <sensor_type>"
        device_id = context.args[1]
        stype = context.args[2].lower()
        value = mgr.simulate_reading(device_id, stype)
        return f"✅ Simulated {stype}: {value}"

    elif subcmd == "dashboard":
        return "📊 Mini App dashboard coming soon! Use /iot status for now."

    elif subcmd == "help":
        return build_iot_commands()

    return build_iot_commands()


def build_iot_dashboard_html(devices: List[Dict]) -> str:
    device_cards = ""
    for d in devices:
        status_color = "#00ff41" if d["status"] == "online" else "#ff0040"
        device_cards += f"""
        <div class="device-card">
            <h3 style="color:{status_color}">{d['name']}</h3>
            <p>ID: {d['device_id']} | Type: {d['type']}</p>
            <p>Status: <span style="color:{status_color}">{d['status']}</span></p>
            <p>Pins: {len(d['pins'])} | Alerts: {d['alerts']}</p>
            <div class="pins">
                {''.join(f'<button class="pin-btn" onclick="togglePin(\'{d["device_id"]}\',{pin},{1-state})">{pin}:{state}</button>' for pin, info in d['pins'].items() for state in [info['state']])}
            </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>IoT Dashboard</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0a0a0a; color:#00ff41; font-family:monospace; padding:10px; }}
h1 {{ text-align:center; margin:10px 0; font-size:1.5em; }}
.device-card {{ background:#111; border:1px solid #00ff41; border-radius:8px; padding:15px; margin:10px 0; }}
.pins {{ display:flex; gap:5px; flex-wrap:wrap; margin-top:10px; }}
.pin-btn {{ background:#1a1a1a; color:#00ff41; border:1px solid #00ff41; padding:5px 10px; border-radius:4px; cursor:pointer; font-family:monospace; }}
.pin-btn:hover {{ background:#00ff41; color:#0a0a0a; }}
.status-dot {{ width:8px; height:8px; border-radius:50%; display:inline-block; }}
</style>
</head>
<body>
<h1>📡 IoT Dashboard</h1>
{device_cards if device_cards else '<p style="text-align:center">No devices. Add one with /iot add</p>'}
<script>
function togglePin(deviceId, pin, state) {{
    fetch('/api/iot/pin', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{device_id: deviceId, pin: pin, state: state}})
    }});
}}
</script>
</body>
</html>"""
