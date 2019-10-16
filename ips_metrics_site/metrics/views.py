# Create your views here.

# One cool idea would be to have views that appear for individual IPF numbers, or tags. Something like the
# polls detail views shown at https://docs.djangoproject.com/en/2.2/intro/tutorial03/

# So, like /metrics/ipf/1/ would display the details for PT522309A

# Might also be cool to try to build a pattern that'd return details of partial tags. So /metrics/tags/309
# would return details for PT522309A, 309B, 525309A, etc. etc.

from datetime import datetime, timedelta

from django.apps import apps
from django.http import HttpResponse
from django.shortcuts import render

Cell = apps.get_model("metrics", "Cell")

def not_found(request):
    return HttpResponse('Nothing here yet.')

def sandbox(request):
    """ Used for testing different ideas and behaviors """
    out_str = "Metrics Sandbox - for testing out ideas and such.<br>"

    return HttpResponse(out_str)


def upcoming(request):  # Will want to accept start_ and stop_date eventually, however that's done.
    next_due = Cell.get_next_due(stop_date=datetime.now() + timedelta(days=90))  # All cells for IPFs coming due

    # Filter just the useful columns:
    col_headers = ["IPF Number", "Tag Number", "Description", "Plant", "Next Procedure Date"]
    next_due = next_due.filter(col_header__value__in=col_headers[1:]).order_by('ipf_num')

    rows = list()
    for ipf_num in set([cell.ipf_num.value for cell in next_due]):
        row_cells = next_due.filter(ipf_num__value=ipf_num)
        r = {"IPF Number": ipf_num}
        r.update({col_header: row_cells.filter(col_header__value=col_header)[0].date_or_content
                  for col_header in col_headers[1:]})

        rows.append(r)

    return render(request, 'metrics/upcoming.html', {'rows': rows, 'col_headers': col_headers})

# From: https://docs.djangoproject.com/en/2.2/intro/tutorial03/
# Will want to use the following shortcuts for dealing with failures to retrieve DB items:
# from django.shortcuts import get_object_or_404, render
# from .models import Cell
# # ...
# def detail(request, question_id):
#     question = get_object_or_404(Cell, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})

# There's also get_list_or_404() which uses filter() instead of get()
