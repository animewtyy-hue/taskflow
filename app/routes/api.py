from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Task, Project

api = Blueprint('api', __name__, url_prefix='/api/v1')

# ─── Helper ───────────────────────────────────────────
def task_to_dict(task):
    return {
        'id':          task.id,
        'title':       task.title,
        'description': task.description,
        'status':      task.status,
        'priority':    task.priority,
        'due_date':    task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
        'project_id':  task.project_id,
        'created_at':  task.created_at.strftime('%Y-%m-%d %H:%M')
    }

# ─── Tasks ────────────────────────────────────────────

@api.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify({'success': True,
                    'tasks': [task_to_dict(t) for t in tasks]})

@api.route('/tasks/<int:id>', methods=['GET'])
@login_required
def get_task(id):
    task = Task.query.get_or_404(id)
    return jsonify({'success': True, 'task': task_to_dict(task)})

@api.route('/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'success': False, 'error': 'العنوان مطلوب'}), 400

    task = Task(
        title       = data['title'],
        description = data.get('description', ''),
        status      = data.get('status', 'todo'),
        priority    = data.get('priority', 'medium'),
        user_id     = current_user.id,
        project_id  = data.get('project_id')
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'success': True, 'task': task_to_dict(task)}), 201

@api.route('/tasks/<int:id>', methods=['PATCH'])
@login_required
def update_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'غير مصرح'}), 403

    data = request.get_json()
    if 'status'      in data: task.status      = data['status']
    if 'priority'    in data: task.priority    = data['priority']
    if 'title'       in data: task.title       = data['title']
    if 'description' in data: task.description = data['description']

    db.session.commit()
    return jsonify({'success': True, 'task': task_to_dict(task)})

@api.route('/tasks/<int:id>', methods=['DELETE'])
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'غير مصرح'}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم الحذف'})

# ─── Stats ────────────────────────────────────────────

@api.route('/stats', methods=['GET'])
@login_required
def get_stats():
    uid = current_user.id
    return jsonify({
        'success': True,
        'stats': {
            'total':       Task.query.filter_by(user_id=uid).count(),
            'todo':        Task.query.filter_by(user_id=uid, status='todo').count(),
            'in_progress': Task.query.filter_by(user_id=uid, status='in_progress').count(),
            'done':        Task.query.filter_by(user_id=uid, status='done').count(),
        }
    })

# ─── Projects ─────────────────────────────────────────

@api.route('/projects', methods=['GET'])
@login_required
def get_projects():
    projects = Project.query.all()
    return jsonify({
        'success': True,
        'projects': [{'id': p.id, 'name': p.name} for p in projects]
    })