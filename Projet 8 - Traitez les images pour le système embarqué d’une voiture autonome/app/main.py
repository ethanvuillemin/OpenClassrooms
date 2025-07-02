import gradio as gr
import numpy as np
import random

# Define the function to annotate the image with random boxes and segments.
def section(img):
    sections = []
    num_boxes = 2  # Fixed number of boxes
    num_segments = 1  # Fixed number of segments
    section_labels = [
        "apple",
        "banana",
        "carrot",
        "donut",
        "eggplant",
        "fish",
        "grapes",
        "hamburger",
        "ice cream",
        "juice",
    ]

    for a in range(num_boxes):
        x = random.randint(0, img.shape[1])
        y = random.randint(0, img.shape[0])
        w = random.randint(0, img.shape[1] - x)
        h = random.randint(0, img.shape[0] - y)
        sections.append(((x, y, x + w, y + h), section_labels[a]))

    for b in range(num_segments):
        x = random.randint(0, img.shape[1])
        y = random.randint(0, img.shape[0])
        r = random.randint(0, min(x, y, img.shape[1] - x, img.shape[0] - y))
        mask = np.zeros(img.shape[:2])
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                dist_square = (i - y) ** 2 + (j - x) ** 2
                if dist_square < r**2:
                    mask[i, j] = round((r**2 - dist_square) / r**2 * 4) / 4
        sections.append((mask, section_labels[b + num_boxes]))

    return (img, sections)

# Create the Gradio interface.
with gr.Blocks() as demo:
    with gr.Row():
        img_input = gr.Image(label="Upload Image")
        img_output = gr.AnnotatedImage(label="Result", color_map={"banana": "#a89a00", "carrot": "#ffae00"})

    section_btn = gr.Button("Predict")

    # Connect the button click to the section function.
    section_btn.click(section, inputs=img_input, outputs=img_output)

# Launch the interface.
if __name__ == "__main__":
    demo.launch(show_error=True)
