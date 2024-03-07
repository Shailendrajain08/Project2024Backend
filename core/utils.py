from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


ALLOWED_FILE_EXTENSIONS = ["pdf", "doc", "docx", "txt", "jpg", "jpeg", "png"]


def validate_file_size(value):
    max_size = 100 * 1024 * 1024  # 100 MB
    if value.size > max_size:
        raise ValidationError("File size must be no more than 100 MB.")


def file_field_validators():
    return [
        FileExtensionValidator(allowed_extensions=ALLOWED_FILE_EXTENSIONS),
        validate_file_size,
    ]
