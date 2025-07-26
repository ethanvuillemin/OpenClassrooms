import gradio as gr

from transformations.simple_cv import apply_transformation
from transformations.augmentation import apply_augmentation
from transformations.ai_model import call_api_and_overlay_mask


with gr.Blocks() as demo:
    with gr.Tab("Image Segmentation Tool"):
        gr.Markdown("<div style='text-align: center;'><h1>Image Segmentation Tool</h1><br><h3>Upload an image and select a transformation</h3></div>")
        with gr.Row():
            img_input_1 = gr.Image(label="Upload Image", type="numpy")
            img_output_1 = gr.Image(label="Transformed Image", type="pil", format="png")
        with gr.Row():
            transform_choice = gr.Dropdown(
                ["DeeplabV3+", "Canny Edge Detection", "Blur", "Invert"],
                label="Choose a transformation",
                value="Canny Edge Detection"
            )
        with gr.Row():
            transform_btn = gr.Button("Apply Transformation", variant="primary")
        transform_btn.click(
            lambda img, choice: call_api_and_overlay_mask(img) if choice == "DeeplabV3+" else apply_transformation(img, choice),
            inputs=[img_input_1, transform_choice],
            outputs=img_output_1
        )
    with gr.Tab("Data Augmentation"):
        gr.Markdown("<div style='text-align: center;'><h1>Data Augmentation</h1><br><h3>Upload an image and choose an augmentation technique</h3></div>")
        with gr.Row():
            img_input_2 = gr.Image(label="Upload Image", type="numpy")
            img_output_2 = gr.Image(label="Augmented Image", type="numpy")
        with gr.Row():
            aug_choice = gr.Dropdown(
                [
                    "Horizontal Flip",
                    "Vertical Flip",
                    "Rotation",
                    "Zoom",
                    "Gaussian Noise"
                ],
                label="Choose an augmentation",
                value="Horizontal Flip"
            )
        with gr.Row():
            aug_btn = gr.Button("Apply Augmentation", variant="primary")
        aug_btn.click(
            apply_augmentation,
            inputs=[img_input_2, aug_choice],
            outputs=img_output_2
        )

if __name__ == "__main__":
    demo.launch(show_error=True)
