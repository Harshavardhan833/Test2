from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader
from .models import EKA

def users(request):
    return HttpResponse("Users endpoint")
    
def index(request):
    users = EKA.objects.all().values()
    template = loader.get_template('index.html')
    context = {
        'users': users,
    }
    return HttpResponse(template.render(context, request))
def details(request, user_id):
    users = EKA.objects.get(id=user_id)
    template = loader.get_template('details.html')
    context = {
        'users': users,
    }
    return HttpResponse(template.render(context, request))
def main(request):
    template = loader.get_template('main.html')
    return HttpResponse(template.render())

def testing(request):
  template = loader.get_template('template.html')
  context = {
    'fruits': ['Apple', 'Banana', 'Cherry'],   
  }
  return HttpResponse(template.render(context, request))


