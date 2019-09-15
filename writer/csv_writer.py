import csv


class DefaultWriter:
    def __init__(self, filename, delim):
        self.fp = open(filename, mode='w')
        self.delimiter = delim

    def __enter__(self):
        return self

    def write(self, *data):
        writer = csv.writer(self.fp, delimiter=self.delimiter)
        writer.writerows(data)

    def __exit__(self, type, value, traceback):
        self.fp.close()
        if value:
            raise


class ColumnWriter:
    def __init__(self, filename, delim):
        self.fp = open(filename, mode='w')
        self.delimiter = delim

    def __enter__(self):
        return self

    def write(self, *data):
        writer = csv.writer(self.fp, delimiter=self.delimiter)
        # номер итерации и данные в каждой строке
        writer.writerows(zip(range(1, len(data[0])+1), *data))

    def __exit__(self, type, value, traceback):
        self.fp.close()
        if value:
            raise
