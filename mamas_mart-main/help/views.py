from django.shortcuts import render

def help_index(request):
    return render(request, 'help/help_index.html')
