import gc
import torch  # For memory clean-up
from pathlib import Path

from fastai.vision.all import *

in_path: str = r"d:\data\NRSI\__ai_training_images"

def image_test(image_path: Path) -> bool:
    """Determine if the given image path is in the "true" folder,
    so the training / fine-tuning algorithm can learn from it.

    Args:
        image_path (Path): The Path for the image being processed

    Returns:
        bool: `True` if the folder contains `true` in the path,
              `False` otherwise.
    """
    # See: https://docs.python.org/3/library/pathlib.html#accessing-individual-parts
    return "true" in image_path.parts


# See: https://docs.fast.ai/vision.data.html#ImageDataLoaders.from_path_func
data_loader = ImageDataLoaders.from_path_func(
    path=in_path,
    fnames=get_image_files(in_path),
    valid_pct=0.2,
    seed=42,
    label_func=image_test,
    item_tfms=Resize(224),
    bs=32,  # Batch Size defaults to 64 - but 32 fixes the `RuntimeError: CUDA out of memory.`
)

if __name__ == "__main__":
    # Clean up the GPU memory
    gc.collect()
    torch.cuda.empty_cache()

    # Try and learn
    learn = cnn_learner(data_loader, resnet34, metrics=error_rate)
    learn.fine_tune(1)
