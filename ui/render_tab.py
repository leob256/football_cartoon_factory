import gradio as gr
import os
from engine.compositor import compose_scene


def build_render_tab(qm):
    with gr.Column():
        gr.Markdown("## Wan 2.2 Render Queue")
        gr.Markdown("Upload images using the buttons below. You can upload a character, a background, or a pre-composed image.")

        with gr.Row():
            with gr.Column(scale=1):
                character_file = gr.File(
                    label="Character Image (PNG/JPG)",
                    file_types=["image"],
                    type="filepath"
                )
                background_file = gr.File(
                    label="Background Image (PNG/JPG)",
                    file_types=["image"],
                    type="filepath"
                )
                precomposed_file = gr.File(
                    label="OR pre-composed image (optional)",
                    file_types=["image"],
                    type="filepath"
                )

                prompt_input = gr.Textbox(
                    label="Motion Prompt",
                    lines=4,
                    placeholder="Example: Ronaldo opens fridge, camera slowly zooms in, exaggerated cartoon facial expression, smooth body movement, cinematic lighting."
                )
                resolution_dropdown = gr.Dropdown(
                    choices=["360p", "480p"],
                    value="360p",
                    label="Resolution"
                )
                duration_slider = gr.Slider(
                    minimum=1,
                    maximum=8,
                    value=2,
                    step=1,
                    label="Duration (seconds)",
                    interactive=True
                )
                add_btn = gr.Button("Add to Queue", variant="primary")

            with gr.Column(scale=2):
                jobs_table = gr.Dataframe(
                    headers=["ID", "Prompt", "Resolution", "Duration", "Status", "Output"],
                    datatype=["str", "str", "str", "number", "str", "str"],
                    label="Render Queue",
                    interactive=False
                )
                with gr.Row():
                    refresh_btn = gr.Button("Refresh Queue")
                    render_queue_btn = gr.Button("Start / Resume Queue", variant="primary")
                status_text = gr.Textbox(label="Queue Status", interactive=False)

                job_selector = gr.Dropdown(
                    label="Completed Jobs (select to download)",
                    choices=[],
                    interactive=True
                )
                download_btn = gr.Button("Download Selected Video")
                video_output = gr.File(label="Download")

        def get_table():
            jobs = qm.get_jobs()
            rows = []
            for j in jobs:
                prompt_short = j["prompt"][:50] + ("..." if len(j["prompt"]) > 50 else "")
                rows.append([
                    j["id"],
                    prompt_short,
                    j["resolution"],
                    j["duration"],
                    j["status"],
                    j["output"] or "",
                ])
            return rows

        def update_selector():
            jobs = qm.get_jobs()
            choices = [j["output"] for j in jobs if j["status"] == "completed" and j["output"]]
            return gr.Dropdown.update(choices=choices, value=choices[0] if choices else None)

        def add_job(char_file, bg_file, precomp_file, prompt, resolution, duration):
            if not prompt.strip():
                return get_table(), "Please enter a motion prompt", update_selector()

            char_path = char_file if char_file else None
            bg_path = bg_file if bg_file else None
            precomp_path = precomp_file if precomp_file else None

            if precomp_path:
                final_image = precomp_path
            elif char_path and bg_path:
                try:
                    final_image = compose_scene(char_path, bg_path)
                except Exception as e:
                    return get_table(), f"Compositing failed: {e}", update_selector()
            elif char_path:
                final_image = char_path
            elif bg_path:
                final_image = bg_path
            else:
                return get_table(), "Please upload at least one image", update_selector()

            qm.add_job(final_image, prompt, resolution, int(duration))
            return (
                get_table(),
                f"Added job. Queue length: {len(qm.get_jobs())}",
                update_selector(),
            )

        def start_queue():
            if qm.is_processing():
                return get_table(), "Queue is already processing", update_selector()
            qm.start()
            return get_table(), "Queue processing started", update_selector()

        def refresh():
            return get_table(), update_selector(), qm.get_status_text()

        def download_selected(path):
            if path and os.path.exists(path):
                return path
            return None

        add_btn.click(
            fn=add_job,
            inputs=[character_file, background_file, precomposed_file, prompt_input, resolution_dropdown, duration_slider],
            outputs=[jobs_table, status_text, job_selector]
        )
        render_queue_btn.click(
            fn=start_queue,
            outputs=[jobs_table, status_text, job_selector]
        )
        refresh_btn.click(
            fn=refresh,
            outputs=[jobs_table, job_selector, status_text]
        )
        download_btn.click(
            fn=download_selected,
            inputs=job_selector,
            outputs=video_output
        )

        jobs_table.value = get_table()