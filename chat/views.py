from django.shortcuts import render

def index(request):
    return render(request, 'room.html', {})

def room(request, room_name):
    return render(request, 'roomy.html', {
        'room_name': room_name
    })