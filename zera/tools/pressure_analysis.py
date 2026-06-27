from typing import List

def detect_pressure_rebound(time_series: List[float]) -> bool:
    """
    Detects pressure rebound from a time-series of readings.
    A rebound is defined as pressure initially decreasing and then increasing.
    """
    if not time_series or len(time_series) < 3:
        return False
        
    has_decreased = False
    
    for i in range(1, len(time_series)):
        diff = time_series[i] - time_series[i-1]
        
        # Pressure is decreasing
        if diff < -0.1:
            has_decreased = True
            
        # Pressure is increasing after it has decreased
        elif diff > 0.1 and has_decreased:
            return True
            
    return False
