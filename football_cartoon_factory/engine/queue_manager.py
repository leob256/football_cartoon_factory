import threading
import uuid
from engine.wan_renderer import WanRenderer
from config import SCENES_DIR


class QueueManager:
    """
    Thread-safe render queue.
    """

    def __init__(self):
        self.jobs = []
        self.lock = threading.Lock()
        self.processing = False
        self.worker_thread = None
        self.status = "Idle"

    def add_job(self, image_path, prompt, resolution, duration):
        job = {
            "id": str(uuid.uuid4())[:8],
            "image_path": image_path,
            "prompt": prompt,
            "resolution": resolution,
            "duration": int(duration),
            "status": "pending",
            "output": None,
            "error": None,
        }
        with self.lock:
            self.jobs.append(job)
        return job

    def get_jobs(self):
        with self.lock:
            # Return copies so UI can safely read
            return list(self.jobs)

    def is_processing(self):
        return self.processing

    def get_status_text(self):
        return self.status

    def start(self):
        if self.processing:
            return

        self.processing = True
        self.status = "Processing queue..."
        self.worker_thread = threading.Thread(target=self._process_jobs, daemon=True)
        self.worker_thread.start()

    def _process_jobs(self):
        renderer = WanRenderer()

        while True:
            pending = None

            with self.lock:
                for job in self.jobs:
                    if job["status"] == "pending":
                        job["status"] = "rendering"
                        pending = job
                        break

            if pending is None:
                break

            try:
                output_path = renderer.render(
                    image_path=pending["image_path"],
                    prompt=pending["prompt"],
                    resolution_key=pending["resolution"],
                    duration=pending["duration"],
                    output_dir=SCENES_DIR,
                )

                with self.lock:
                    for job in self.jobs:
                        if job["id"] == pending["id"]:
                            job["status"] = "completed"
                            job["output"] = output_path
                            break

                self.status = f"Completed {pending['id']}"

            except Exception as e:
                with self.lock:
                    for job in self.jobs:
                        if job["id"] == pending["id"]:
                            job["status"] = "failed"
                            job["error"] = str(e)
                            break

                self.status = f"Failed {pending['id']}: {e}"

        self.processing = False
        self.status = "Queue idle"