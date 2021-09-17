import uuid


def pronounce_full_path(instance, filename):
    if not instance.id:
        raise Exception('Uploading pronounce is not supported at word creation time')

    ext = os.path.splitext(filename)[1]
    filename = '%07d-%s' % (instance.id, uuid.uuid4().hex[:8])
    basename = filename + ext

    return os.path.join('pronounce', basename)