from .models import File, Folder


def object_counts(request):
    """Returns number of File and Folder objects for menu bar"""
    return {
        'num_files': File.objects.count(),
        'num_folders': Folder.objects.count()
    }
