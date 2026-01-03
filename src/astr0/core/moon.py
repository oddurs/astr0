"""
Lunar position and event calculations.

Implements lunar position using algorithms from Meeus, "Astronomical Algorithms".
Provides moon position, phase, illumination, and rise/set times.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple, List
from enum import Enum

from astr0.core.angles import Angle
from astr0.core.time import JulianDate, jd_now
from astr0.core.coords import ICRSCoord
from astr0.core.observer import Observer
from astr0.core.constants import CONSTANTS
from astr0.verbose import VerboseContext, step


class MoonPhase(Enum):
    """Named lunar phases."""
    NEW_MOON = "New Moon"
    WAXING_CRESCENT = "Waxing Crescent"
    FIRST_QUARTER = "First Quarter"
    WAXING_GIBBOUS = "Waxing Gibbous"
    FULL_MOON = "Full Moon"
    WANING_GIBBOUS = "Waning Gibbous"
    LAST_QUARTER = "Last Quarter"
    WANING_CRESCENT = "Waning Crescent"


@dataclass(frozen=True)
class MoonPosition:
    """Lunar position at a given instant."""
    
    # Geocentric ecliptic coordinates
    longitude: Angle  # Ecliptic longitude
    latitude: Angle   # Ecliptic latitude
    
    # Equatorial coordinates
    ra: Angle         # Right Ascension
    dec: Angle        # Declination
    
    # Distance
    distance_km: float   # Earth-Moon distance in km
    distance_earth_radii: float  # Distance in Earth radii
    
    # Angular size
    angular_diameter: Angle  # Apparent angular diameter
    
    # Parallax
    parallax: Angle  # Horizontal parallax
    
    def to_icrs(self) -> ICRSCoord:
        """Convert to ICRS coordinate."""
        return ICRSCoord(ra=self.ra, dec=self.dec)


@dataclass(frozen=True)
class MoonPhaseInfo:
    """Information about the Moon's phase."""
    
    phase_angle: float      # Phase angle in degrees (0-360)
    illumination: float     # Fraction illuminated (0-1)
    phase_name: MoonPhase   # Named phase
    age_days: float         # Days since last new moon
    
    @property
    def percent_illuminated(self) -> float:
        """Return illumination as percentage."""
        return self.illumination * 100


def _julian_century(jd: JulianDate) -> float:
    """Calculate Julian centuries from J2000.0."""
    return (jd.jd - 2451545.0) / 36525.0


def moon_mean_longitude(jd: JulianDate, verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the Moon's mean longitude.
    
    Args:
        jd: Julian Date
        verbose: Optional verbose context for calculation steps
        
    Returns:
        Moon's mean longitude as an Angle
    """
    T = _julian_century(jd)
    
    # Meeus Chapter 47
    L_prime = (218.3164477 
               + 481267.88123421 * T 
               - 0.0015786 * T**2
               + T**3 / 538841
               - T**4 / 65194000)
    
    L_prime = L_prime % 360.0
    if L_prime < 0:
        L_prime += 360.0
    
    if verbose:
        step(verbose, "Moon mean longitude", 
             f"L' = 218.3164° + 481267.881° × T = {L_prime:.6f}°")
    
    return Angle(degrees=L_prime)


def moon_mean_anomaly(jd: JulianDate, verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the Moon's mean anomaly.
    
    Args:
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        Moon's mean anomaly as an Angle
    """
    T = _julian_century(jd)
    
    # Meeus Chapter 47
    M_prime = (134.9633964
               + 477198.8675055 * T
               + 0.0087414 * T**2
               + T**3 / 69699
               - T**4 / 14712000)
    
    M_prime = M_prime % 360.0
    if M_prime < 0:
        M_prime += 360.0
    
    if verbose:
        step(verbose, "Moon mean anomaly", f"M' = {M_prime:.6f}°")
    
    return Angle(degrees=M_prime)


def moon_mean_elongation(jd: JulianDate, verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the Moon's mean elongation from the Sun.
    
    Args:
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        Mean elongation as an Angle
    """
    T = _julian_century(jd)
    
    # Meeus Chapter 47
    D = (297.8501921
         + 445267.1114034 * T
         - 0.0018819 * T**2
         + T**3 / 545868
         - T**4 / 113065000)
    
    D = D % 360.0
    if D < 0:
        D += 360.0
    
    if verbose:
        step(verbose, "Mean elongation", f"D = {D:.6f}°")
    
    return Angle(degrees=D)


def moon_argument_of_latitude(jd: JulianDate, verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the Moon's argument of latitude.
    
    Args:
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        Argument of latitude as an Angle
    """
    T = _julian_century(jd)
    
    # Meeus Chapter 47
    F = (93.2720950
         + 483202.0175233 * T
         - 0.0036539 * T**2
         - T**3 / 3526000
         + T**4 / 863310000)
    
    F = F % 360.0
    if F < 0:
        F += 360.0
    
    if verbose:
        step(verbose, "Argument of latitude", f"F = {F:.6f}°")
    
    return Angle(degrees=F)


def sun_mean_anomaly_for_moon(jd: JulianDate) -> Angle:
    """Calculate Sun's mean anomaly (for Moon calculations)."""
    T = _julian_century(jd)
    
    M = (357.5291092
         + 35999.0502909 * T
         - 0.0001536 * T**2
         + T**3 / 24490000)
    
    M = M % 360.0
    if M < 0:
        M += 360.0
    
    return Angle(degrees=M)


def moon_position(jd: JulianDate, verbose: Optional[VerboseContext] = None) -> MoonPosition:
    """
    Calculate the geocentric position of the Moon.
    
    Uses the simplified algorithm from Meeus Chapter 47.
    Accuracy is about 10" in longitude and 4" in latitude.
    
    Args:
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        MoonPosition with all calculated parameters
    """
    T = _julian_century(jd)
    
    if verbose:
        step(verbose, "Julian century", f"T = {T:.10f}")
    
    # Fundamental arguments
    L_prime = moon_mean_longitude(jd, verbose)
    D = moon_mean_elongation(jd, verbose)
    M = sun_mean_anomaly_for_moon(jd)
    M_prime = moon_mean_anomaly(jd, verbose)
    F = moon_argument_of_latitude(jd, verbose)
    
    # Convert to radians for trig
    L_rad = math.radians(L_prime.degrees)
    D_rad = math.radians(D.degrees)
    M_rad = math.radians(M.degrees)
    Mp_rad = math.radians(M_prime.degrees)
    F_rad = math.radians(F.degrees)
    
    # Additional arguments
    A1 = math.radians((119.75 + 131.849 * T) % 360)
    A2 = math.radians((53.09 + 479264.290 * T) % 360)
    A3 = math.radians((313.45 + 481266.484 * T) % 360)
    
    # Eccentricity of Earth's orbit
    E = 1 - 0.002516 * T - 0.0000074 * T**2
    E2 = E * E
    
    if verbose:
        step(verbose, "Earth eccentricity", f"E = {E:.8f}")
    
    # Sum the periodic terms for longitude and distance
    # These are the most significant terms from Meeus Table 47.A
    
    # Sigma_l terms (longitude)
    sigma_l = 0.0
    sigma_l += 6288774 * math.sin(Mp_rad)
    sigma_l += 1274027 * math.sin(2*D_rad - Mp_rad)
    sigma_l += 658314 * math.sin(2*D_rad)
    sigma_l += 213618 * math.sin(2*Mp_rad)
    sigma_l += -185116 * E * math.sin(M_rad)
    sigma_l += -114332 * math.sin(2*F_rad)
    sigma_l += 58793 * math.sin(2*D_rad - 2*Mp_rad)
    sigma_l += 57066 * E * math.sin(2*D_rad - M_rad - Mp_rad)
    sigma_l += 53322 * math.sin(2*D_rad + Mp_rad)
    sigma_l += 45758 * E * math.sin(2*D_rad - M_rad)
    sigma_l += -40923 * E * math.sin(M_rad - Mp_rad)
    sigma_l += -34720 * math.sin(D_rad)
    sigma_l += -30383 * E * math.sin(M_rad + Mp_rad)
    sigma_l += 15327 * math.sin(2*D_rad - 2*F_rad)
    sigma_l += -12528 * math.sin(Mp_rad + 2*F_rad)
    sigma_l += 10980 * math.sin(Mp_rad - 2*F_rad)
    sigma_l += 10675 * math.sin(4*D_rad - Mp_rad)
    sigma_l += 10034 * math.sin(3*Mp_rad)
    sigma_l += 8548 * math.sin(4*D_rad - 2*Mp_rad)
    sigma_l += -7888 * E * math.sin(2*D_rad + M_rad - Mp_rad)
    sigma_l += -6766 * E * math.sin(2*D_rad + M_rad)
    sigma_l += -5163 * math.sin(D_rad - Mp_rad)
    sigma_l += 4987 * E * math.sin(D_rad + M_rad)
    sigma_l += 4036 * E * math.sin(2*D_rad - M_rad + Mp_rad)
    
    # Add A1, A2 corrections
    sigma_l += 3958 * math.sin(A1)
    sigma_l += 1962 * math.sin(L_rad - F_rad)
    sigma_l += 318 * math.sin(A2)
    
    # Sigma_r terms (distance)
    sigma_r = 0.0
    sigma_r += -20905355 * math.cos(Mp_rad)
    sigma_r += -3699111 * math.cos(2*D_rad - Mp_rad)
    sigma_r += -2955968 * math.cos(2*D_rad)
    sigma_r += -569925 * math.cos(2*Mp_rad)
    sigma_r += 48888 * E * math.cos(M_rad)
    sigma_r += -3149 * math.cos(2*F_rad)
    sigma_r += 246158 * math.cos(2*D_rad - 2*Mp_rad)
    sigma_r += -152138 * E * math.cos(2*D_rad - M_rad - Mp_rad)
    sigma_r += -170733 * math.cos(2*D_rad + Mp_rad)
    sigma_r += -204586 * E * math.cos(2*D_rad - M_rad)
    sigma_r += -129620 * E * math.cos(M_rad - Mp_rad)
    sigma_r += 108743 * math.cos(D_rad)
    sigma_r += 104755 * E * math.cos(M_rad + Mp_rad)
    sigma_r += 79661 * math.cos(Mp_rad - 2*F_rad)
    
    # Sigma_b terms (latitude)
    sigma_b = 0.0
    sigma_b += 5128122 * math.sin(F_rad)
    sigma_b += 280602 * math.sin(Mp_rad + F_rad)
    sigma_b += 277693 * math.sin(Mp_rad - F_rad)
    sigma_b += 173237 * math.sin(2*D_rad - F_rad)
    sigma_b += 55413 * math.sin(2*D_rad - Mp_rad + F_rad)
    sigma_b += 46271 * math.sin(2*D_rad - Mp_rad - F_rad)
    sigma_b += 32573 * math.sin(2*D_rad + F_rad)
    sigma_b += 17198 * math.sin(2*Mp_rad + F_rad)
    sigma_b += 9266 * math.sin(2*D_rad + Mp_rad - F_rad)
    sigma_b += 8822 * math.sin(2*Mp_rad - F_rad)
    sigma_b += 8216 * E * math.sin(2*D_rad - M_rad - F_rad)
    sigma_b += 4324 * math.sin(2*D_rad - 2*Mp_rad - F_rad)
    sigma_b += 4200 * math.sin(2*D_rad + Mp_rad + F_rad)
    
    # Add A1, A3 corrections
    sigma_b += -3359 * math.sin(A1 - F_rad)
    sigma_b += -2463 * math.sin(2*D_rad + F_rad)
    sigma_b += -1870 * math.sin(2*D_rad - M_rad - Mp_rad + F_rad) * E
    sigma_b += 1828 * math.sin(4*D_rad - Mp_rad - F_rad)
    sigma_b += -1714 * math.sin(A3)
    
    # Calculate coordinates
    longitude = L_prime.degrees + sigma_l / 1000000.0
    latitude = sigma_b / 1000000.0
    distance = 385000.56 + sigma_r / 1000.0  # km
    
    longitude = longitude % 360.0
    if longitude < 0:
        longitude += 360.0
    
    if verbose:
        step(verbose, "Σl (longitude correction)", f"Σl = {sigma_l/1000000:.6f}°")
        step(verbose, "Σb (latitude)", f"Σb = {sigma_b/1000000:.6f}°")
        step(verbose, "Σr (distance correction)", f"Σr = {sigma_r/1000:.2f} km")
        step(verbose, "Geocentric longitude", f"λ = {longitude:.6f}°")
        step(verbose, "Geocentric latitude", f"β = {latitude:.6f}°")
        step(verbose, "Distance", f"Δ = {distance:.2f} km")
    
    # Convert to equatorial coordinates
    # Obliquity of ecliptic
    epsilon = 23.439291 - 0.0130042 * T - 1.64e-7 * T**2 + 5.04e-7 * T**3
    
    lon_rad = math.radians(longitude)
    lat_rad = math.radians(latitude)
    eps_rad = math.radians(epsilon)
    
    # Convert ecliptic to equatorial
    sin_lon = math.sin(lon_rad)
    cos_lon = math.cos(lon_rad)
    sin_lat = math.sin(lat_rad)
    cos_lat = math.cos(lat_rad)
    sin_eps = math.sin(eps_rad)
    cos_eps = math.cos(eps_rad)
    
    # Right Ascension
    ra = math.atan2(sin_lon * cos_eps - math.tan(lat_rad) * sin_eps, cos_lon)
    ra_deg = math.degrees(ra) % 360.0
    
    # Declination
    dec = math.asin(sin_lat * cos_eps + cos_lat * sin_eps * sin_lon)
    dec_deg = math.degrees(dec)
    
    if verbose:
        step(verbose, "Obliquity of ecliptic", f"ε = {epsilon:.6f}°")
        step(verbose, "Right Ascension", f"α = {ra_deg:.6f}°")
        step(verbose, "Declination", f"δ = {dec_deg:.6f}°")
    
    # Calculate angular diameter and parallax
    # Mean lunar distance = 384400 km, mean angular diameter = 0.5181°
    angular_diameter = 0.5181 * (384400.0 / distance)
    
    # Horizontal parallax
    # sin(π) = Earth_radius / distance
    parallax = math.degrees(math.asin(6378.14 / distance))
    
    # Distance in Earth radii
    earth_radii = distance / 6378.14
    
    if verbose:
        step(verbose, "Angular diameter", f"θ = {angular_diameter:.4f}°")
        step(verbose, "Horizontal parallax", f"π = {parallax:.4f}°")
    
    return MoonPosition(
        longitude=Angle(degrees=longitude),
        latitude=Angle(degrees=latitude),
        ra=Angle(degrees=ra_deg),
        dec=Angle(degrees=dec_deg),
        distance_km=distance,
        distance_earth_radii=earth_radii,
        angular_diameter=Angle(degrees=angular_diameter),
        parallax=Angle(degrees=parallax)
    )


def moon_phase(jd: JulianDate, verbose: Optional[VerboseContext] = None) -> MoonPhaseInfo:
    """
    Calculate the Moon's phase information.
    
    Args:
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        MoonPhaseInfo with phase details
    """
    # Get elongation from sun
    D = moon_mean_elongation(jd, verbose)
    
    # Phase angle (0 = new, 180 = full)
    # This is a simplification; for high accuracy, use actual positions
    phase_angle = D.degrees
    
    # Illuminated fraction (Meeus Chapter 48)
    # k = (1 + cos(i)) / 2 where i is phase angle
    i_rad = math.radians(phase_angle)
    illumination = (1 - math.cos(i_rad)) / 2
    
    if verbose:
        step(verbose, "Phase angle", f"i = {phase_angle:.2f}°")
        step(verbose, "Illumination", f"k = {illumination:.4f} ({illumination*100:.1f}%)")
    
    # Determine named phase
    # Normalize to 0-360
    d = phase_angle % 360
    if d < 0:
        d += 360
    
    if d < 22.5 or d >= 337.5:
        phase_name = MoonPhase.NEW_MOON
    elif d < 67.5:
        phase_name = MoonPhase.WAXING_CRESCENT
    elif d < 112.5:
        phase_name = MoonPhase.FIRST_QUARTER
    elif d < 157.5:
        phase_name = MoonPhase.WAXING_GIBBOUS
    elif d < 202.5:
        phase_name = MoonPhase.FULL_MOON
    elif d < 247.5:
        phase_name = MoonPhase.WANING_GIBBOUS
    elif d < 292.5:
        phase_name = MoonPhase.LAST_QUARTER
    else:
        phase_name = MoonPhase.WANING_CRESCENT
    
    # Age in days (synodic month = 29.530589 days)
    synodic = CONSTANTS.SYNODIC_MONTH.value
    age_days = (d / 360.0) * synodic
    
    if verbose:
        step(verbose, "Phase name", f"{phase_name.value}")
        step(verbose, "Age", f"{age_days:.2f} days since new moon")
    
    return MoonPhaseInfo(
        phase_angle=phase_angle,
        illumination=illumination,
        phase_name=phase_name,
        age_days=age_days
    )


def moon_altitude(observer: Observer, jd: JulianDate, 
                  verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the Moon's altitude at a given time and location.
    
    Args:
        observer: Observer location
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        Altitude above/below horizon as Angle
    """
    pos = moon_position(jd, verbose)
    
    # Calculate local sidereal time
    T = _julian_century(jd)
    theta0 = 280.46061837 + 360.98564736629 * (jd.jd - 2451545.0)
    theta0 += 0.000387933 * T**2 - T**3 / 38710000.0
    theta0 = theta0 % 360.0
    
    # Local sidereal time
    lst = theta0 + observer.lon_deg
    lst = lst % 360.0
    
    # Hour angle
    H = lst - pos.ra.degrees
    H_rad = math.radians(H)
    
    # Observer latitude
    phi_rad = math.radians(observer.lat_deg)
    dec_rad = math.radians(pos.dec.degrees)
    
    # Altitude
    sin_alt = (math.sin(phi_rad) * math.sin(dec_rad) + 
               math.cos(phi_rad) * math.cos(dec_rad) * math.cos(H_rad))
    alt = math.degrees(math.asin(sin_alt))
    
    # Apply parallax correction (Moon is close enough to matter)
    parallax_correction = pos.parallax.degrees * math.cos(math.radians(alt))
    alt_corrected = alt - parallax_correction
    
    if verbose:
        step(verbose, "Local sidereal time", f"θ = {lst:.4f}°")
        step(verbose, "Hour angle", f"H = {H:.4f}°")
        step(verbose, "Geometric altitude", f"h = {alt:.4f}°")
        step(verbose, "Parallax correction", f"Δh = {parallax_correction:.4f}°")
        step(verbose, "Apparent altitude", f"h' = {alt_corrected:.4f}°")
    
    return Angle(degrees=alt_corrected)


def _moon_transit_altitude(observer: Observer, jd: JulianDate) -> float:
    """Helper to find when moon crosses a given altitude."""
    return moon_altitude(observer, jd).degrees


def moonrise(observer: Observer, jd: JulianDate,
             verbose: Optional[VerboseContext] = None) -> Optional[JulianDate]:
    """
    Calculate moonrise time.
    
    Args:
        observer: Observer location
        jd: Julian Date (date of interest)
        verbose: Optional verbose context
        
    Returns:
        JulianDate of moonrise or None if Moon doesn't rise
    """
    # Rise altitude accounting for refraction and Moon's angular size
    rise_altitude = CONSTANTS.RISE_SET_ALTITUDE_MOON.value
    
    if verbose:
        step(verbose, "Rise altitude", f"h₀ = {rise_altitude}° (refraction + semidiameter)")
    
    # Start from local midnight
    jd_midnight = JulianDate(math.floor(jd.jd - 0.5) + 0.5 + observer.lon_deg / 360.0)
    
    # Search through the day
    dt = 0.01  # Search step in days (~15 min)
    
    prev_alt = moon_altitude(observer, jd_midnight).degrees
    
    for i in range(1, 150):  # Cover ~1.5 days
        test_jd = JulianDate(jd_midnight.jd + i * dt)
        curr_alt = moon_altitude(observer, test_jd).degrees
        
        # Check for rising (crossing from below to above horizon)
        if prev_alt < rise_altitude <= curr_alt:
            # Refine with bisection
            jd1 = JulianDate(test_jd.jd - dt)
            jd2 = test_jd
            
            for _ in range(20):
                jd_mid = JulianDate((jd1.jd + jd2.jd) / 2)
                mid_alt = moon_altitude(observer, jd_mid).degrees
                
                if mid_alt < rise_altitude:
                    jd1 = jd_mid
                else:
                    jd2 = jd_mid
            
            result = JulianDate((jd1.jd + jd2.jd) / 2)
            
            if verbose:
                step(verbose, "Moonrise", f"JD = {result.jd:.6f}")
            
            return result
        
        prev_alt = curr_alt
    
    return None


def moonset(observer: Observer, jd: JulianDate,
            verbose: Optional[VerboseContext] = None) -> Optional[JulianDate]:
    """
    Calculate moonset time.
    
    Args:
        observer: Observer location
        jd: Julian Date (date of interest)
        verbose: Optional verbose context
        
    Returns:
        JulianDate of moonset or None if Moon doesn't set
    """
    # Set altitude accounting for refraction and Moon's angular size
    set_altitude = CONSTANTS.RISE_SET_ALTITUDE_MOON.value
    
    if verbose:
        step(verbose, "Set altitude", f"h₀ = {set_altitude}° (refraction + semidiameter)")
    
    # Start from local midnight
    jd_midnight = JulianDate(math.floor(jd.jd - 0.5) + 0.5 + observer.lon_deg / 360.0)
    
    # Search through the day
    dt = 0.01  # Search step in days (~15 min)
    
    prev_alt = moon_altitude(observer, jd_midnight).degrees
    
    for i in range(1, 150):  # Cover ~1.5 days
        test_jd = JulianDate(jd_midnight.jd + i * dt)
        curr_alt = moon_altitude(observer, test_jd).degrees
        
        # Check for setting (crossing from above to below horizon)
        if prev_alt >= set_altitude > curr_alt:
            # Refine with bisection
            jd1 = JulianDate(test_jd.jd - dt)
            jd2 = test_jd
            
            for _ in range(20):
                jd_mid = JulianDate((jd1.jd + jd2.jd) / 2)
                mid_alt = moon_altitude(observer, jd_mid).degrees
                
                if mid_alt >= set_altitude:
                    jd1 = jd_mid
                else:
                    jd2 = jd_mid
            
            result = JulianDate((jd1.jd + jd2.jd) / 2)
            
            if verbose:
                step(verbose, "Moonset", f"JD = {result.jd:.6f}")
            
            return result
        
        prev_alt = curr_alt
    
    return None


def next_phase(jd: JulianDate, phase: MoonPhase,
               verbose: Optional[VerboseContext] = None) -> JulianDate:
    """
    Find the next occurrence of a specific lunar phase.
    
    Args:
        jd: Starting Julian Date
        phase: The phase to find
        verbose: Optional verbose context
        
    Returns:
        JulianDate of the next occurrence of the phase
    """
    # Target phase angles
    phase_targets = {
        MoonPhase.NEW_MOON: 0,
        MoonPhase.FIRST_QUARTER: 90,
        MoonPhase.FULL_MOON: 180,
        MoonPhase.LAST_QUARTER: 270,
    }
    
    # For named phases, find the major ones
    if phase not in phase_targets:
        raise ValueError(f"Can only find major phases, not {phase.value}")
    
    target = phase_targets[phase]
    synodic = CONSTANTS.SYNODIC_MONTH.value
    
    if verbose:
        step(verbose, "Target phase", f"{phase.value} (D = {target}°)")
    
    # Get current elongation
    current = moon_mean_elongation(jd).degrees % 360
    
    # Calculate approximate days until target
    diff = (target - current) % 360
    days_approx = (diff / 360.0) * synodic
    
    if days_approx < 1:
        days_approx += synodic
    
    # Start searching from approximate time
    test_jd = JulianDate(jd.jd + days_approx - 2)
    
    # Refine with bisection
    prev_D = moon_mean_elongation(test_jd).degrees
    dt = 0.1
    
    for i in range(100):
        test_jd = JulianDate(test_jd.jd + dt)
        curr_D = moon_mean_elongation(test_jd).degrees
        
        # Check for crossing target
        # Handle wrap-around at 360/0
        crossed = False
        if target == 0:
            if prev_D > 350 and curr_D < 10:
                crossed = True
        else:
            if prev_D < target <= curr_D:
                crossed = True
        
        if crossed:
            # Refine
            jd1 = JulianDate(test_jd.jd - dt)
            jd2 = test_jd
            
            for _ in range(20):
                jd_mid = JulianDate((jd1.jd + jd2.jd) / 2)
                mid_D = moon_mean_elongation(jd_mid).degrees
                
                if target == 0:
                    if mid_D > 180:
                        jd1 = jd_mid
                    else:
                        jd2 = jd_mid
                else:
                    if mid_D < target:
                        jd1 = jd_mid
                    else:
                        jd2 = jd_mid
            
            result = JulianDate((jd1.jd + jd2.jd) / 2)
            
            if verbose:
                step(verbose, f"Next {phase.value}", f"JD = {result.jd:.6f}")
            
            return result
        
        prev_D = curr_D
    
    # Shouldn't reach here
    return JulianDate(jd.jd + synodic)


def lunar_distance_to_sun(jd: JulianDate, 
                          verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the angular distance between the Moon and Sun.
    
    Args:
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        Angular separation as an Angle
    """
    from astr0.core.sun import sun_position
    
    moon = moon_position(jd, verbose)
    sun = sun_position(jd, verbose)
    
    # Angular separation formula
    moon_ra = math.radians(moon.ra.degrees)
    moon_dec = math.radians(moon.dec.degrees)
    sun_ra = math.radians(sun.ra.degrees)
    sun_dec = math.radians(sun.dec.degrees)
    
    cos_sep = (math.sin(moon_dec) * math.sin(sun_dec) +
               math.cos(moon_dec) * math.cos(sun_dec) * 
               math.cos(moon_ra - sun_ra))
    
    separation = math.degrees(math.acos(max(-1, min(1, cos_sep))))
    
    if verbose:
        step(verbose, "Moon-Sun separation", f"θ = {separation:.2f}°")
    
    return Angle(degrees=separation)


# Emoji for moon phases
PHASE_EMOJI = {
    MoonPhase.NEW_MOON: "🌑",
    MoonPhase.WAXING_CRESCENT: "🌒",
    MoonPhase.FIRST_QUARTER: "🌓",
    MoonPhase.WAXING_GIBBOUS: "🌔",
    MoonPhase.FULL_MOON: "🌕",
    MoonPhase.WANING_GIBBOUS: "🌖",
    MoonPhase.LAST_QUARTER: "🌗",
    MoonPhase.WANING_CRESCENT: "🌘",
}
