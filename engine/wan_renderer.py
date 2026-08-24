import os
import torch
from PIL import Image
import imageio
from config import MODEL_ID, RESOLUTIONS, DEFAULT_FPS, DEFAULT_GUIDANCE, DEFAULT_STEPS


class WanRenderer:
    """
    Singleton renderer for Wan 2.2 image-to-video.
    Loads the model once and reuses it for every queued job.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.pipe = None
        return cls._instance

    def _load_pipe(self):
        if self.pipe is None:
            try:
                from diffusers import WanImageToVideoPipeline

                self.pipe = WanImageToVideoPipeline.from_pretrained(
                    MODEL_ID,
                    torch_dtype=torch.float16,
                )
            except ImportError:
                from diffusers import AutoPipelineForImageToVideo

                self.pipe = AutoPipelineForImageToVideo.from_pretrained(
                    MODEL_ID,
                    torch_dtype=torch.float16,
                )

            # Free Colab friendly
            if torch.cuda.is_available():
                self.pipe.to("cuda")
            self.pipe.enable_model_cpu_offload()
            self.pipe.enable_attention_slicing()

            # VAE tiling saves VRAM
            if hasattr(self.pipe, "vae") and hasattr(self.pipe.vae, "enable_tiling"):
                self.pipe.vae.enable_tiling()

        return self.pipe

    def render(
        self,
        image_path,
        prompt,
        resolution_key,
        duration,
        fps=DEFAULT_FPS,
        guidance=DEFAULT_GUIDANCE,
        steps=DEFAULT_STEPS,
        output_dir=None,
    ):
        """
        Renders one image into a video clip.

        Args:
            image_path: path to input image
            prompt: motion prompt for Wan
            resolution_key: "360p" or "480p"
            duration: seconds
            fps: frames per second
            guidance: classifier-free guidance scale
            steps: number of inference steps
            output_dir: folder to save the mp4

        Returns:
            path to output mp4
        """
        pipe = self._load_pipe()

        width, height = RESOLUTIONS[resolution_key]
        num_frames = int(fps * duration)

        # Load and resize image
        image = Image.open(image_path).convert("RGB").resize((width, height))

        # Generate video frames
        video_frames = pipe(
            image=image,
            prompt=prompt,
            height=height,
            width=width,
            num_frames=num_frames,
            guidance_scale=guidance,
            num_inference_steps=steps,
        ).frames[0]

        if output_dir is None:
            output_dir = os.path.dirname(image_path)

        os.makedirs(output_dir, exist_ok=True)

        base = os.path.splitext(os.path.basename(image_path))[0]
        safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt)[:30]
        output_path = os.path.join(
            output_dir,
            f"{base}_{resolution_key}_{duration}s_{safe_prompt}.mp4",
        )

        imageio.mimsave(output_path, video_frames, fps=fps)
        return output_path