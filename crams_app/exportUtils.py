# coding=utf-8
"""
    File export Utilities
"""
import csv
from django.http import StreamingHttpResponse

__author__ = 'https://docs.djangoproject.com/en/1.7/howto/outputting-csv/'


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """

    # noinspection PyMethodMayBeStatic
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer.
        :param value:
        """
        return value


def stream_csv_view(column_array_row_list, csv_file_name):
    """A view that streams a large CSV file.
    :param column_array_row_list:
    :param csv_file_name:
    """
    # Generate a sequence of columns. The range is based on the maximum number
    #  of columns that can be handled by a single sheet in most spreadsheet
    # applications.
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in column_array_row_list),
        content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="' + \
        csv_file_name + '"'
    return response
