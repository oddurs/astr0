"""
Target visibility calculations.

Provides calculations for determining when celestial objects are observable
from a given location, including airmass, transit times, and visibility windows.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, List, Tuple

from astr0.core.angles import Angle, angular_separation
from astr0.core.time import JulianDate, jd_now
from astr0.core.coords import ICRSCoord
from astr0.core.observer import Observer
from astr0.core.sun import solar_altitude, sun_position
from astr0.core.moon import moon_position, moon_altitude, lunar_distance_to_sun
from astr0.core.constants import CONSTANTS
from astr0.verbose import VerboseContext, step


@dataclass(frozen=True)
class VisibilityWindow:
    """A time window when a target is observable."""
    
    start: JulianDate   # When target becomes observable
    end: JulianDate     # When target stops being observable
    peak_altitude: Angle  # Maximum altitude during window
    peak_time: JulianDate  # Time of maximum altitude
    
    @property
    def duration_hours(self) -> float:
        """Duration of the visibility window in hours."""
        return (self.end.jd - self.start.jd) * 24.0


@dataclass(frozen=True)
class TargetVisibility:
    """Complete visibility information for a target."""
    
    target: ICRSCoord
    observer: Observer
    date: JulianDate
    
    # Current state
    current_altitude: Angle
    current_airmass: Optional[float]
    is_up: bool
    
    # Events
    rise_time: Optional[JulianDate]
    set_time: Optional[JulianDate]
    transit_time: JulianDate
    transit_altitude: Angle
    
    # Moon separation
    moon_separation: Angle
    
    # Visibility windows (dark time when target is up)
    dark_windows: List[VisibilityWindow]


def airmass(altitude: Angle, verbose: Optional[VerboseContext] = None) -> Optional[float]:
    """
    Calculate the airmass for a given altitude.
    
    Uses the Pickering (2002) formula for accuracy down to the horizon.
    
    Args:
        altitude: Altitude above horizon
        verbose: Optional verbose context
        
    Returns:
        Airmass value, or None if below horizon
    """
    alt_deg = altitude.degrees
    
    if alt_deg <= 0:
        if verbose:
            step(verbose, "Airmass", "Target below horizon (altitude ≤ 0°)")
        return None
    
    # Pickering (2002) formula - accurate to horizon
    # X = 1 / sin(h + 244.46° / (165.0 + 47° × h^1.1))
    h = alt_deg
    denom_angle = 244.46 / (165.0 + 47.0 * (h ** 1.1))
    sin_term = math.sin(math.radians(h + denom_angle))
    
    if sin_term <= 0:
        return None
    
    X = 1.0 / sin_term
    
    if verbose:
        step(verbose, "Altitude", f"h = {alt_deg:.2f}°")
        step(verbose, "Airmass (Pickering)", f"X = {X:.3f}")
    
    return X


def target_altitude(target: ICRSCoord, observer: Observer, jd: JulianDate,
                    verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the altitude of a target at a given time and location.
    
    Args:
        target: Target coordinates (ICRS)
        observer: Observer location
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        Altitude above/below horizon
    """
    # Calculate local sidereal time
    T = (jd.jd - 2451545.0) / 36525.0
    theta0 = 280.46061837 + 360.98564736629 * (jd.jd - 2451545.0)
    theta0 += 0.000387933 * T**2 - T**3 / 38710000.0
    theta0 = theta0 % 360.0
    
    # Local sidereal time
    lst = theta0 + observer.lon_deg
    lst = lst % 360.0
    
    if verbose:
        step(verbose, "Local sidereal time", f"θ = {lst:.4f}°")
    
    # Hour angle
    H = lst - target.ra.degrees
    H_rad = math.radians(H)
    
    if verbose:
        step(verbose, "Hour angle", f"H = {H:.4f}°")
    
    # Observer latitude
    phi_rad = math.radians(observer.lat_deg)
    dec_rad = math.radians(target.dec.degrees)
    
    # Altitude formula
    sin_alt = (math.sin(phi_rad) * math.sin(dec_rad) +
               math.cos(phi_rad) * math.cos(dec_rad) * math.cos(H_rad))
    
    alt = math.degrees(math.asin(max(-1, min(1, sin_alt))))
    
    if verbose:
        step(verbose, "Altitude", f"h = {alt:.4f}°")
    
    return Angle(degrees=alt)


def target_azimuth(target: ICRSCoord, observer: Observer, jd: JulianDate,
                   verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the azimuth of a target at a given time and location.
    
    Args:
        target: Target coordinates (ICRS)
        observer: Observer location
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        Azimuth (N=0°, E=90°)
    """
    # Calculate local sidereal time
    T = (jd.jd - 2451545.0) / 36525.0
    theta0 = 280.46061837 + 360.98564736629 * (jd.jd - 2451545.0)
    theta0 += 0.000387933 * T**2 - T**3 / 38710000.0
    theta0 = theta0 % 360.0
    
    # Local sidereal time
    lst = theta0 + observer.lon_deg
    lst = lst % 360.0
    
    # Hour angle
    H = lst - target.ra.degrees
    H_rad = math.radians(H)
    
    # Observer latitude
    phi_rad = math.radians(observer.lat_deg)
    dec_rad = math.radians(target.dec.degrees)
    
    # Azimuth formula
    sin_az = -math.cos(dec_rad) * math.sin(H_rad)
    cos_az = (math.sin(dec_rad) * math.cos(phi_rad) -
              math.cos(dec_rad) * math.sin(phi_rad) * math.cos(H_rad))
    
    az = math.degrees(math.atan2(sin_az, cos_az))
    if az < 0:
        az += 360.0
    
    if verbose:
        step(verbose, "Azimuth", f"A = {az:.4f}°")
    
    return Angle(degrees=az)


def transit_time(target: ICRSCoord, observer: Observer, jd: JulianDate,
                 verbose: Optional[VerboseContext] = None) -> JulianDate:
    """
    Calculate when a target transits (crosses the meridian).
    
    Args:
        target: Target coordinates (ICRS)
        observer: Observer location
        jd: Julian Date (date to search)
        verbose: Optional verbose context
        
    Returns:
        JulianDate of transit
    """
    # Start from local midnight
    jd_midnight = JulianDate(math.floor(jd.jd - 0.5) + 0.5 + observer.lon_deg / 360.0)
    
    # Calculate approximate transit time
    # Transit occurs when LST = RA
    T = (jd_midnight.jd - 2451545.0) / 36525.0
    theta0 = 280.46061837 + 360.98564736629 * (jd_midnight.jd - 2451545.0)
    theta0 = theta0 % 360.0
    
    # LST at midnight
    lst_midnight = (theta0 + observer.lon_deg) % 360.0
    
    # Time until RA matches LST
    # LST increases by 360.98564736629°/day
    ra_deg = target.ra.degrees
    delta_lst = (ra_deg - lst_midnight) % 360.0
    
    # Convert LST difference to days
    transit_offset = delta_lst / 360.98564736629
    
    result = JulianDate(jd_midnight.jd + transit_offset)
    
    if verbose:
        step(verbose, "LST at midnight", f"θ = {lst_midnight:.4f}°")
        step(verbose, "Target RA", f"α = {ra_deg:.4f}°")
        step(verbose, "Transit", f"JD = {result.jd:.6f}")
    
    return result


def transit_altitude_calc(target: ICRSCoord, observer: Observer,
                          verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the maximum altitude a target reaches at transit.
    
    Args:
        target: Target coordinates (ICRS)
        observer: Observer location
        verbose: Optional verbose context
        
    Returns:
        Transit altitude
    """
    # Transit altitude = 90° - |φ - δ| for targets that transit south of zenith
    # Or = 90° + |φ - δ| - 180° = |φ - δ| - 90° for targets that transit north
    
    phi = observer.lat_deg
    delta = target.dec.degrees
    
    # For northern hemisphere observer:
    # If δ > φ, target transits north of zenith
    # If δ < φ, target transits south of zenith
    
    # General formula
    alt_transit = 90.0 - abs(phi - delta)
    
    if verbose:
        step(verbose, "Transit altitude formula", f"h_transit = 90° - |φ - δ|")
        step(verbose, "Observer latitude", f"φ = {phi:.4f}°")
        step(verbose, "Target declination", f"δ = {delta:.4f}°")
        step(verbose, "Transit altitude", f"h = {alt_transit:.4f}°")
    
    return Angle(degrees=alt_transit)


def target_rise_set(target: ICRSCoord, observer: Observer, jd: JulianDate,
                    horizon_altitude: float = 0.0,
                    verbose: Optional[VerboseContext] = None) -> Tuple[Optional[JulianDate], Optional[JulianDate]]:
    """
    Calculate rise and set times for a target.
    
    Args:
        target: Target coordinates (ICRS)
        observer: Observer location
        jd: Julian Date (date to search)
        horizon_altitude: Altitude considered as horizon (degrees)
        verbose: Optional verbose context
        
    Returns:
        Tuple of (rise_time, set_time), either may be None
    """
    # Start from local midnight
    jd_midnight = JulianDate(math.floor(jd.jd - 0.5) + 0.5 + observer.lon_deg / 360.0)
    
    if verbose:
        step(verbose, "Horizon altitude", f"h₀ = {horizon_altitude}°")
    
    # Search through the day
    dt = 0.01  # ~15 min steps
    
    rise_time = None
    set_time = None
    
    prev_alt = target_altitude(target, observer, jd_midnight).degrees
    
    for i in range(1, 120):  # Cover ~29 hours
        test_jd = JulianDate(jd_midnight.jd + i * dt)
        curr_alt = target_altitude(target, observer, test_jd).degrees
        
        # Rising
        if prev_alt < horizon_altitude <= curr_alt and rise_time is None:
            # Refine with bisection
            jd1 = JulianDate(test_jd.jd - dt)
            jd2 = test_jd
            
            for _ in range(15):
                jd_mid = JulianDate((jd1.jd + jd2.jd) / 2)
                mid_alt = target_altitude(target, observer, jd_mid).degrees
                
                if mid_alt < horizon_altitude:
                    jd1 = jd_mid
                else:
                    jd2 = jd_mid
            
            rise_time = JulianDate((jd1.jd + jd2.jd) / 2)
            
            if verbose:
                step(verbose, "Target rise", f"JD = {rise_time.jd:.6f}")
        
        # Setting
        if prev_alt >= horizon_altitude > curr_alt and set_time is None:
            # Refine with bisection
            jd1 = JulianDate(test_jd.jd - dt)
            jd2 = test_jd
            
            for _ in range(15):
                jd_mid = JulianDate((jd1.jd + jd2.jd) / 2)
                mid_alt = target_altitude(target, observer, jd_mid).degrees
                
                if mid_alt >= horizon_altitude:
                    jd1 = jd_mid
                else:
                    jd2 = jd_mid
            
            set_time = JulianDate((jd1.jd + jd2.jd) / 2)
            
            if verbose:
                step(verbose, "Target set", f"JD = {set_time.jd:.6f}")
        
        prev_alt = curr_alt
    
    return (rise_time, set_time)


def moon_target_separation(target: ICRSCoord, jd: JulianDate,
                           verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the angular separation between a target and the Moon.
    
    Args:
        target: Target coordinates (ICRS)
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        Angular separation
    """
    moon = moon_position(jd, verbose)
    moon_coord = moon.to_icrs()
    
    sep = angular_separation(target.ra, target.dec, moon_coord.ra, moon_coord.dec, verbose)
    
    if verbose:
        step(verbose, "Moon-target separation", f"θ = {sep.degrees:.2f}°")
    
    return sep


def is_night(observer: Observer, jd: JulianDate, 
             twilight: str = 'astronomical',
             verbose: Optional[VerboseContext] = None) -> bool:
    """
    Check if it's dark enough for observation.
    
    Args:
        observer: Observer location
        jd: Julian Date
        twilight: Twilight type ('civil', 'nautical', 'astronomical')
        verbose: Optional verbose context
        
    Returns:
        True if dark enough
    """
    sun_alt = solar_altitude(observer, jd, verbose)
    
    thresholds = {
        'civil': CONSTANTS.CIVIL_TWILIGHT_ALTITUDE.value,
        'nautical': CONSTANTS.NAUTICAL_TWILIGHT_ALTITUDE.value,
        'astronomical': CONSTANTS.ASTRONOMICAL_TWILIGHT_ALTITUDE.value,
    }
    
    threshold = thresholds.get(twilight, -18.0)
    is_dark = sun_alt.degrees < threshold
    
    if verbose:
        step(verbose, "Sun altitude", f"h☉ = {sun_alt.degrees:.2f}°")
        step(verbose, "Twilight threshold", f"{twilight}: {threshold}°")
        step(verbose, "Is night", f"{is_dark}")
    
    return is_dark


def compute_visibility(target: ICRSCoord, observer: Observer, jd: JulianDate,
                       min_altitude: float = 20.0,
                       twilight: str = 'astronomical',
                       verbose: Optional[VerboseContext] = None) -> TargetVisibility:
    """
    Compute comprehensive visibility information for a target.
    
    Args:
        target: Target coordinates (ICRS)
        observer: Observer location
        jd: Julian Date (date of observation)
        min_altitude: Minimum altitude for observation (degrees)
        twilight: Twilight type for determining dark time
        verbose: Optional verbose context
        
    Returns:
        TargetVisibility with all computed information
    """
    if verbose:
        step(verbose, "Computing visibility for", f"RA={target.ra.format_hms()}, Dec={target.dec.format_dms()}")
        step(verbose, "Observer", f"{observer.name}")
        step(verbose, "Minimum altitude", f"{min_altitude}°")
    
    # Current state
    curr_alt = target_altitude(target, observer, jd, verbose)
    curr_airmass = airmass(curr_alt, verbose) if curr_alt.degrees > 0 else None
    is_up = curr_alt.degrees > min_altitude
    
    # Rise/set times
    rise, set_t = target_rise_set(target, observer, jd, min_altitude, verbose)
    
    # Transit
    trans = transit_time(target, observer, jd, verbose)
    trans_alt = transit_altitude_calc(target, observer, verbose)
    
    # Moon separation
    moon_sep = moon_target_separation(target, jd, verbose)
    
    # Find dark windows when target is observable
    # This is simplified - a full implementation would search for sunset/sunrise
    dark_windows: List[VisibilityWindow] = []
    
    return TargetVisibility(
        target=target,
        observer=observer,
        date=jd,
        current_altitude=curr_alt,
        current_airmass=curr_airmass,
        is_up=is_up,
        rise_time=rise,
        set_time=set_t,
        transit_time=trans,
        transit_altitude=trans_alt,
        moon_separation=moon_sep,
        dark_windows=dark_windows
    )


def observable_tonight(targets: List[ICRSCoord], observer: Observer, jd: JulianDate,
                       min_altitude: float = 30.0,
                       min_moon_sep: float = 30.0,
                       verbose: Optional[VerboseContext] = None) -> List[Tuple[ICRSCoord, float]]:
    """
    Filter a list of targets by observability tonight.
    
    Args:
        targets: List of target coordinates
        observer: Observer location
        jd: Julian Date (date of observation)
        min_altitude: Minimum altitude for observation (degrees)
        min_moon_sep: Minimum moon separation (degrees)
        verbose: Optional verbose context
        
    Returns:
        List of (target, transit_altitude) for observable targets, sorted by transit
    """
    observable = []
    
    for target in targets:
        trans_alt = transit_altitude_calc(target, observer)
        
        if trans_alt.degrees < min_altitude:
            continue
        
        moon_sep = moon_target_separation(target, jd)
        if moon_sep.degrees < min_moon_sep:
            continue
        
        trans = transit_time(target, observer, jd)
        observable.append((target, trans_alt.degrees, trans.jd))
    
    # Sort by transit time
    observable.sort(key=lambda x: x[2])
    
    return [(t, alt) for t, alt, _ in observable]
