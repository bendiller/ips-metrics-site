from django.shortcuts import render

# Create your views here.

# One cool idea would be to have views that appear for individual IPF numbers, or tags. Something like the
# polls detail views shown at https://docs.djangoproject.com/en/2.2/intro/tutorial03/

# So, like /metrics/ipf/1/ would display the details for PT522309A

# Might also be cool to try to build a pattern that'd return details of partial tags. So /metrics/tags/309
# would return details for PT522309A, 309B, 525309A, etc. etc.
from datetime import datetime, timedelta

from django.http import HttpResponse
from django.apps import apps

Cell = apps.get_model("metrics", "Cell")


def sandbox(request):
    """ Used for testing different ideas and behaviors """

    out_str = "Metrics Sandbox - for testing out ideas and such.<br>"

    results = Cell.get_next_due(stop_date=datetime.now() + timedelta(days=90))

    # Filter just the useful columns:
    col_vals = ["Tag Number", "Description", "Plant", "Next Procedure Date"]
    results = results.filter(col_header__value__in=col_vals).order_by('ipf_num')

    # Convert to a dict indexed by IPF number:
    ipfs = set([result.ipf_num.value for result in results])
    table_data = dict()
    for ipf in ipfs:
        table_data[ipf] = results.filter(ipf_num__value=ipf)

    # At this point I have two indexes - going to try to write some output with this data:
    out_str += "<table border='1'>"
    out_str += "<tr>"
    for col_val in col_vals:
        out_str += f"<td>{col_val}</td>"
    out_str += "</tr>"

    for ipf in ipfs:
        out_str += "<tr>"
        for col_val in col_vals:
            val = table_data[ipf].filter(col_header__value=col_val)[0].date_or_content
            out_str += f"<td>{val}</td>"
        out_str += "</tr>"
    out_str += "</table>"

    # for result in results:
    #     out_str += f"<br>{result}"
        # out_str += f"<br>{result.ipf_num.value}"
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