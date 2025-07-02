import gradio as gr

from simple_cv import apply_transformation

with gr.Blocks() as demo:
    gr.Markdown("<div style='text-align: center;'><h1>Image Segmentation Tool</h1><br><h3>Upload an image and select a transformation</h3></div>")

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
