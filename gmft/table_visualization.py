# Original author is Niels Rogge, source: https://github.com/NielsRogge/Transformers-Tutorials/blob/master/Table%20Transformer/Using_Table_Transformer_for_table_detection_and_table_structure_recognition.ipynb


import matplotlib.pyplot as plt


# colors for visualization
colors = {-1: "red", 0: "red", 1: "blue", 2: "green", 3: "yellow", 4: "orange", 5: "violet"}



def plot_results_unwr(pil_img, confidence, labels, boxes, id2label, filter=None, figsize=(32,20),
                      padding=None, margin=None, linewidth=3,
                      show_labels=True, return_img=False): # prob, boxes):
    """
    Helper method to visualize the results of the table detection/format model.
    
    :param pil_img: PIL image
    :param confidence: list of floats, confidence scores
    :param labels: list of integers, class labels
    :param boxes: list of lists, bounding boxes in the format [xmin, ymin, xmax, ymax]
    :param id2label: dictionary, mapping class labels (int) to class names
    :param filter: list of integers, class labels to selectively display
    :param figsize: tuple, figure size. None for a smaller size
    :param show_labels: boolean, whether to display the class labels
    
    **Example**::

        confidence = [0.993, 0.927]
        labels = [0, 0]  # 0 is the table class
        boxes = [
            [0.000, 0.000, 70.333, 20.333],  # bounding boxes: xmin, ymin, xmax, ymax
            [10.001, 0.001, 0.998, 0.998]
        ]
    """
    # confidence = results["scores"].tolist()
    # labels = results["labels"].tolist()
    # boxes = results["boxes"].tolist()
    if id2label is None:
        id2label = {0: "table", 1: "table rotated"}

    
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(pil_img)
    
    for cl, lbl, (xmin, ymin, xmax, ymax) in zip(confidence, labels, boxes):
        # cl = p.argmax()
        if padding is not None:
            xmin += padding[0]
            ymin += padding[1]
            xmax += padding[0]
            ymax += padding[1]
        if margin is not None:
            xmin += margin[0]
            ymin += margin[1]
            xmax += margin[0]
            ymax += margin[1]
            
        if filter is not None and lbl not in filter:
            continue
        ax.add_patch(plt.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin,
                                   fill=False, color=colors[lbl], linewidth=linewidth))
        if lbl != -1 and show_labels:
            text = f'{id2label[lbl]}: {cl:0.2f}'
            ax.text(xmin, ymin, text, fontsize=15,
                    bbox=dict(facecolor='yellow', alpha=0.5))
    plt.axis('off')
    
    if return_img:
        import io
        from PIL import Image
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img = Image.open(buf)
        
        plt.close(fig)
        return img
    plt.show()
    

# colors for visualization
COLORS = [[0.000, 0.447, 0.741], [0.850, 0.325, 0.098], [0.929, 0.694, 0.125],
          [0.494, 0.184, 0.556], [0.466, 0.674, 0.188], [0.301, 0.745, 0.933]]
COLORS = [(int(r * 255), int(g * 255), int(b * 255)) for r, g, b in COLORS]

# id2label
from PIL import Image, ImageDraw

def plot_shaded_boxes(pil_img, labels: list[int], boxes: list[tuple[float, float, float, float]], 
                      id2color: dict = None, filter=None, alpha=0.2, 
                      id2border: dict = None):
    """
    Helper method to visualize the results of the table detection/format model using PIL.

    :param pil_img: PIL image
    :param labels: list of integers, class labels
    :param boxes: list of tuples, bounding boxes in the format [xmin, ymin, xmax, ymax]
    :param id2color: dictionary, mapping class labels (int) to desired color
    :param filter: list of integers, class labels to selectively display
    :param alpha: float, transparency for the box fill (0 to 1)
    """
    
    # Create a drawing context
    draw = ImageDraw.Draw(pil_img, 'RGBA')
    
    # Loop over the labels and corresponding boxes
    for label, (xmin, ymin, xmax, ymax) in zip(labels, boxes):
        if filter is not None and label not in filter:
            continue
        
        # Determine the color based on id2color or a fallback (if no mapping provided)
        if id2color is None:
            # Fallback to a set of default colors (e.g., repeating colors based on label index)
            c = (*tuple(COLORS[label % len(COLORS)]), int(255 * alpha))  # Red as a default with transparency
        else:
            # Use the color from id2color (could be a string like 'red' or a tuple)
            c = id2color.get(label, (255, 0, 0, int(255 * alpha)))  # Default red if key missing
            if isinstance(c, str):
                # Convert string color names to RGB with transparency if needed
                from PIL import ImageColor
                c = ImageColor.getrgb(c) + (int(255 * alpha),)
        
        if id2border is None:
            id2border = {5: (0, 0, 255, 80)}
        border = id2border.get(label, (255, 255, 255, 0))
        
        
        # Draw the shaded rectangle (box) with the given color
        draw.rectangle([xmin, ymin, xmax, ymax], fill=c, width=3, outline=border) # , outline=c[:3] + (255,)
    
    # Return the modified image
    return pil_img

    


def plot_results_orig(pil_img, results, id2label, filter=None): # prob, boxes):
    
    # results = {
    # "scores": tensor([0.993, 0.927]),
    # "labels": tensor([0, 0]),
    # "boxes": tensor([[0.000, 0.000, 70.333, 20.333], # bounding boxes: xmin, ymin, xmax, ymax
    #                  [10.001, 0.001, 0.998, 0.998]]),
    # }
    plot_results_unwr(pil_img, results["scores"].tolist(), results["labels"].tolist(), results["boxes"].tolist(), id2label, filter=filter)

def display_html_and_image(html_content, pil_image):
    """
    This is strictly for Jupyter notebooks. It displays the HTML content and the PIL image side by side.
    """
    from IPython.display import display, HTML
    from PIL import Image
    import io
    import base64
    
    # Convert the PIL image to a base64 string to embed it directly in the HTML
    img_buffer = io.BytesIO()
    pil_image.save(img_buffer, format='PNG')  # You can change the format if needed
    img_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    img_base64 = f"data:image/png;base64,{img_data}"

    # HTML content to display the image and HTML side by side
    html = f"""
    <style>
    table, th, td {{
        border: 1px solid black;
        border-collapse: collapse;
    }}
    th, td {{
        padding: 1px;
        text-align: left;
    }}
    </style>
    <div style="display: flex; align-items: center;">
        <div style="flex: 1; padding-right: 10px;">
            {html_content}
        </div>
        <div style="flex: 1;">
            <img src="{img_base64}" alt="PIL Image" style="max-width: 100%;"/>
        </div>
    </div>
    """

    # Display the HTML and image
    display(HTML(html))

def plot_interval_histogram(histogram, figsize=(12, 6), invert_x=False, dotted_line_at=1):
    """
    Plot an interval histogram showing frequency changes and optionally the original intervals.
    
    Args:
        histogram: IntervalHistogram instance to plot
        show_intervals: If True, show the original intervals below the histogram
        figsize: Tuple of (width, height) for the figure
        
    Returns:
        matplotlib figure object
    """
    if not histogram.sorted_points:
        raise ValueError("Histogram is empty")
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    
    # plot a series of rects:
    # for 2 consecutive change points [(p, pfreq), (q, qfreq))
    # plot the rectangle (xmin=p, ymin=0, xmax=q, ymax=pfreq)

    # max_freq = 0
    for i in range(len(histogram.sorted_points) - 1):
        p, pfreq = histogram.sorted_points[i]
        q, _ = histogram.sorted_points[i + 1]
        
        # if rotate_graph:
        #     ax.add_patch(plt.Rectangle((0, p), pfreq, q - p, fill=True, color='blue', alpha=0.5, linewidth=0))
        # else:
        ax.add_patch(plt.Rectangle((p, 0), q - p, pfreq, fill=True, color='blue', alpha=0.5, linewidth=0))
        # max_freq = max(max_freq, pfreq)
    

    if histogram.sorted_points:
        min_x = histogram.sorted_points[0][0]
        max_x = histogram.sorted_points[-1][0]
        ax.set_xlim(min_x, max_x)
    if dotted_line_at:
        ax.axhline(y=dotted_line_at, color='black', linestyle='--', linewidth=1)
    if invert_x:
        ax.invert_xaxis()

    # Set labels and title
    # if rotate_graph:
    #     ax.set_ylabel('Position')
    #     ax.set_xlabel('Frequency')
    # else:
    ax.set_xlabel('Position')
    ax.set_ylabel('Frequency')
    ax.set_title('Interval Histogram')
    
    # Adjust y-axis to show intervals if needed
    # if show_intervals:
        # ymin, ymax = ax.get_ylim()
    # if rotate_graph:
    #     ax.set_xlim(0, histogram.height + 0.5)
    #     ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    # else:
    ax.set_ylim(0, histogram.height + 0.5)
    # set y ticks to integers
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    return fig