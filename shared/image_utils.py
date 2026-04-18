import os

from shared.paths import IMAGES_DIR


IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".gif")
DEFAULT_PRODUCT_IMAGE = "Paracetamol.png"


def image_exists(image_name):
    return bool(image_name) and os.path.exists(os.path.join(IMAGES_DIR, image_name))


def product_image_name(product_name, fallback=DEFAULT_PRODUCT_IMAGE):
    clean_name = str(product_name or "").strip()

    for extension in IMAGE_EXTENSIONS:
        candidate = f"{clean_name}{extension}"
        if image_exists(candidate):
            return candidate

    if image_exists(fallback):
        return fallback

    return DEFAULT_PRODUCT_IMAGE
