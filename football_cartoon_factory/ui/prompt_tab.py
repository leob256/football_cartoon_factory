import gradio as gr

IDEA_GENERATOR_PROMPT = """You are a viral YouTube Shorts football cartoon creator.

Generate 10 funny 30-second cartoon Short ideas featuring famous footballers (Ronaldo, Messi, Mbappé, Haaland, Yamal, Bellingham, etc).

Each idea must:
- Have a strong hook in the first 3 seconds
- Use 6 scenes of ~5 seconds each
- Be dialogue-driven or visual comedy
- End with a viral punchline or meme
- Use exaggerated cartoon physics

Return as a numbered list with title + one-sentence logline.
"""

SCENE_BUILDER_TEMPLATE = """Using this chosen idea:

[PASTE CHOSEN IDEA HERE]

Create a complete 30-second cartoon Short storyboard with 6 scenes.

For each scene provide:
1. Scene number and time (e.g. 0-5s)
2. Background (reusable if possible)
3. Characters involved (use my consistent character sheet: Pixar-style, etc.)
4. Dialogue (short, funny)
5. Facial expressions and actions
6. Camera movement (zoom, pan, tracking)
7. WAN 2.2 motion prompt (exactly how to animate the still image)
8. Sound effects / music cue

Then provide a list of all required character images and backgrounds I need to generate in Copilot, with detailed prompts for each (keep character design consistent: Pixar-style).
"""


def build_prompt_tab():
    with gr.Column():
        gr.Markdown("## Prompt Studio")

        with gr.Group():
            gr.Markdown("### 1. Idea Generator")
            gr.Markdown("Copy this into ChatGPT to get 10 viral football cartoon ideas.")
            idea_prompt = gr.Textbox(
                value=IDEA_GENERATOR_PROMPT,
                lines=12,
                show_copy_button=True,
                label="Idea Generator Prompt",
            )

        with gr.Group():
            gr.Markdown("### 2. Scene Builder")
            gr.Markdown("Paste your chosen idea below, then click to build the full scene prompt.")
            chosen_idea = gr.Textbox(
                label="Chosen idea",
                lines=3,
                placeholder="Paste the idea ChatGPT gave you...",
            )
            build_scene_btn = gr.Button("Build Scene Builder Prompt", variant="primary")

            scene_prompt = gr.Textbox(
                label="Scene Builder Prompt — copy this into ChatGPT",
                lines=18,
                show_copy_button=True,
            )

        def build_scene(chosen):
            if not chosen.strip():
                return "Please paste a chosen idea first."
            return SCENE_BUILDER_TEMPLATE.replace(
                "[PASTE CHOSEN IDEA HERE]", chosen.strip()
            )

        build_scene_btn.click(
            fn=build_scene,
            inputs=chosen_idea,
            outputs=scene_prompt,
        )