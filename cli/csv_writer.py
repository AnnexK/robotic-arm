import csv

class DefaultWriter:
    def __init__(self, fp, delim):
        self.fp = fp
        self.delimiter = delim

    def write(self, *data):
        writer = csv.writer(self.fp, delimiter=self.delimiter)
        writer.writerows(data)

    def __del__(self):
        self.fp.close()

class ColumnWriter:
    def __init__(self, fp, delim):
        self.fp = fp
        self.delimiter = delim

    def write(self, *data):
        pass

