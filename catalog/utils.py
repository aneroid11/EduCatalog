import os
import sys
from django.contrib.auth import settings
from .models import EduMaterial


def delete_abandoned_files():
    materials = EduMaterial.objects.all()
    files_not_to_delete = [material.pdf_file.path for material in materials]
    root_dir = settings.BASE_DIR / "pdfmaterials/"

    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            full_path = os.path.join(subdir, file)

            if full_path not in files_not_to_delete:
                os.remove(full_path)


def delete_used_files():
    materials = EduMaterial.objects.all()
    files_to_delete = [material.pdf_file.path for material in materials]

    for file in files_to_delete:
        os.remove(file)

    # sys.exit(1)
