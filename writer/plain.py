class PlainWriter:
    def __init__(self, filename):
        self.fp = None
        self.fname = filename

    def __enter__(self):
        self.fp = open(self.fname, mode='w')
        return self

    def write(self, *data):
        self.fp.writelines(data[0])

    def __exit__(self, type, value, traceback):
        self.fp.close()
        if value:
            raise
