from django import template
from django.http import HttpResponse
from django.template import loader
from django.views.generic.base import TemplateView
from django.shortcuts import render


def index(request):
    template_name = 'epilepsy12index.html'
    return render(request, template_name, {})
