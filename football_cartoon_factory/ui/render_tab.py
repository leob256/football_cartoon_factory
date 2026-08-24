import gradio as gr
import os
from engine.compositor import compose_scene


def build_render_tab(qm):
    with gr.Column():
        gr.Markdown("## Wan 2.2 Render Queue")

        with gr.Row():
            # Left column: input controls
            with gr.Column(scale=1):
                character_image = gr.Image(
                    type="filepath",
                    label="Character Image (transparent PNG works best)",
                )
                background_image = gr.Image(
                    type="filepath",
                    label="Background Image",
                )
                precomposed_image = gr.Image(
                    type="filepath",
                    label="OR use a pre-composed image (optional)",
                )
                prompt_input = gr.Textbox(
                    label="Motion Prompt",
                    lines=4,
                    placeholder="Example: Ronaldo opens fridge, camera slowly zooms in, exaggerated cartoon facial expression, smooth body movement, cinematic lighting.",
                )
                resolution_dropdown = gr.Dropdown(
                    choices=["360p", "480p"],
                    value="360p",
                    label="Resolution",
                )
                duration_slider = gr.Slider(
                    minimum=1,
                    maximum=8,
                    value=5,
                    step=1,
                    label="Duration (seconds)",
                )
                add_btn = gr.Button("Add to Queue", variant="primary")

            # Right column: queue table + controls
            with gr.Column(scale=2):
                jobs_table = gr.Dataframe(
                    headers=["ID", "Prompt", "Resolution", "Duration", "Status", "Output"],
                    datatype=["str", "str", "str", "number", "str", "str"],
                    label="Render Queue",
                    interactive=False,
                )
                refresh_btn = gr.Button("Refresh Queue")
                render_queue_btn = gr.Button("Start / Resume Queue", variant="primary")
                status_text = gr.Textbox(label="Queue Status", interactive=False)

                job_selector = gr.Dropdown(
                    label="Completed Jobs (select to download)",
                    choices=[],
                    interactive=True,
                )
                download_btn = gr.Button("Download Selected Video")
                video_output = gr.File(label="Download")

        # Helper functions
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

        def add_job(character, background, precomposed, prompt, resolution, duration):
            if not prompt.strip():
                return get_table(), "Please enter a motion prompt", update_selector()

            # Determine final image path
            if precomposed:
                final_image = precomposed
            elif character and background:
                try:
                    final_image = compose_scene(character, background)
                except Exception as e:
                    return get_table(), f"Compositing failed: {e}", update_selector()
            elif character:
                final_image = character
            elif background:
                final_image = background
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

        # Wire up events
        add_btn.click(
            fn=add_job,
            inputs=[character_image, background_image, precomposed_image, prompt_input, resolution_dropdown, duration_slider],
            outputs=[jobs_table, status_text, job_selector],
        )

        render_queue_btn.click(
            fn=start_queue,
            outputs=[jobs_table, status_text, job_selector],
        )

        refresh_btn.click(
            fn=refresh,
            outputs=[jobs_table, job_selector, status_text],
        )

        download_btn.click(
            fn=download_selected,
            inputs=job_selector,
            outputs=video_output,
        )

        # Initial table
        jobs_table.value = get_table()