from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Case, When, IntegerField
from django.core.paginator import Paginator

from .models import Todo

from accounts.models import Profile


@login_required
def todo_list(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    search = request.GET.get(
        'search',
        ''
    ).strip()

    status = request.GET.get(
        'status',
        ''
    )

    priority = request.GET.get(
        'priority',
        ''
    )

    category = request.GET.get(
        'category',
        ''
    )

    due = request.GET.get(
        'due',
        ''
    )

    sort = request.GET.get(
        'sort',
        'priority'
    )


    # Base Todo Query

    todos = Todo.objects.filter(
        user=request.user
    )


    # Search

    if search:

        todos = todos.filter(
            title__icontains=search
        )


    # Status Filter

    if status == 'completed':

        todos = todos.filter(
            completed=True
        )

    elif status == 'pending':

        todos = todos.filter(
            completed=False
        )


    # Priority Filter

    if priority in [
        'low',
        'medium',
        'high'
    ]:

        todos = todos.filter(
            priority=priority
        )


    # Category Filter

    if category in [
        'work',
        'study',
        'personal',
        'shopping',
        'health',
        'other'
    ]:

        todos = todos.filter(
            category=category
        )


    # Date Filters

    today = timezone.localdate()

    if due == 'overdue':

        todos = todos.filter(
            completed=False,
            due_date__lt=today
        )

    elif due == 'today':

        todos = todos.filter(
            completed=False,
            due_date=today
        )

    elif due == 'upcoming':

        todos = todos.filter(
            completed=False,
            due_date__gt=today
        )

    elif due == 'none':

        todos = todos.filter(
            due_date__isnull=True
        )


    # Sorting

    if sort == 'due_date':

        todos = todos.order_by(
            'due_date',
            '-created_at'
        )

    elif sort == 'created':

        todos = todos.order_by(
            '-created_at'
        )

    elif sort == 'title':

        todos = todos.order_by(
            'title'
        )

    else:

        todos = todos.annotate(
            priority_order=Case(
                When(
                    priority='high',
                    then=1
                ),
                When(
                    priority='medium',
                    then=2
                ),
                When(
                    priority='low',
                    then=3
                ),
                output_field=IntegerField()
            )
        ).order_by(
            'priority_order',
            'due_date',
            '-created_at'
        )


    # Pagination

    paginator = Paginator(
        todos,
        10
    )

    page_number = request.GET.get(
        'page'
    )

    page_obj = paginator.get_page(
        page_number
    )


    # Statistics

    total_todos = Todo.objects.filter(
        user=request.user
    ).count()

    completed_todos = Todo.objects.filter(
        user=request.user,
        completed=True
    ).count()

    pending_todos = Todo.objects.filter(
        user=request.user,
        completed=False
    ).count()


    # Completion Percentage

    if total_todos > 0:

        completion_percentage = round(
            (completed_todos / total_todos) * 100
        )

    else:

        completion_percentage = 0


    # Today's Statistics

    today_todos = Todo.objects.filter(
        user=request.user,
        due_date=today,
        completed=False
    ).count()

    overdue_todos = Todo.objects.filter(
        user=request.user,
        due_date__lt=today,
        completed=False
    ).count()


    return render(
        request,
        'dashboard.html',
        {
            'todos': page_obj,
            'page_obj': page_obj,

            'profile': profile,

            'total_todos': total_todos,
            'completed_todos': completed_todos,
            'pending_todos': pending_todos,

            'completion_percentage': completion_percentage,

            'today_todos': today_todos,
            'overdue_todos': overdue_todos,

            'search': search,
            'status': status,
            'priority': priority,
            'category': category,
            'due': due,
            'sort': sort,

            'today': today
        }
    )


@login_required
def add_todo(request):

    if request.method == 'POST':

        title = request.POST.get(
            'title',
            ''
        ).strip()

        description = request.POST.get(
            'description',
            ''
        ).strip()

        due_date = request.POST.get(
            'due_date'
        ) or None

        priority = request.POST.get(
            'priority',
            'medium'
        )

        category = request.POST.get(
            'category',
            'other'
        )


        # Validate Title

        if not title:

            messages.error(
                request,
                'Todo title cannot be empty. ❌'
            )

            return redirect(
                'dashboard'
            )


        # Validate Priority

        if priority not in [
            'low',
            'medium',
            'high'
        ]:

            priority = 'medium'


        # Validate Category

        if category not in [
            'work',
            'study',
            'personal',
            'shopping',
            'health',
            'other'
        ]:

            category = 'other'


        # Create Todo

        Todo.objects.create(
            user=request.user,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            category=category
        )


        messages.success(
            request,
            'Todo added successfully! ✅'
        )


    return redirect(
        'dashboard'
    )


@login_required
def toggle_todo(request, todo_id):

    todo = get_object_or_404(
        Todo,
        id=todo_id,
        user=request.user
    )


    if request.method == 'POST':

        todo.completed = not todo.completed

        todo.save()


        if todo.completed:

            messages.success(
                request,
                'Todo marked as completed! ✅'
            )

        else:

            messages.info(
                request,
                'Todo marked as pending! ⏳'
            )


    return redirect(
        'dashboard'
    )


@login_required
def delete_todo(request, todo_id):

    todo = get_object_or_404(
        Todo,
        id=todo_id,
        user=request.user
    )


    if request.method == 'POST':

        todo.delete()

        messages.success(
            request,
            'Todo deleted successfully! 🗑️'
        )


    return redirect(
        'dashboard'
    )


@login_required
def edit_todo(request, todo_id):

    todo = get_object_or_404(
        Todo,
        id=todo_id,
        user=request.user
    )


    if request.method == 'POST':

        title = request.POST.get(
            'title',
            ''
        ).strip()

        description = request.POST.get(
            'description',
            ''
        ).strip()

        due_date = request.POST.get(
            'due_date'
        ) or None

        priority = request.POST.get(
            'priority',
            'medium'
        )

        category = request.POST.get(
            'category',
            'other'
        )


        # Validate Title

        if not title:

            messages.error(
                request,
                'Todo title cannot be empty. ❌'
            )

            return redirect(
                'edit_todo',
                todo_id=todo.id
            )


        # Validate Priority

        if priority not in [
            'low',
            'medium',
            'high'
        ]:

            priority = 'medium'


        # Validate Category

        if category not in [
            'work',
            'study',
            'personal',
            'shopping',
            'health',
            'other'
        ]:

            category = 'other'


        # Update Todo

        todo.title = title
        todo.description = description
        todo.due_date = due_date
        todo.priority = priority
        todo.category = category

        todo.save()


        messages.success(
            request,
            'Todo updated successfully! ✏️'
        )


        return redirect(
            'dashboard'
        )


    return render(
        request,
        'edit_todo.html',
        {
            'todo': todo
        }
    )