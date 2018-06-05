from .models import File, Folder


def object_counts(request):
    return {
        'num_files': File.objects.count(),
        'num_folders': Folder.objects.count()
    }
