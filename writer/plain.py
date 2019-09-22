class PlainWriter:
    def __init__(self, filename):
        self.fp = None
        self.fname = filename

    def __enter__(self):
        self.fp = open(self.fname, mode='w')
        return self

    def write(self, *data):
        if self.fp is None:
            raise TypeError()
        for d in zip(*data):
            for val in d:
                self.fp.write('{} '.format(val))
            self.fp.write('\n')

    def __exit__(self, type, value, traceback):
        self.fp.close()
        if value:
            raise
