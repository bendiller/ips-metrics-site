from django.shortcuts import render

# Create your views here.

# One cool idea would be to have views that appear for individual IPF numbers, or tags. Something like the
# polls detail views shown at https://docs.djangoproject.com/en/2.2/intro/tutorial03/

# So, like /metrics/ipf/1/ would display the details for PT522309A

# Might also be cool to try to build a pattern that'd return details of partial tags. So /metrics/tags/309
# would return details for PT522309A, 309B, 525309A, etc. etc.
from collections import namedtuple
from datetime import datetime, timedelta

from django.http import HttpResponse
from django.apps import apps

Cell = apps.get_model("metrics", "Cell")


def sandbox(request):
    """ Used for testing different ideas and behaviors """


    out_str = "Metrics Sandbox - for testing out ideas and such.<br>"

    results = Cell.get_next_due(stop_date=datetime.now() + timedelta(days=280))

    # Filter just the useful columns:
    col_vals = ["Tag Number", "Description", "Plant", "Next Procedure Date"]
    results = results.filter(col_header__value__in=col_vals).order_by('ipf_num')

    # Define convenience object
    # (May seriously want to think about creating something that's more universally useful)
    # Can probably just use dict or something
    Row = namedtuple('Row', 'ipf_num tag desc plant due_date')

    rows = list()
    for ipf_num in set([result.ipf_num.value for result in results]):
        row_cells = results.filter(ipf_num__value=ipf_num)
        r = Row(ipf_num,
                row_cells.filter(col_header__value="Tag Number")[0].date_or_content,
                row_cells.filter(col_header__value="Description")[0].date_or_content,
                row_cells.filter(col_header__value="Plant")[0].date_or_content,
                row_cells.filter(col_header__value="Next Procedure Date")[0].date_or_content,
                )
        rows.append(r)

    # At this point I have two indexes - going to try to write some output with this data:
    # Build table and header row:
    out_str += "<table border='1'>"
    out_str += "<tr>"
    out_str += "<td>IPF Number</td>"
    for col_val in col_vals:
        out_str += f"<td>{col_val}</td>"
    out_str += "</tr>"

    # Build further table contents based on results of query:
    for row in sorted(rows, key=lambda row: row.due_date):  # Allows for convenient sorting by header
        out_str += "<tr>"
        for i in range(len(Row._fields)):
            val = row[i]
            out_str += f"<td>{val}</td>"
        out_str += "</tr>"
    out_str += "</table>"

    return HttpResponse(out_str)

# From: https://docs.djangoproject.com/en/2.2/intro/tutorial03/
# Will want to use the following shortcuts for dealing with failures to retrieve DB items:
# from django.shortcuts import get_object_or_404, render
# from .models import Cell
# # ...
# def detail(request, question_id):
#     question = get_object_or_404(Cell, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})

# There's also get_list_or_404() which uses filter() instead of get()