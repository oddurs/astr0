"""
Solar position and event calculations.

Implements solar position using the algorithm from Meeus, "Astronomical Algorithms".
Provides sunrise, sunset, twilight times, and solar position calculations.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

from astr0.core.angles import Angle
from astr0.core.time import JulianDate, jd_now
from astr0.core.coords import ICRSCoord
from astr0.core.observer import Observer
from astr0.core.constants import CONSTANTS
from astr0.verbose import VerboseContext, step


@dataclass(frozen=True)
class SunPosition:
    """Solar position at a given instant."""
    
    # Ecliptic coordinates
    longitude: Angle  # Apparent ecliptic longitude
    latitude: Angle   # Ecliptic latitude (nearly zero for Sun)
    
    # Equatorial coordinates
    ra: Angle         # Right Ascension
    dec: Angle        # Declination
    
    # Distance
    distance_au: float  # Earth-Sun distance in AU
    
    # Additional parameters
    equation_of_time: float  # Minutes
    
    def to_icrs(self) -> ICRSCoord:
        """Convert to ICRS coordinate."""
        return ICRSCoord(ra=self.ra, dec=self.dec)


def sun_mean_longitude(jd: JulianDate, verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the Sun's geometric mean longitude.
    
    Args:
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        Mean longitude as Angle
    """
    T = jd.t_j2000
    
    # Meeus equation 25.2
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
    
    step(verbose, "Sun mean longitude",
         f"L₀ = 280.46646 + 36000.76983·T + 0.0003032·T²\n"
         f"T = {T:.10f} centuries\n"
         f"L₀ = {L0:.6f}°")
    
    return Angle(degrees=L0).normalize()


def sun_mean_anomaly(jd: JulianDate, verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the Sun's mean anomaly.
    
    Args:
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        Mean anomaly as Angle
    """
    T = jd.t_j2000
    
    # Meeus equation 25.3
    M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
    
    step(verbose, "Sun mean anomaly",
         f"M = 357.52911 + 35999.05029·T - 0.0001537·T²\n"
         f"M = {M:.6f}°")
    
    return Angle(degrees=M).normalize()


def earth_eccentricity(jd: JulianDate) -> float:
    """Calculate Earth's orbit eccentricity."""
    T = jd.t_j2000
    return 0.016708634 - 0.000042037 * T - 0.0000001267 * T * T


def sun_equation_of_center(jd: JulianDate, verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the equation of center for the Sun.
    
    Args:
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        Equation of center as Angle
    """
    T = jd.t_j2000
    M = sun_mean_anomaly(jd)
    M_rad = M.radians
    
    # Meeus equation 25.4
    C = ((1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M_rad) +
         (0.019993 - 0.000101 * T) * math.sin(2 * M_rad) +
         0.000289 * math.sin(3 * M_rad))
    
    step(verbose, "Equation of center",
         f"C = (1.9146 - 0.0048·T)·sin(M) + 0.0200·sin(2M) + 0.0003·sin(3M)\n"
         f"C = {C:.6f}°")
    
    return Angle(degrees=C)


def sun_true_longitude(jd: JulianDate, verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the Sun's true geometric longitude.
    
    Args:
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        True longitude as Angle
    """
    L0 = sun_mean_longitude(jd, verbose)
    C = sun_equation_of_center(jd, verbose)
    
    true_lon = L0.degrees + C.degrees
    
    step(verbose, "Sun true longitude",
         f"☉ = L₀ + C = {L0.degrees:.6f}° + {C.degrees:.6f}° = {true_lon:.6f}°")
    
    return Angle(degrees=true_lon).normalize()


def sun_apparent_longitude(jd: JulianDate, verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the Sun's apparent longitude (corrected for nutation and aberration).
    
    Args:
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        Apparent longitude as Angle
    """
    true_lon = sun_true_longitude(jd, verbose)
    T = jd.t_j2000
    
    # Longitude of ascending node of Moon's mean orbit
    omega = 125.04 - 1934.136 * T
    
    # Correction for nutation and aberration
    correction = -0.00569 - 0.00478 * math.sin(math.radians(omega))
    
    apparent = true_lon.degrees + correction
    
    step(verbose, "Apparent longitude",
         f"Ω = {omega:.4f}°\n"
         f"Correction = -0.00569 - 0.00478·sin(Ω) = {correction:.6f}°\n"
         f"λ = {apparent:.6f}°")
    
    return Angle(degrees=apparent).normalize()


def mean_obliquity(jd: JulianDate, verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the mean obliquity of the ecliptic.
    
    Args:
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        Mean obliquity as Angle
    """
    T = jd.t_j2000
    
    # Meeus equation 22.2 (in arcseconds, then convert)
    eps0_arcsec = (84381.448 - 46.8150 * T - 0.00059 * T * T + 0.001813 * T * T * T)
    eps0 = eps0_arcsec / 3600.0
    
    step(verbose, "Mean obliquity",
         f"ε₀ = 84381.448 - 46.815·T - 0.00059·T² + 0.00181·T³\n"
         f"ε₀ = {eps0_arcsec:.3f}\" = {eps0:.6f}°")
    
    return Angle(degrees=eps0)


def true_obliquity(jd: JulianDate, verbose: Optional[VerboseContext] = None) -> Angle:
    """
    Calculate the true obliquity of the ecliptic (with nutation).
    
    Args:
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        True obliquity as Angle
    """
    eps0 = mean_obliquity(jd, verbose)
    T = jd.t_j2000
    
    # Simplified nutation in obliquity
    omega = 125.04 - 1934.136 * T
    delta_eps = 0.00256 * math.cos(math.radians(omega))
    
    eps = eps0.degrees + delta_eps
    
    step(verbose, "True obliquity",
         f"Δε = 0.00256·cos(Ω) = {delta_eps:.6f}°\n"
         f"ε = ε₀ + Δε = {eps:.6f}°")
    
    return Angle(degrees=eps)


def sun_distance(jd: JulianDate, verbose: Optional[VerboseContext] = None) -> float:
    """
    Calculate Earth-Sun distance in AU.
    
    Args:
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        Distance in AU
    """
    T = jd.t_j2000
    M = sun_mean_anomaly(jd)
    e = earth_eccentricity(jd)
    
    # True anomaly
    C = sun_equation_of_center(jd)
    v = M.degrees + C.degrees
    
    # Distance (Meeus equation 25.5)
    R = (1.000001018 * (1 - e * e)) / (1 + e * math.cos(math.radians(v)))
    
    step(verbose, "Sun distance",
         f"e = {e:.9f}\n"
         f"v = M + C = {v:.6f}°\n"
         f"R = a(1-e²)/(1+e·cos(v)) = {R:.9f} AU")
    
    return R


def equation_of_time(jd: JulianDate, verbose: Optional[VerboseContext] = None) -> float:
    """
    Calculate the equation of time.
    
    The equation of time is the difference between apparent solar time
    and mean solar time, in minutes.
    
    Args:
        jd: Julian Date
        verbose: Optional verbose context
        
    Returns:
        Equation of time in minutes
    """
    T = jd.t_j2000
    
    L0 = sun_mean_longitude(jd).radians
    M = sun_mean_anomaly(jd).radians
    e = earth_eccentricity(jd)
    eps = mean_obliquity(jd).radians
    
    y = math.tan(eps / 2) ** 2
    
    # Equation of time formula
    E = (y * math.sin(2 * L0) 
         - 2 * e * math.sin(M) 
         + 4 * e * y * math.sin(M) * math.cos(2 * L0)
         - 0.5 * y * y * math.sin(4 * L0)
         - 1.25 * e * e * math.sin(2 * M))
    
    # Convert to minutes (radians to degrees, then to time)
    E_minutes = math.degrees(E) * 4
    
    step(verbose, "Equation of time",
         f"y = tan²(ε/2) = {y:.9f}\n"
         f"E = {E:.9f} rad = {E_minutes:.2f} minutes")
    
    return E_minutes


def sun_position(jd: Optional[JulianDate] = None, verbose: Optional[VerboseContext] = None) -> SunPosition:
    """
    Calculate the Sun's position at a given time.
    
    Args:
        jd: Julian Date (default: now)
        verbose: Optional verbose context
        
    Returns:
        SunPosition with all solar parameters
    """
    if jd is None:
        jd = jd_now()
    
    step(verbose, "Sun position calculation",
         f"JD = {jd.jd:.6f}\n"
         f"T = {jd.t_j2000:.10f} centuries since J2000.0")
    
    # Calculate ecliptic longitude
    lon = sun_apparent_longitude(jd, verbose)
    lat = Angle(degrees=0)  # Sun's ecliptic latitude is essentially 0
    
    # Calculate obliquity
    eps = true_obliquity(jd, verbose)
    
    # Convert to equatorial coordinates
    lon_rad = lon.radians
    eps_rad = eps.radians
    
    # Right Ascension
    ra_rad = math.atan2(
        math.cos(eps_rad) * math.sin(lon_rad),
        math.cos(lon_rad)
    )
    ra = Angle(radians=ra_rad).normalize()
    
    # Declination
    dec_rad = math.asin(math.sin(eps_rad) * math.sin(lon_rad))
    dec = Angle(radians=dec_rad)
    
    step(verbose, "Equatorial coordinates",
         f"α = atan2(cos(ε)·sin(λ), cos(λ))\n"
         f"α = {ra.to_hms()}\n"
         f"δ = asin(sin(ε)·sin(λ))\n"
         f"δ = {dec.to_dms()}")
    
    # Distance
    R = sun_distance(jd, verbose)
    
    # Equation of time
    E = equation_of_time(jd, verbose)
    
    return SunPosition(
        longitude=lon,
        latitude=lat,
        ra=ra,
        dec=dec,
        distance_au=R,
        equation_of_time=E
    )


def _hour_angle_rise_set(
    dec: Angle,
    latitude: Angle,
    altitude: float,
    verbose: Optional[VerboseContext] = None
) -> Optional[Angle]:
    """
    Calculate the hour angle when an object is at a given altitude.
    
    Args:
        dec: Object declination
        latitude: Observer latitude
        altitude: Target altitude in degrees
        verbose: Optional verbose context
        
    Returns:
        Hour angle as Angle, or None if object never reaches altitude
    """
    lat_rad = latitude.radians
    dec_rad = dec.radians
    alt_rad = math.radians(altitude)
    
    cos_H = (math.sin(alt_rad) - math.sin(lat_rad) * math.sin(dec_rad)) / (
        math.cos(lat_rad) * math.cos(dec_rad)
    )
    
    step(verbose, "Hour angle calculation",
         f"cos(H) = (sin(h₀) - sin(φ)·sin(δ)) / (cos(φ)·cos(δ))\n"
         f"cos(H) = (sin({altitude}°) - sin({latitude.degrees:.4f}°)·sin({dec.degrees:.4f}°)) / "
         f"(cos({latitude.degrees:.4f}°)·cos({dec.degrees:.4f}°))\n"
         f"cos(H) = {cos_H:.6f}")
    
    # Check if object never rises or never sets
    if cos_H < -1:
        step(verbose, "Result", "cos(H) < -1: Object is always above this altitude (circumpolar)")
        return None  # Always above altitude
    if cos_H > 1:
        step(verbose, "Result", "cos(H) > 1: Object never reaches this altitude")
        return None  # Never reaches altitude
    
    H = math.degrees(math.acos(cos_H))
    
    step(verbose, "Result", f"H = acos({cos_H:.6f}) = {H:.4f}°")
    
    return Angle(degrees=H)


def _solar_transit(
    jd: JulianDate,
    longitude: Angle,
    verbose: Optional[VerboseContext] = None
) -> JulianDate:
    """
    Calculate the Julian Date of solar transit (solar noon).
    
    Args:
        jd: Julian Date (approximate date)
        longitude: Observer longitude
        verbose: Optional verbose context
        
    Returns:
        JD of solar transit
    """
    # Get integer JD at 0h UT
    jd0 = JulianDate(math.floor(jd.jd - 0.5) + 0.5)
    
    # Sun position at transit (approximate)
    sun = sun_position(jd0)
    
    # Equation of time in days
    E_days = sun.equation_of_time / (60 * 24)
    
    # Transit time (fraction of day)
    transit = 0.5 - longitude.degrees / 360 - E_days
    
    # Normalize to [0, 1)
    while transit < 0:
        transit += 1
    while transit >= 1:
        transit -= 1
    
    result = JulianDate(jd0.jd + transit)
    
    step(verbose, "Solar transit",
         f"JD₀ = {jd0.jd:.1f}\n"
         f"E = {sun.equation_of_time:.2f} min = {E_days:.6f} days\n"
         f"Transit = 0.5 - λ/360 - E = {transit:.6f}\n"
         f"JD_transit = {result.jd:.6f}")
    
    return result


def sunrise(
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None
) -> Optional[JulianDate]:
    """
    Calculate sunrise time for an observer.
    
    Args:
        observer: Observer location
        jd: Julian Date (default: today)
        verbose: Optional verbose context
        
    Returns:
        JD of sunrise, or None if sun doesn't rise
    """
    if jd is None:
        jd = jd_now()
    
    step(verbose, "Sunrise calculation",
         f"Observer: {observer.name}\n"
         f"Latitude: {observer.lat_deg:.4f}°\n"
         f"Longitude: {observer.lon_deg:.4f}°\n"
         f"Date: JD {jd.jd:.2f}")
    
    # Solar noon
    transit = _solar_transit(jd, observer.longitude, verbose)
    
    # Sun position at transit
    sun = sun_position(transit, verbose)
    
    # Hour angle at sunrise (altitude = -0.8333°)
    H = _hour_angle_rise_set(
        sun.dec, 
        observer.latitude, 
        CONSTANTS.RISE_SET_ALTITUDE_SUN.value,
        verbose
    )
    
    if H is None:
        return None
    
    # Sunrise is transit minus hour angle (in days)
    H_days = H.degrees / 360
    result = JulianDate(transit.jd - H_days)
    
    step(verbose, "Sunrise result",
         f"Transit: JD {transit.jd:.6f}\n"
         f"H = {H.degrees:.4f}° = {H_days:.6f} days\n"
         f"Sunrise: JD {result.jd:.6f} = {result.to_datetime()}")
    
    return result


def sunset(
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None
) -> Optional[JulianDate]:
    """
    Calculate sunset time for an observer.
    
    Args:
        observer: Observer location
        jd: Julian Date (default: today)
        verbose: Optional verbose context
        
    Returns:
        JD of sunset, or None if sun doesn't set
    """
    if jd is None:
        jd = jd_now()
    
    step(verbose, "Sunset calculation",
         f"Observer: {observer.name}\n"
         f"Date: JD {jd.jd:.2f}")
    
    # Solar noon
    transit = _solar_transit(jd, observer.longitude, verbose)
    
    # Sun position at transit
    sun = sun_position(transit, verbose)
    
    # Hour angle at sunset (altitude = -0.8333°)
    H = _hour_angle_rise_set(
        sun.dec,
        observer.latitude,
        CONSTANTS.RISE_SET_ALTITUDE_SUN.value,
        verbose
    )
    
    if H is None:
        return None
    
    # Sunset is transit plus hour angle (in days)
    H_days = H.degrees / 360
    result = JulianDate(transit.jd + H_days)
    
    step(verbose, "Sunset result",
         f"Transit: JD {transit.jd:.6f}\n"
         f"H = {H.degrees:.4f}° = {H_days:.6f} days\n"
         f"Sunset: JD {result.jd:.6f} = {result.to_datetime()}")
    
    return result


def solar_noon(
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None
) -> JulianDate:
    """
    Calculate solar noon (transit) time for an observer.
    
    Args:
        observer: Observer location
        jd: Julian Date (default: today)
        verbose: Optional verbose context
        
    Returns:
        JD of solar noon
    """
    if jd is None:
        jd = jd_now()
    
    return _solar_transit(jd, observer.longitude, verbose)


def _twilight_time(
    observer: Observer,
    jd: JulianDate,
    altitude: float,
    is_morning: bool,
    verbose: Optional[VerboseContext] = None
) -> Optional[JulianDate]:
    """Calculate twilight time for a given altitude threshold."""
    transit = _solar_transit(jd, observer.longitude, verbose)
    sun = sun_position(transit)
    
    H = _hour_angle_rise_set(sun.dec, observer.latitude, altitude, verbose)
    
    if H is None:
        return None
    
    H_days = H.degrees / 360
    
    if is_morning:
        return JulianDate(transit.jd - H_days)
    else:
        return JulianDate(transit.jd + H_days)


def civil_twilight(
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None
) -> Tuple[Optional[JulianDate], Optional[JulianDate]]:
    """
    Calculate civil twilight times (Sun at -6°).
    
    Args:
        observer: Observer location
        jd: Julian Date (default: today)
        verbose: Optional verbose context
        
    Returns:
        Tuple of (morning_twilight, evening_twilight) JDs
    """
    if jd is None:
        jd = jd_now()
    
    morning = _twilight_time(observer, jd, -6.0, True, verbose)
    evening = _twilight_time(observer, jd, -6.0, False, verbose)
    
    return (morning, evening)


def nautical_twilight(
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None
) -> Tuple[Optional[JulianDate], Optional[JulianDate]]:
    """
    Calculate nautical twilight times (Sun at -12°).
    
    Args:
        observer: Observer location
        jd: Julian Date (default: today)
        verbose: Optional verbose context
        
    Returns:
        Tuple of (morning_twilight, evening_twilight) JDs
    """
    if jd is None:
        jd = jd_now()
    
    morning = _twilight_time(observer, jd, -12.0, True, verbose)
    evening = _twilight_time(observer, jd, -12.0, False, verbose)
    
    return (morning, evening)


def astronomical_twilight(
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None
) -> Tuple[Optional[JulianDate], Optional[JulianDate]]:
    """
    Calculate astronomical twilight times (Sun at -18°).
    
    Args:
        observer: Observer location
        jd: Julian Date (default: today)
        verbose: Optional verbose context
        
    Returns:
        Tuple of (morning_twilight, evening_twilight) JDs
    """
    if jd is None:
        jd = jd_now()
    
    morning = _twilight_time(observer, jd, -18.0, True, verbose)
    evening = _twilight_time(observer, jd, -18.0, False, verbose)
    
    return (morning, evening)


def solar_altitude(
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None
) -> Angle:
    """
    Calculate the current solar altitude for an observer.
    
    Args:
        observer: Observer location
        jd: Julian Date (default: now)
        verbose: Optional verbose context
        
    Returns:
        Solar altitude as Angle
    """
    if jd is None:
        jd = jd_now()
    
    sun = sun_position(jd, verbose)
    coord = sun.to_icrs()
    
    # Convert to horizontal coordinates
    horiz = coord.to_horizontal(
        jd,
        observer.latitude,
        observer.longitude,
        verbose
    )
    
    return horiz.alt


def day_length(
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None
) -> Optional[float]:
    """
    Calculate the length of the day in hours.
    
    Args:
        observer: Observer location
        jd: Julian Date (default: today)
        verbose: Optional verbose context
        
    Returns:
        Day length in hours, or None if sun doesn't rise/set
    """
    if jd is None:
        jd = jd_now()
    
    rise = sunrise(observer, jd, verbose)
    set_ = sunset(observer, jd, verbose)
    
    if rise is None or set_ is None:
        return None
    
    # Difference in days, convert to hours
    length_hours = (set_.jd - rise.jd) * 24
    
    step(verbose, "Day length",
         f"Sunrise: JD {rise.jd:.6f}\n"
         f"Sunset: JD {set_.jd:.6f}\n"
         f"Length: {length_hours:.2f} hours")
    
    return length_hours
