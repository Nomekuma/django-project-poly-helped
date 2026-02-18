from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'pages/home.html')

def about(request):
    return render(request, 'pages/about.html')

def members(request):
    return render(request, 'pages/members.html')

def contact(request):
    return render(request, 'pages/contact.html')