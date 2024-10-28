

from gmft.algo.histogram import IntervalHistogram


def test_histogram_1():    
    # Test 1: Basic initialization
    hist = IntervalHistogram()
    assert len(hist.sorted_points) == 0, "Empty histogram should have no points"
    # assert len(hist.change_points) == 0, "Empty histogram should have no change points"

def test_histogram_2():
    # Test 2: Initialize with boundaries
    hist = IntervalHistogram(min_x=0, max_x=10)
    assert len(hist.sorted_points) == 2, "Should have two boundary points"
    assert hist.sorted_points[0] == (0, 0), "First point should be (0, 0)"
    assert hist.sorted_points[1] == (10, 0), "Second point should be (10, 0)"

def test_histogram_3():
    # Test 3: Basic interval addition
    hist = IntervalHistogram()
    hist.append((1, 5))
    assert len(hist.sorted_points) == 2, "Should have two points after adding interval"
    assert hist.sorted_points[0] == (1, 1), "Start point should have frequency 1"
    assert hist.sorted_points[1] == (5, 0), "End point should have frequency 0"

def test_histogram_4():
    # Test 4: Overlapping intervals
    hist = IntervalHistogram()
    hist.append((1, 5))
    hist.append((3, 7))
    expected_points = [(1, 1), (3, 2), (5, 1), (7, 0)]
    assert hist.sorted_points == expected_points, f"Expected {expected_points}, got {hist.sorted_points}"

def test_histogram_5():
    # Test 5: Frequency queries
    hist = IntervalHistogram()
    hist.append((1, 5))
    hist.append((3, 7))
    test_points = [
        (0, 0),  # Before all intervals
        (2, 1),  # Inside first interval only
        (4, 2),  # Inside both intervals
        (6, 1),  # Inside second interval only
        (8, 0),  # After all intervals
    ]
    for point, expected_freq in test_points:
        assert hist.frequency(point) == expected_freq, f"Expected frequency {expected_freq} at point {point}, got {hist.frequency(point)}"

def test_histogram_6():
    # Test 6: Edge cases
    hist = IntervalHistogram()
    hist.append((1, 2))
    hist.append((2, 3))  # Adjacent intervals
    assert hist.frequency(2) == 1, "Point at interval boundary should belong to second interval only"

def test_histogram_7():
    # Test 7: Error cases
    hist = IntervalHistogram()
    try:
        hist.append((5, 3))  # Start > end
        assert False, "Should raise ValueError for invalid interval"
    except ValueError:
        pass

def test_histogram_empty():
    # Test 7b: empty cases
    hist = IntervalHistogram()
    assert hist.frequency(1) == 0, "Frequency of point before all intervals should be 0"
    hist.append((1, 1))
    hist.append((1, 1))
    assert hist.frequency(1) == 0, "Intervals [1, 1) have measure 0 and should have no effect"

def test_histogram_8():
    # Test 8: Multiple overlapping intervals
    hist = IntervalHistogram()
    intervals = [(1, 5), (2, 6), (3, 7), (4, 8)]
    max_freq = 0
    for interval in intervals:
        hist.append(interval)
        max_freq += 1
        assert max(point[1] for point in hist.sorted_points) == max_freq, f"Maximum frequency should be {max_freq}"

    # Test 9: Binary search edge cases
    hist = IntervalHistogram()
    hist.append((1, 5))
    assert hist.get_index_before_or_equal(0) == -1, "Should return -1 for point before all intervals"
    assert hist.get_index_before_or_equal(6) == 1, "Should return last index for point after all intervals"
    assert hist.get_index_after(6) == 2, "Should return length for point after all intervals"

    # Test 10: Non-overlapping intervals
    hist = IntervalHistogram()
    intervals = [(1, 2), (3, 4), (5, 6), (7, 8)]
    max_freq = 0
    for interval in intervals:
        hist.append(interval)
    expected_points = [(1, 1), (2, 0), (3, 1), (4, 0), (5, 1), (6, 0), (7, 1), (8, 0)]
    assert hist.sorted_points == expected_points, f"Expected {expected_points}, got {hist.sorted_points}"

