Note that LTA is theoretically equivalent to one round of k-means clustering
in the 1-dimensional case with an initial guess of equally spaced centroids, 
and with centroid merging.

That is, when bboxes are regularized so that there are no gaps or overlap between consecutive 
rows/columns (that is, for example, y_end = y_start for consecutive rows), AND such that the
rows/columns are even (that is, for example, x_start = x_start for every row), 

then for any textbox, the row/column with the highest intersection is exactly the row/column where
the center of the textbox resides. 