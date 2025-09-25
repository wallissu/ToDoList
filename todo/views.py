from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Max, F
from django.utils import timezone
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import TodoForm, CustomUserCreationForm
from .models import Todo

def index(request):
    today = timezone.now().date()
    
    if request.user.is_authenticated:
        # Show user's cards if logged in
        columns = {
            'column1': {
                'name': 'To Do',
                'cards': Todo.objects.filter(user=request.user, column='column1').order_by('position')
            },
            'column2': {
                'name': 'Doing', 
                'cards': Todo.objects.filter(user=request.user, column='column2').order_by('position')
            },
            'column3': {
                'name': 'Done',
                'cards': Todo.objects.filter(user=request.user, column='column3').order_by('position')
            },
        }
    else:
        # Show empty columns for non-logged-in users
        columns = {
            'column1': {'name': 'To Do', 'cards': []},
            'column2': {'name': 'Doing', 'cards': []},
            'column3': {'name': 'Done', 'cards': []},
        }
    
    page = {
        "columns": columns,
        "title": "Trellado", 
        "today": today,
    }
    return render(request, 'todo/index.html', page)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('todo')  # Redirect to index after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'todo/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('todo')  # Redirect to index if already logged in
        
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('todo')  # Redirect to index after login
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'todo/login.html')

@login_required
def profile(request):
    # Optional: you can keep this view but add a link to go to index
    return render(request, 'todo/profile.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('login')

@login_required
def remove(request, id):
    item = get_object_or_404(Todo, id=id, user=request.user)
    item.delete()
    messages.info(request, "Task Removed!")
    return redirect('todo')

@login_required
def create(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user  # Set the user
            todo.column = 'column1'
            
            if not todo.created_in:
                todo.created_in = timezone.now()
                
            last_position = Todo.objects.filter(user=request.user, column='column1').aggregate(Max('position'))['position__max']
            todo.position = (last_position or 0) + 1
            todo.save()
            messages.success(request, 'Task created successfully!')
            return redirect('todo')
    else:
        form = TodoForm()
    return render(request, 'todo/create_card.html', {'form': form})

@login_required
def edit_card(request, id):
    todo = get_object_or_404(Todo, id=id, user=request.user)
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            edited_todo = form.save(commit=False)
            edited_todo.user = request.user  # Ensure user is preserved
            edited_todo.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('todo')
    else:
        form = TodoForm(instance=todo)
    return render(request, 'todo/edit_card.html', {'form': form})

@csrf_exempt
@require_POST
@login_required
def update_card_position(request):
    try:
        data = json.loads(request.body)
        card_id = data.get('card_id')
        new_column = data.get('column')
        new_position = int(data.get('position'))
        
        # Ensure the card belongs to the current user
        card = get_object_or_404(Todo, id=card_id, user=request.user)
        old_column = card.column
        old_position = card.position
        
        # If moving within the same column
        if old_column == new_column:
            if new_position > old_position:
                Todo.objects.filter(
                    user=request.user,
                    column=old_column,
                    position__gt=old_position,
                    position__lte=new_position
                ).update(position=F('position') - 1)
            else:
                Todo.objects.filter(
                    user=request.user,
                    column=old_column,
                    position__lt=old_position,
                    position__gte=new_position
                ).update(position=F('position') + 1)
        else:
            # Moving between columns
            Todo.objects.filter(
                user=request.user,
                column=old_column,
                position__gt=old_position
            ).update(position=F('position') - 1)
            
            Todo.objects.filter(
                user=request.user,
                column=new_column,
                position__gte=new_position
            ).update(position=F('position') + 1)
        
        # Update the moved card
        Todo.objects.filter(id=card_id, user=request.user).update(
            column=new_column,
            position=new_position
        )
        
        return JsonResponse({'status': 'success'})
    
    except Exception as e:
        print(f"Erro: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})