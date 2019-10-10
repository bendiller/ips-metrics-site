from django.shortcuts import render

# Create your views here.

# One cool idea would be to have views that appear for individual IPF numbers, or tags. Something like the
# polls detail views shown at https://docs.djangoproject.com/en/2.2/intro/tutorial03/

# So, like /metrics/ipf/1/ would display the details for PT522309A

# Might also be cool to try to build a pattern that'd return details of partial tags. So /metrics/tags/309
# would return details for PT522309A, 309B, 525309A, etc. etc.

from django.http import HttpResponse
from django.apps import apps

Cell = apps.get_model("metrics", "Cell")

def sandbox(request):
    """ Used for testing different ideas and behaviors """
    cells =  Cell.objects.all()
    out_str = "Metrics Sandbox - for testing out ideas and such."
    out_str += f"\nCell: {str(cells[0])}"
    return HttpResponse(out_str)

