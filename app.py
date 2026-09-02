import gradio as gr
from detector import analyze_code


example_code = """from ucimlrepo import fetch_ucirepo

# fetch dataset
bike_sharing = fetch_ucirepo(id=275)

# data (as pandas dataframes)
X = bike_sharing.data.features
y = bike_sharing.data.targets

# metadata
print(bike_sharing.metadata)

# variable information
print(bike_sharing.variables)
"""


with gr.Blocks(title="Auto ML Problem Detector") as app:

    gr.Markdown(
        """
        # Auto ML Problem Detector

        Paste your UCI ML Repository dataset code below.

        The system will automatically determine whether the
        dataset is more suitable for **Classification** or **Regression**.
        """
    )

    code_input = gr.Code(
        label="UCI Dataset Code",
        language="python",
        value=example_code,
        lines=20
    )

    submit_button = gr.Button("Analyze Dataset")

    result_output = gr.Textbox(
        label="Analysis Result",
        lines=12
    )

    submit_button.click(
        fn=analyze_code,
        inputs=code_input,
        outputs=result_output
    )


app.launch()