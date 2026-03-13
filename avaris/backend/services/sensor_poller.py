"""
ESP32 Sensor Polling Service for AVARIS
Polls ESP32 sensor server for environmental data instead of waiting for pushes
"""

# Python 3.13 compatibility fix for cgi module
import sys
if sys.version_info >= (3, 13):
    try:
        import cgi
    except ImportError:
        # Create a minimal cgi module stub for Python 3.13 compatibility
        import types
        import html
        import email.message
        
        cgi = types.ModuleType('cgi')
        # Provide the most commonly used cgi functions
        cgi.escape = html.escape  # html.escape is the modern replacement
        cgi.parse_qs = lambda qs, keep_blank_values=False, strict_parsing=False: {}
        cgi.parse_qsl = lambda qs, keep_blank_values=False, strict_parsing=False: []
        
        # Add parse_header function that httpx needs
        def parse_header(line):
            """Parse a Content-type like header."""
            parts = line.split(';')
            main_type = parts[0].strip()
            pdict = {}
            for p in parts[1:]:
                if '=' in p:
                    name, value = p.split('=', 1)
                    name = name.strip().lower()
                    value = value.strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    pdict[name] = value
            return main_type, pdict
        
        cgi.parse_header = parse_header
        
        # Add to sys.modules so other imports can find it
        sys.modules['cgi'] = cgi

import asyncio
import logging
import httpx
from typing import Optional, Dict, Any
from datetime import datetime
import json

from backend.config.settings import settings

logger = logging.getLogger(__name__)

class SensorPoller:
    def __init__(self):
        self.esp32_url = f"http://{settings.ESP32_SENSOR_IP}/sensors"
        self.poll_interval = settings.SENSOR_POLL_INTERVAL
        self.latest_data: Optional[Dict[str, Any]] = None
        self.is_running = False
        self.client = httpx.AsyncClient(timeout=5.0)
        
    async def start_polling(self):
        """Start the polling loop"""
        if self.is_running:
            logger.warning("Sensor polling already running")
            return
            
        self.is_running = True
        logger.info(f"Starting sensor polling from {self.esp32_url} every {self.poll_interval}s")
        
        while self.is_running:
            try:
                await self.poll_sensors()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                await asyncio.sleep(self.poll_interval)
    
    async def stop_polling(self):
        """Stop the polling loop"""
        self.is_running = False
        await self.client.aclose()
        logger.info("Sensor polling stopped")
    
    async def poll_sensors(self) -> Optional[Dict[str, Any]]:
        """Poll ESP32 for latest sensor data"""
        try:
            logger.debug(f"Polling sensors from {self.esp32_url}")
            
            response = await self.client.get(self.esp32_url)
            response.raise_for_status()
            
            data = response.json()
            
            # Validate response structure
            if not self._validate_sensor_data(data):
                logger.warning(f"Invalid sensor data received: {data}")
                return None
            
            # Add server timestamp
            data['server_timestamp'] = datetime.now().isoformat()
            
            # Store latest data
            self.latest_data = data
            
            logger.debug(f"Received sensor data: T={data.get('temperature')}°C, "
                        f"H={data.get('humidity')}%, D={data.get('dust')}µg/m³")
            
            # Store in database and calculate risk (async task)
            asyncio.create_task(self._store_sensor_data(data))
            
            return data
            
        except Exception as e:
            # Handle all httpx exceptions generically
            error_type = type(e).__name__
            
            if 'timeout' in error_type.lower() or 'Timeout' in error_type:
                logger.warning(f"Timeout polling ESP32 at {self.esp32_url}")
            elif 'connect' in error_type.lower() or 'Network' in error_type:
                logger.warning(f"Cannot connect to ESP32 at {self.esp32_url}")
            elif 'HTTP' in error_type:
                logger.warning(f"HTTP error polling ESP32: {e}")
            elif 'JSON' in error_type or 'json' in str(e).lower():
                logger.warning("Invalid JSON response from ESP32")
            else:
                logger.error(f"Unexpected error polling sensors ({error_type}): {e}")
            
            return None
    
    async def _store_sensor_data(self, data: Dict[str, Any]):
        """Store sensor data and risk assessment in database"""
        try:
            from backend.database.init_db import get_db
            from backend.database.models import SensorData, RiskPrediction
            from backend.api.routes import calculate_rule_based_risk
            
            # Get database session
            db = next(get_db())
            
            try:
                # Store sensor data
                sensor_record = SensorData(
                    temperature=data['temperature'],
                    humidity=data['humidity'],
                    dust=data['dust'],
                    timestamp=datetime.now()
                )
                db.add(sensor_record)
                
                # Calculate and store risk assessment
                risk_level, confidence = calculate_rule_based_risk(
                    data['temperature'],
                    data['humidity'],
                    data['dust']
                )
                
                risk_record = RiskPrediction(
                    risk_level=risk_level,
                    confidence=confidence,
                    timestamp=datetime.now()
                )
                db.add(risk_record)
                
                db.commit()
                
                logger.debug(f"Stored sensor data and risk assessment: {risk_level} ({confidence:.2f})")
                
            except Exception as e:
                db.rollback()
                logger.error(f"Database error storing sensor data: {e}")
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error storing sensor data: {e}")
    
    def _validate_sensor_data(self, data: Dict[str, Any]) -> bool:
        """Validate sensor data structure"""
        required_fields = ['temperature', 'humidity', 'dust']
        
        if not isinstance(data, dict):
            return False
            
        for field in required_fields:
            if field not in data:
                return False
            if not isinstance(data[field], (int, float)):
                return False
                
        # Check reasonable ranges
        temp = data['temperature']
        humidity = data['humidity']
        dust = data['dust']
        
        if not (-40 <= temp <= 80):  # DHT22 range
            logger.warning(f"Temperature out of range: {temp}°C")
            return False
            
        if not (0 <= humidity <= 100):  # Humidity percentage
            logger.warning(f"Humidity out of range: {humidity}%")
            return False
            
        if not (0 <= dust <= 1000):  # Dust density µg/m³
            logger.warning(f"Dust level out of range: {dust}µg/m³")
            return False
            
        return True
    
    def get_latest_data(self) -> Optional[Dict[str, Any]]:
        """Get the latest polled sensor data"""
        return self.latest_data
    
    def is_data_fresh(self, max_age_seconds: int = 30) -> bool:
        """Check if latest data is fresh enough"""
        if not self.latest_data or 'server_timestamp' not in self.latest_data:
            return False
            
        try:
            timestamp = datetime.fromisoformat(self.latest_data['server_timestamp'])
            age = (datetime.now() - timestamp).total_seconds()
            return age <= max_age_seconds
        except Exception:
            return False

# Global poller instance
_sensor_poller: Optional[SensorPoller] = None

def get_sensor_poller() -> SensorPoller:
    """Get the global sensor poller instance"""
    global _sensor_poller
    if _sensor_poller is None:
        _sensor_poller = SensorPoller()
    return _sensor_poller

async def start_sensor_polling():
    """Start the global sensor polling service"""
    poller = get_sensor_poller()
    # Run polling in background task
    asyncio.create_task(poller.start_polling())

async def stop_sensor_polling():
    """Stop the global sensor polling service"""
    poller = get_sensor_poller()
    await poller.stop_polling()