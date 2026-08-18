from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Todo

todos_bp = Blueprint('todos', __name__)

PRIORITIES = ['high', 'medium', 'low']


def _sorted_todos(todos):
    return sorted(
        todos,
        key=lambda t: (t.completed, t.due_date is None, t.due_date or date.max)
    )


@todos_bp.route('/')
@login_required
def index():
    today = date.today()
    cat_filter = request.args.get('category', '').strip().lower()

    all_todos = Todo.query.filter_by(user_id=current_user.id).all()

    # Unique categories for the filter tabs
    categories = sorted(set(t.category.lower() for t in all_todos if t.category))

    if cat_filter and cat_filter != 'all':
        display = [t for t in all_todos if (t.category or '').lower() == cat_filter]
    else:
        display = all_todos

    tasks = _sorted_todos(display)
    reminders = [
        t for t in all_todos
        if not t.completed and t.due_date and t.due_date <= today
    ]
    return render_template(
        'todos/index.html',
        tasks=tasks,
        reminders=reminders,
        today=today,
        categories=categories,
        active_category=cat_filter,
    )


@todos_bp.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form.get('title', '').strip()
    if not title:
        flash('Task title cannot be empty.', 'warning')
        return redirect(url_for('todos.index'))

    due_date = None
    due_str = request.form.get('due_date', '')
    if due_str:
        try:
            due_date = date.fromisoformat(due_str)
        except ValueError:
            pass

    priority = request.form.get('priority', 'medium')
    if priority not in PRIORITIES:
        priority = 'medium'

    category = request.form.get('category', '').strip().lower()
    notes = request.form.get('notes', '').strip()

    todo = Todo(
        user_id=current_user.id,
        title=title,
        due_date=due_date,
        priority=priority,
        category=category,
        notes=notes,
    )
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for('todos.index', category=category) if category else url_for('todos.index'))


@todos_bp.route('/toggle/<int:todo_id>', methods=['POST'])
@login_required
def toggle(todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first_or_404()
    todo.completed = not todo.completed
    db.session.commit()
    cat = request.form.get('_category', '')
    return redirect(url_for('todos.index', category=cat) if cat else url_for('todos.index'))


@todos_bp.route('/edit/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def edit(todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Task title cannot be empty.', 'warning')
            return redirect(url_for('todos.edit', todo_id=todo_id))
        todo.title = title
        due_str = request.form.get('due_date', '')
        try:
            todo.due_date = date.fromisoformat(due_str) if due_str else None
        except ValueError:
            todo.due_date = None
        priority = request.form.get('priority', 'medium')
        todo.priority = priority if priority in PRIORITIES else 'medium'
        todo.category = request.form.get('category', '').strip().lower()
        todo.notes = request.form.get('notes', '').strip()
        db.session.commit()
        flash('Task updated.', 'success')
        return redirect(url_for('todos.index'))
    return render_template('todos/edit.html', todo=todo, priorities=PRIORITIES)


@todos_bp.route('/delete/<int:todo_id>', methods=['POST'])
@login_required
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first_or_404()
    db.session.delete(todo)
    db.session.commit()
    cat = request.form.get('_category', '')
    return redirect(url_for('todos.index', category=cat) if cat else url_for('todos.index'))
