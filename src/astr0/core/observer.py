"""
Observer location management.

Handles observer profiles with location, elevation, and timezone.
Profiles are stored in ~/.astr0/observers.toml.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, List
import math

from astr0.core.angles import Angle


@dataclass(frozen=True)
class Observer:
    """
    An astronomical observer with location information.
    
    Attributes:
        name: Human-readable name for this location
        latitude: Geographic latitude (positive North)
        longitude: Geographic longitude (positive East)
        elevation: Elevation above sea level in meters
        timezone: IANA timezone string (e.g., 'America/Los_Angeles')
    """
    
    name: str
    latitude: Angle
    longitude: Angle
    elevation: float = 0.0
    timezone: Optional[str] = None
    
    @classmethod
    def from_degrees(
        cls,
        name: str,
        latitude: float,
        longitude: float,
        elevation: float = 0.0,
        timezone: Optional[str] = None
    ) -> Observer:
        """Create an Observer from decimal degree coordinates."""
        return cls(
            name=name,
            latitude=Angle(degrees=latitude),
            longitude=Angle(degrees=longitude),
            elevation=elevation,
            timezone=timezone
        )
    
    @property
    def lat_deg(self) -> float:
        """Latitude in decimal degrees."""
        return self.latitude.degrees
    
    @property
    def lon_deg(self) -> float:
        """Longitude in decimal degrees."""
        return self.longitude.degrees
    
    def __str__(self) -> str:
        lat_dir = "N" if self.lat_deg >= 0 else "S"
        lon_dir = "E" if self.lon_deg >= 0 else "W"
        return (
            f"{self.name}: "
            f"{abs(self.lat_deg):.4f}°{lat_dir}, "
            f"{abs(self.lon_deg):.4f}°{lon_dir}, "
            f"{self.elevation:.0f}m"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        d = {
            'name': self.name,
            'latitude': self.lat_deg,
            'longitude': self.lon_deg,
            'elevation': self.elevation,
        }
        if self.timezone:
            d['timezone'] = self.timezone
        return d
    
    @classmethod
    def from_dict(cls, name: str, data: dict) -> Observer:
        """Create Observer from dictionary."""
        return cls.from_degrees(
            name=data.get('name', name),
            latitude=data['latitude'],
            longitude=data['longitude'],
            elevation=data.get('elevation', 0.0),
            timezone=data.get('timezone')
        )


def get_config_dir() -> Path:
    """Get the astr0 configuration directory."""
    config_dir = Path.home() / '.astr0'
    return config_dir


def get_config_file() -> Path:
    """Get the observers configuration file path."""
    return get_config_dir() / 'observers.toml'


def ensure_config_dir() -> Path:
    """Ensure configuration directory exists."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def _parse_toml(content: str) -> dict:
    """Simple TOML parser for observer config files.
    
    Supports basic key=value pairs and [section] headers.
    This avoids requiring tomllib (Python 3.11+) or external deps.
    """
    result = {}
    current_section = None
    
    for line in content.split('\n'):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        
        # Section header
        if line.startswith('[') and line.endswith(']'):
            section_path = line[1:-1].split('.')
            
            # Navigate/create nested structure
            current = result
            for part in section_path[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            section_name = section_path[-1]
            if section_name not in current:
                current[section_name] = {}
            current_section = current[section_name]
            continue
        
        # Key = value
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Parse value
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            elif value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif '.' in value:
                try:
                    value = float(value)
                except ValueError:
                    pass
            else:
                try:
                    value = int(value)
                except ValueError:
                    pass
            
            if current_section is not None:
                current_section[key] = value
            else:
                result[key] = value
    
    return result


def _to_toml(data: dict, prefix: str = '') -> str:
    """Convert dictionary to TOML string."""
    lines = []
    
    # First write simple key-value pairs
    for key, value in data.items():
        if not isinstance(value, dict):
            if isinstance(value, str):
                lines.append(f'{key} = "{value}"')
            elif isinstance(value, bool):
                lines.append(f'{key} = {str(value).lower()}')
            elif isinstance(value, float):
                lines.append(f'{key} = {value}')
            elif isinstance(value, int):
                lines.append(f'{key} = {value}')
    
    # Then write sections
    for key, value in data.items():
        if isinstance(value, dict):
            section_path = f'{prefix}.{key}' if prefix else key
            lines.append('')
            lines.append(f'[{section_path}]')
            
            # Write section contents
            for k, v in value.items():
                if isinstance(v, dict):
                    # Nested section
                    lines.append(_to_toml({k: v}, section_path))
                else:
                    if isinstance(v, str):
                        lines.append(f'{k} = "{v}"')
                    elif isinstance(v, bool):
                        lines.append(f'{k} = {str(v).lower()}')
                    elif isinstance(v, float):
                        lines.append(f'{k} = {v}')
                    elif isinstance(v, int):
                        lines.append(f'{k} = {v}')
    
    return '\n'.join(lines)


class ObserverManager:
    """Manages observer profiles stored in configuration file."""
    
    def __init__(self):
        self._observers: Dict[str, Observer] = {}
        self._default: Optional[str] = None
        self._loaded = False
    
    def _ensure_loaded(self):
        """Load observers from config file if not already loaded."""
        if self._loaded:
            return
        
        config_file = get_config_file()
        if config_file.exists():
            try:
                content = config_file.read_text()
                data = _parse_toml(content)
                
                self._default = data.get('default')
                
                observers_data = data.get('observers', {})
                for name, obs_data in observers_data.items():
                    self._observers[name] = Observer.from_dict(name, obs_data)
            except Exception:
                # If config is corrupt, start fresh
                pass
        
        self._loaded = True
    
    def _save(self):
        """Save observers to config file."""
        ensure_config_dir()
        
        data = {}
        if self._default:
            data['default'] = self._default
        
        data['observers'] = {}
        for name, obs in self._observers.items():
            data['observers'][name] = obs.to_dict()
        
        config_file = get_config_file()
        config_file.write_text(_to_toml(data))
    
    def add(self, observer: Observer) -> None:
        """Add or update an observer profile."""
        self._ensure_loaded()
        key = observer.name.lower().replace(' ', '_')
        self._observers[key] = observer
        
        # Set as default if it's the first one
        if self._default is None:
            self._default = key
        
        self._save()
    
    def remove(self, name: str) -> bool:
        """Remove an observer profile. Returns True if found."""
        self._ensure_loaded()
        key = name.lower().replace(' ', '_')
        
        if key in self._observers:
            del self._observers[key]
            if self._default == key:
                self._default = next(iter(self._observers.keys()), None)
            self._save()
            return True
        return False
    
    def get(self, name: str) -> Optional[Observer]:
        """Get an observer by name."""
        self._ensure_loaded()
        key = name.lower().replace(' ', '_')
        return self._observers.get(key)
    
    def get_default(self) -> Optional[Observer]:
        """Get the default observer."""
        self._ensure_loaded()
        if self._default:
            return self._observers.get(self._default)
        return None
    
    def set_default(self, name: str) -> bool:
        """Set the default observer. Returns True if found."""
        self._ensure_loaded()
        key = name.lower().replace(' ', '_')
        
        if key in self._observers:
            self._default = key
            self._save()
            return True
        return False
    
    def list_all(self) -> List[Observer]:
        """List all observer profiles."""
        self._ensure_loaded()
        return list(self._observers.values())
    
    @property
    def default_name(self) -> Optional[str]:
        """Get the name of the default observer."""
        self._ensure_loaded()
        return self._default


# Singleton instance
OBSERVERS = ObserverManager()


def get_observer(name: Optional[str] = None) -> Optional[Observer]:
    """
    Get an observer by name, or the default if no name given.
    
    Args:
        name: Observer name, or None for default
        
    Returns:
        Observer instance, or None if not found
    """
    if name:
        return OBSERVERS.get(name)
    return OBSERVERS.get_default()
