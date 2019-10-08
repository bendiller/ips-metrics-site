# from django.shortcuts import render

from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. Welcome to the sandbox.")


def sub_page(request):
    return HttpResponse("Here's a sub page.")
