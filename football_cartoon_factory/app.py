import gradio as gr
from engine.queue_manager import QueueManager
from ui.prompt_tab import build_prompt_tab
from ui.render_tab import build_render_tab


def create_app():
    qm = QueueManager()

    with gr.Blocks(
        title="Football Cartoon Factory",
        theme=gr.themes.Soft(),
    ) as app:
        gr.Markdown("# Football Cartoon Factory v1.0")

        with gr.Tab("Prompt Studio"):
            build_prompt_tab()

        with gr.Tab("Render Queue"):
            build_render_tab(qm)

        with gr.Tab("Voice / Lip Sync"):
            gr.Markdown("### Coming in Milestone 2")

        with gr.Tab("Subtitles / FX"):
            gr.Markdown("### Coming in Milestone 2")

        with gr.Tab("Export"):
            gr.Markdown("### Coming in Milestone 2")

    return app


if __name__ == "__main__":
    app = create_app()
    app.launch(share=True)