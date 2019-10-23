# Create your views here.

# One cool idea would be to have views that appear for individual IPF numbers, or tags. Something like the
# polls detail views shown at https://docs.djangoproject.com/en/2.2/intro/tutorial03/

# So, like /metrics/ipf/1/ would display the details for PT522309A

# Might also be cool to try to build a pattern that'd return details of partial tags. So /metrics/tags/309
# would return details for PT522309A, 309B, 525309A, etc. etc.

from datetime import datetime, timedelta

from django.apps import apps
from django.core.exceptions import FieldError
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

Cell = apps.get_model("metrics", "Cell")


def not_found(request):
    return HttpResponse('Nothing here yet.')


def sandbox(request):
    """ Used for testing different ideas and behaviors """
    out_str = "Metrics Sandbox - for testing out ideas and such.<br>"

    return HttpResponse(out_str)


class Upcoming(View):
    # TODO: Make the column headers links with asc/desc
    # TODO: Make sure the links at left keep the preferred sorting
    col_headers = ["IPF Number", "Tag Number", "Type", "Description", "Plant", "Next Procedure Date", "Days Until Due"]
    sort_fields = {s.lower().replace(" ", ""): s for s in col_headers}  # Just a convenience object for sorting

    def get(self, request, days=30, sort_field="", reverse=False):  # Will want to accept start_ and stop_date eventually, however that's done.
        if sort_field is not "" and sort_field not in self.sort_fields:
            raise FieldError(f"{sort_field} is not a valid field for sorting.")  # Can't sort by a non-existent field.
            # I wonder if this should just 404 instead. # TODO Test this behavior

        stop_date = datetime.now() + timedelta(days=days)
        next_due = Cell.get_next_due(stop_date=stop_date)  # All cells for IPFs coming due

        # Filter just the useful columns:
        next_due = next_due.filter(col_header__value__in=self.col_headers[1:]).order_by('ipf_num')

        rows = list()
        for ipf_num in set([cell.ipf_num.value for cell in next_due]):
            row_cells = next_due.filter(ipf_num__value=ipf_num)
            r = {"IPF Number": ipf_num}
            r.update({col_header: row_cells.filter(col_header__value=col_header)[0].date_or_content
                      for col_header in self.col_headers[1:-1]})
            r.update({"Days Until Due": (r["Next Procedure Date"] - datetime.now().date()).days})

            rows.append(r)

        # Sort rows (may be dynamic / user-configurable later):
        # Default sorting that occurs before any user-specified sorting. May not want to keep this; not sure
        rows = sorted(rows, key=lambda row: row["IPF Number"])
        rows = sorted(rows, key=lambda row: row["Days Until Due"])

        if sort_field:
            rows = sorted(rows, key=lambda row: row[self.sort_fields[sort_field]], reverse=reverse)

        # Another option for this might look like:
        # orderbyList = ['check-in']  # default order
        #
        # if request.GET.getlist('order'):
        #     orderbyList = request.GET.getlist('order')
        #
        # modelclassinstance.objects.all().order_by(*orderbyList)

        # TODO Determine if self.col_headers needs to be returned anymore - probably not!
        return render(request, 'metrics/upcoming.html', {'rows': rows, 'col_headers': self.col_headers, 'days': days})

# From: https://docs.djangoproject.com/en/2.2/intro/tutorial03/
# Will want to use the following shortcuts for dealing with failures to retrieve DB items:
# from django.shortcuts import get_object_or_404, render
# from .models import Cell
# # ...
# def detail(request, question_id):
#     question = get_object_or_404(Cell, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})

# There's also get_list_or_404() which uses filter() instead of get()

# Check out generic.DetailView as shown here: https://docs.djangoproject.com/en/2.2/intro/tutorial04/
# This would be useful for pages that link to an individual IPF number or similar
