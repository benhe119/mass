from .models import File, Folder, ClamAVSettings


def object_counts(request):
    """Returns number of File and Folder objects for menu bar"""
    return {
        'num_files': File.objects.count(),
        'num_folders': Folder.objects.count()
    }


def clamav_settings(request):
    return {'clamav_settings': ClamAVSettings.load()}
