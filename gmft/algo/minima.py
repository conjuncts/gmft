import math


def find_local_minima(points, with_endpoint=True):
    """
    Find local minima in a stepwise function defined by points.
    Each point is a tuple (x, y) where y is the function value at x.
    The function value remains constant between consecutive x values.
    
    Args:
        points: List of tuples (x, y) sorted by x coordinate
        with_endpoint: If True, return the endpoint of the minima as well
        
    Returns:
        List of tuples (x, y) representing local minima
        IF with_endpoint is True, then returns (p, pfreq, q). f(p) == pfreq in [p, q).
    """
    if len(points) < 2:
        return points
        
    minima = []
    n = len(points)
    
    # Check first point
    if points[0][1] <= points[1][1]:
        if with_endpoint:
            outcome = (*points[0], points[1][0])
        else:
            outcome = points[0]
        minima.append(outcome)
    
    # Check intermediate points
    for i in range(1, n-1):
        prev_y = points[i-1][1]
        curr_y = points[i][1]
        next_y = points[i+1][1]
        
        # Current point is a local minimum if:
        # 1. It's strictly less than the next value
        # 2. It's less than or equal to the previous value
        if curr_y <= prev_y and curr_y < next_y:
            if with_endpoint:
                outcome = (*points[i], points[i+1][0])
            else:
                outcome = points[i]
            minima.append(outcome)
            
    # Check last point
    if points[-1][1] <= points[-2][1]:
        if with_endpoint:
            minima.append((*points[-1], None))
        else:
            minima.append(points[-1])
        
    return minima
    

# Helper function to test the algorithm
def test_stepwise_minima():
    # Test case 1: Simple V shape
    points1 = [(0, 3), (1, 2), (5, 4)]
    assert (out := find_local_minima(points1)) == [(1, 2, 4)], out
    
    # Test case 2: Multiple minima
    points2 = [(0, 3), (1, 1), (2, 4), (3, 2), (40, 5)]
    assert (out := find_local_minima(points2)) == [(1, 1, 1), (3, 2, 37)], out
    
    # Test case 3: Flat sections
    points3 = [(0, 2), (2, 1), (4, 3)]
    assert (out := find_local_minima(points3)) == [(2, 1, 2)], out

    # Test case 4: simulate x^2
    points4 = [(i, i**2) for i in range(-10, 10)]
    assert (out := find_local_minima(points4)) == [(0, 0, 1)], out

    points4 = [(i, (i-5)**2 + 3) for i in range(10)]
    assert (out := find_local_minima(points4)) == [(5, 3, 1)], out

    # test case 5: cos(x)
    import math
    points5 = [(i, math.cos(i)) for i in range(10)]
    out = find_local_minima(points5)
    assert [p[0] for p in out] == [3, 9], points5 # close to pi, 3pi
    print("All test cases passed!")

    # test case 6: find local minimum, not just global minimum
    points6 = [(x, x**4 - 2 * x**2 + x) for x in [x/10 for x in range(-20, 20, 1)]]
    # minima are (-1.107, 0.837)
    out = find_local_minima(points6)
    assert [p[0] for p in out] == [-1.1, 0.8], out

# Run tests
# test_stepwise_minima()