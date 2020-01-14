# Create your views here.

# One cool idea would be to have views that appear for individual IPF numbers, or tags. Something like the
# polls detail views shown at https://docs.djangoproject.com/en/2.2/intro/tutorial03/

# So, like /metrics/ipf/1/ would display the details for PT522309A

# Might also be cool to try to build a pattern that'd return details of partial tags. So /metrics/tags/309
# would return details for PT522309A, 309B, 525309A, etc. etc.

from datetime import datetime, timedelta
import json

from django.apps import apps
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

Cell = apps.get_model("metrics", "Cell")
DocsBlob = apps.get_model("metrics", "DocsBlob")
IPFNumber = apps.get_model("metrics", "IPFNumber")
WorkSheet = apps.get_model("metrics", "WorkSheet")


def not_found(request):
    return HttpResponse('Nothing here yet.')


def sandbox(request):
    """ Used for testing different ideas and behaviors """
    out_str = "Metrics Sandbox - for testing out ideas and such.<br>"

    return HttpResponse(out_str)


def load(ipf_num):
    # Look for JSON file corresponding to this IPF num:
    import os
    fpath = os.path.join(r"C:\ProgProjects\ips-folder-crawler", f"{ipf_num}.json")
    if os.path.isfile(fpath):
        with open(fpath, 'r') as f:
            content = json.load(f)
        docs_blob = DocsBlob(ipf_num=ipf_num, content=content)
        try:
            docs_blob.save()
        except IntegrityError:
            return f"JSON contents for IPF #{ipf_num} already stored in DB!"
        return f"Successfully loaded JSON for IPF #{ipf_num} into DB."

    else:
        return f"Could not locate JSON file for IPF #{ipf_num} at path: {fpath}"


class Upcoming(View):
    # TODO - Should I use Last Procedure Date somehow too? This whole thing breaks if "Next Procedure Date" is wrong
    col_headers = ["IPF Number", "Tag Number", "Type", "Description", "Plant", "Next Procedure Date", "Days Until Due"]
    sort_fields = {s.lower().replace(" ", ""): s for s in col_headers}  # Just a convenience object for sorting

    def get(self, request, days=30):  # Will want to accept start_ and stop_date eventually, however that's done.
        # if sort_field is not "" and sort_field not in self.sort_fields:
        #     raise FieldError(f"{sort_field} is not a valid field for sorting.")  # Can't sort by a non-existent field.
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

        # if sort_field:
        #     rows = sorted(rows, key=lambda row: row[self.sort_fields[sort_field]], reverse=reverse)

        # Another option for this might look like:
        # orderbyList = ['check-in']  # default order
        #
        # if request.GET.getlist('order'):
        #     orderbyList = request.GET.getlist('order')
        #
        # modelclassinstance.objects.all().order_by(*orderbyList)

        # TODO Determine if self.col_headers needs to be returned anymore - probably not!
        return render(request, 'metrics/upcoming.html', {'rows': rows, 'col_headers': self.col_headers, 'days': days})


class IPFDetail(View):
    def get(self, request, ipf_num, cmd=''):
        # TODO - just a temporary measure to load from the JSON files previously collected, so that I can get a prototype for this View going.
        if cmd == "load":
            return HttpResponse(load(ipf_num))

        try:
            docs_blob = DocsBlob.objects.get(ipf_num=ipf_num)

        except ObjectDoesNotExist:
            return HttpResponse(f"IPF #{ipf_num} has not had details loaded yet.")
        docs_blob = eval(docs_blob.content)

        content = dict()
        content["ipf_num"] = ipf_num
        content["tag"] = docs_blob["tag"]  # Should probably be a DB lookup, eventually.
        content["site"] = docs_blob["site"]
        content["documents"] = docs_blob["documents"]

        return render(request, 'metrics/ipf-detail.html', content)


class IPFDetailLoader(View):
    def get(self, request):
        """Temporary View for loading all collected JSON data about IPF documents into DB."""
        results = ""
        latest_ws = WorkSheet.objects.latest('modified_time')
        ipf_numbers = [i.value for i in IPFNumber.objects.all().filter(worksheet=latest_ws)]
        for ipf_num in ipf_numbers:
            results += f"<li>{ipf_num} | {load(ipf_num)}</li>"

        return HttpResponse(f"<ul>{results}</ul>")





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
