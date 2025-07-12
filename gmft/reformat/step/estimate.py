from typing import List
import numpy as np

from gmft.core.schema import TableTextBbox, TextBbox
from gmft.formatters.base import FormattedTable


def _estimate_count_lines_kmeans(
    words: List[TextBbox], _merge_hyperparam=0.6
) -> int:
    """
    Estimate the height of a row (in lines) using k-means clustering.

    Overview of algorithm:
    1. Take y_avg for each word.
    2. Take avg_y_height.
    3. Initialize centroids with y values spaced evenly between min and max y values, with a spacing of avg_y_height.
    4. Run k-means.
    5. Merge clusters that are too close to each other (config._large_table_merge_distance), which is 0.6 * avg_y_height
    6. (Repeat once for good measure)
    7. Count number of remaining clusters.
    8. Return the estimated row height (in lines) based on the number of clusters.
    """
    if not words:
        return 0.0

    # Step 1: Take y_avg for each word
    y_avgs = [(word["ymin"] + word["ymax"]) / 2 for word in words]

    # Step 2: Take avg_y_height
    y_heights = [word["ymax"] - word["ymin"] for word in words]
    avg_y_height = np.mean(y_heights) if y_heights else 1.0

    # Step 3: Initialize centroids with y values spaced evenly between min and max y values
    min_y = min(y_avgs)
    max_y = max(y_avgs)

    if min_y == max_y:
        return 1

    # Estimate number of clusters based on the range and average height
    # estimated_clusters = max(1, int((max_y - min_y) / avg_y_height))

    # Initialize centroids evenly spaced
    centroids = np.arange(
        min_y, max_y + avg_y_height, avg_y_height
    )  # [:estimated_clusters]

    if len(centroids) <= 1:
        return 1

    # Step 4: Run k-means (simple implementation)
    y_avgs_array = np.array(y_avgs)

    for _ in range(2):  # Just 2 iterations with good initial guess
        # Assign points to nearest centroid
        distances = np.abs(y_avgs_array[:, np.newaxis] - centroids)
        assignments = np.argmin(distances, axis=1)

        # Update centroids
        new_centroids = []
        for i in range(len(centroids)):
            cluster_points = y_avgs_array[assignments == i]
            if len(cluster_points) > 0:
                new_centroids.append(np.mean(cluster_points))
            # let centroids disappear
            # else:
            #     new_centroids.append(centroids[i])

        new_centroids = np.array(new_centroids)

        # No need to check for convergence - it typically converges very fast
        # if np.allclose(centroids, new_centroids):
        #     break

        centroids = new_centroids

    # Step 5: Merge clusters that are too close to each other
    merge_distance = _merge_hyperparam * avg_y_height

    # Sort centroids
    centroids = np.sort(centroids)

    # Merge close clusters
    i = 1
    while i < len(centroids):
        if abs(centroids[i] - centroids[i - 1]) < merge_distance:
            # Merge by averaging
            centroids[i - 1] = (centroids[i - 1] + centroids[i]) / 2
            centroids = np.delete(centroids, i)
        else:
            i += 1

    # Step 7: Count number of remaining clusters
    num_clusters = len(centroids)

    # Return the estimated row height (in lines) based on the number of clusters
    return num_clusters


def _estimate_row_height_kmeans_all(
    words: List[TableTextBbox], _merge_hyperparam=0.6
) -> float:
    row_indices = set(x["row_idx"] for x in words)
    collector = {}
    for idx in row_indices:
        subset = [w for w in words if w["row_idx"] == idx]
        collector[idx] = _estimate_count_lines_kmeans(subset, _merge_hyperparam)
    return collector
