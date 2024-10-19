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
                      id2color: dict = None, filter=None, alpha=0.2):
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
        
        # Draw the shaded rectangle (box) with the given color
        draw.rectangle([xmin, ymin, xmax, ymax], fill=c, width=3) # , outline=c[:3] + (255,)
    
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
