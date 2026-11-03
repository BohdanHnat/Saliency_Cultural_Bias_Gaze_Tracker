from PIL import Image
import numpy as np
import io

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def generate_heatmap(gaze_data, image_file, bins=100, alpha=0.5):
    x = np.array([row['norm_x'] for row in gaze_data])
    y = np.array([row['norm_y'] for row in gaze_data])

    bg_image = Image.open(image_file).convert('RGB')
    width, height = bg_image.size

    if np.min(x) < 0 or np.max(x) > width:
        x = ((x - np.min(x)) / (np.max(x) - np.min(x))) * width
    if np.min(y) < 0 or np.max(y) > height:
        y = ((y - np.min(y)) / (np.max(y) - np.min(y))) * height

    heatmap, xedges, yedges = np.histogram2d(x, y, bins=[bins, bins], range=[[0, width], [0, height]])

    # Plot image and overlay heatmap
    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    ax.imshow(bg_image, extent=[0, width, 0, height], aspect='auto', zorder=1)
    ax.imshow(
        heatmap.T,
        origin='lower',
        cmap='hot',
        interpolation='nearest',
        alpha=alpha,
        aspect='auto',
        extent=[0, width, 0, height],
        zorder=2,
    )
    plt.axis("off")
    plt.tight_layout(pad=0)

    # Save bytes to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    result_img = Image.open(buf).copy()
    buf.close()

    return result_img
