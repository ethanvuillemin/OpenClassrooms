import gradio as gr
import cv2
import numpy as np

def canny_edge_detection(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    edges = cv2.Canny(blurred_image, 50, 150)
    return edges

def blur_image(image):
    blurred_image = cv2.GaussianBlur(image, (15, 15), 0)
    return blurred_image

def invert_image(image):
    inverted_image = cv2.bitwise_not(image)
    return inverted_image

def apply_transformation(image, choice):
    if choice == "Canny Edge Detection":
        return canny_edge_detection(image)
    elif choice == "Blur":
        return blur_image(image)
    elif choice == "Invert":
        return invert_image(image)

with gr.Blocks() as demo:
    gr.Markdown("<div style='text-align: center;'># Image Transformation App</div>")
    gr.Markdown("<div style='text-align: center;'>Upload an image and select a transformation</div>")

    with gr.Row():
        img_input = gr.Image(label="Upload Image", type="numpy")
        img_output = gr.Image(label="Transformed Image", type="pil", format="png")

    with gr.Row():
        transform_choice = gr.Dropdown(
            ["Canny Edge Detection", "Blur", "Invert"],
            label="Choose a transformation",
            value="Canny Edge Detection"
        )

    with gr.Row():
        transform_btn = gr.Button("Apply Transformation", variant="primary")

    transform_btn.click(
        apply_transformation,
        inputs=[img_input, transform_choice],
        outputs=img_output
    )

if __name__ == "__main__":
    demo.launch(show_error=True)
