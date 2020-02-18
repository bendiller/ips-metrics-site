from datetime import datetime, timedelta
import json

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

Cell = apps.get_model("metrics", "Cell")
ColumnHeader = apps.get_model("metrics", "ColumnHeader")
DocsBlob = apps.get_model("metrics", "DocsBlob")
IPFNumber = apps.get_model("metrics", "IPFNumber")
WorkSheet = apps.get_model("metrics", "WorkSheet")


class Upcoming(View):
    col_headers = ["IPF Number", "Tag Number", "Type", "Description", "Plant", "Next Procedure Date", "Days Until Due"]
    sort_fields = {s.lower().replace(" ", ""): s for s in col_headers}  # Just a convenience object for sorting
    template = 'metrics/upcoming.html'

    def get(self, request, days=30):
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

        # Default sorting that occurs before any user-specified sorting.
        rows = sorted(rows, key=lambda row: row["IPF Number"])
        rows = sorted(rows, key=lambda row: row["Days Until Due"])

        return render(request, self.template, {'rows': rows, 'col_headers': self.col_headers, 'days': days})


class IPFDetail(View):
    template = 'metrics/ipf-detail.html'

    def get(self, request, ipf_num):
        try:
            docs_blob = DocsBlob.objects.get(ipf_num=ipf_num)
        except ObjectDoesNotExist:
            return HttpResponse(f"IPF #{ipf_num} has not had details loaded yet.")

        try:
            # Necessary as try/except due to initial way data was stored
            docs_blob = json.loads(docs_blob.content)
        except json.decoder.JSONDecodeError:
            docs_blob = eval(docs_blob.content)

        content = dict()
        content["ipf_num"] = ipf_num
        content["tag"] = docs_blob["tag"]  # Should probably be a DB lookup, eventually.
        content["site"] = docs_blob["site"]
        content["documents"] = docs_blob["documents"]

        latest_ws = WorkSheet.objects.latest('modified_time')
        ipf_num_record = IPFNumber.objects.all().filter(value=ipf_num,
                                                        worksheet=latest_ws)[0]
        desc_col_header = ColumnHeader.objects.all().filter(value="Description",
                                                            worksheet=latest_ws)[0]
        content["description"] = Cell.objects.all().filter(ipf_num=ipf_num_record,
                                                           col_header=desc_col_header,
                                                           worksheet=latest_ws)[0].content

        next_due_col_header = ColumnHeader.objects.all().filter(value="Next Procedure Date",
                                                                worksheet=latest_ws)[0]
        content["next_due"] = Cell.objects.all().filter(ipf_num=ipf_num_record,
                                                        col_header=next_due_col_header,
                                                        worksheet=latest_ws)[0].date_or_content

        last_done_col_header = ColumnHeader.objects.all().filter(value="Last Procedure Date",
                                                                 worksheet=latest_ws)[0]
        content["last_done"] = Cell.objects.all().filter(ipf_num=ipf_num_record,
                                                         col_header=last_done_col_header,
                                                         worksheet=latest_ws)[0].date_or_content

        return render(request, self.template, content)


class Repopulate(View):
    def post(self, response, ipf_num):
        doc_paths = DocsBlob.update(ipf_num)
        context = {'result': doc_paths, 'ipf_num': ipf_num}
        return render(response, 'metrics/ipf-repop.html', context)
