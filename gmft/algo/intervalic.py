from collections import defaultdict
from bisect import bisect_right

class IntervalHistogram:
    """
    Class that keeps track of a histogram of intervals.
    For any point x, the frequency at x is the number of intervals that contain x.
    Internally, the histogram is stored as a list of key points, which is represented by a tuple (p, p_freq).
    For 2 consecutive key points (p, p_freq) and (q, q_freq), the frequency of all points in the interval [p, q) is p_freq.
    By convention, the end key-point of the entire histogram is (max_x, 0). 
    """
    def __init__(self, min_x=None, max_x=None):
        # Store points and their cumulative frequencies
        self.sorted_points = [] 
        """List of (point, frequency) tuples"""

        self.height = 0
        """The maximum frequency in the histogram"""
        
        # Initialize with boundary points if provided
        if min_x is not None:
            self.sorted_points.append((min_x, 0))
        if max_x is not None:
            self.sorted_points.append((max_x, 0))

    def get_index_before_or_equal(self, point):
        """
        Return the index of the last change point that is <= the query point.
        If no such point exists, return -1.
        """
        idx = bisect_right(self.sorted_points, point, key=lambda x: x[0]) - 1
        return idx

    def get_index_after(self, point):
        """
        Return the index of the first change point that is strictly > the query point.
        If no such point exists, return len(self.sorted_points).
        """
        return bisect_right(self.sorted_points, point, key=lambda x: x[0])

    def frequency(self, point):
        """
        Return the frequency of the point in the histogram.
        We compute this by finding the last change point before or at the query point
        and returning its associated frequency.
        """
        idx = self.get_index_before_or_equal(point)
        if idx == -1:
            return 0
        return self.sorted_points[idx][1]

    def append(self, interval):
        """
        Adds the interval [p, q) to the histogram.
        We modify the frequency change points at the start and end of the interval.
        
        Edge cases: [p, p) is considered empty. Adding it will have no effect. (no dirac delta allowed.)
        """
        start, end = interval
        if end < start:
            raise ValueError('invalid interval')
        if start == end:
            return

        end_freq = self.frequency(end) # before all else, measure end freq
        
        # Handle start point
        start_idx = self.get_index_before_or_equal(start)
        if 0 <= start_idx < len(self.sorted_points):
            start_freq = self.sorted_points[start_idx][1]
        else:
            start_freq = 0
        if start_idx >= 0 and self.sorted_points[start_idx][0] == start:
            # Point exists, just update frequency
            self.sorted_points[start_idx] = (start, start_freq + 1)
        else:
            # Insert new point with frequency increment
            start_idx += 1
            self.sorted_points.insert(start_idx, (start, start_freq + 1))
        
        if start_freq + 1 > self.height:
            self.height = start_freq + 1
        
        # Handle end point
        end_idx = self.get_index_before_or_equal(end)
        if end_idx >= 0 and self.sorted_points[end_idx][0] == end:
            pass
        else:
            # Insert new point with same frequency as before
            end_idx += 1
            self.sorted_points.insert(end_idx, (end, end_freq))
        
        # increase all frequencies in between
        for i in range(start_idx+1, end_idx):
            # self.sorted_points[i][1] += 1
            self.sorted_points[i] = (self.sorted_points[i][0], self.sorted_points[i][1] + 1)

    def __str__(self):
        """Return a string representation of the histogram."""
        return f"IntervalHistogram(points={self.sorted_points})"
    
    def iter_intervals_below(self, threshold):
        """
        Yields all the intervals [p, q) such that for all x in [p, q), frequency(x) <= threshold.
        Note that this will merge consecutive intervals, even if they have different frequencies, as long as they are all <= threshold.

        Yields intervals of [p, q).
        """
        if not self.sorted_points:
            return
            
        current_start = None  # Start of the current interval
        for i in range(len(self.sorted_points)):
            point, freq = self.sorted_points[i]
            
            # If frequency is <= threshold and we haven't started an interval
            if freq <= threshold:
                if current_start is None and i < len(self.sorted_points) - 1: # don't start an interval at the global end point
                    current_start = point
            # If frequency > threshold and we have an open interval
            else:
                if current_start is not None:
                    yield (current_start, point)
                    current_start = None
                
        # Handle the last point specially if we have an open interval
        if current_start is not None:
            yield (current_start, point)
    

