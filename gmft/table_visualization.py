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


def plot_results_orig(pil_img, results, id2label, filter=None): # prob, boxes):
    
    # results = {
    # "scores": tensor([0.993, 0.927]),
    # "labels": tensor([0, 0]),
    # "boxes": tensor([[0.000, 0.000, 70.333, 20.333], # bounding boxes: xmin, ymin, xmax, ymax
    #                  [10.001, 0.001, 0.998, 0.998]]),
    # }
    plot_results_unwr(pil_img, results["scores"].tolist(), results["labels"].tolist(), results["boxes"].tolist(), id2label, filter=filter)
