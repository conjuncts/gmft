## k-means

Note that LTA is theoretically equivalent to one round of k-means clustering
in the 1-dimensional case with an initial guess of equally spaced centroids, 
and with centroid merging.

That is, when bboxes are regularized so that there are no gaps or overlap between consecutive 
rows/columns (that is, for example, y_end = y_start for consecutive rows), AND such that the
rows/columns are even (that is, for example, x_start = x_start for every row), 

then for any textbox, the row/column with the highest intersection is exactly the row/column where
the center of the textbox resides. 


## indices

Indices convention:

"good" intervals are projections of the cell bboxes (onto either the x or y axis) - that is, they describe where text reside.
Index 0 is the first row, etc.

"dividers" only describe dividers between rows. 

But to match the indexing scheme of "good", index 0 is still the first row.

So (with endpoints included) the row at index $i$ is described by the partitions $i$ and $i+1$.

The new partitions code has the convention where dividers do indeed include endpoints. But the previous DITR does not have this convention.
When in doubt, if table_bbox is passed in, then it follows the old convention.

## normalize

We call "Normalize" 

- In pandas and polars, json_normalize is used to convert heterogenous data into a flat table. 

In the same way, normalize_x creates a flat table by taking merged cells and reduplicating values to create a flat, homogenous table.
The behavior is most similar to `explode()`, where a hierarchical 