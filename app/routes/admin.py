from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, Task, Project

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ─── Decorator للتحقق من صلاحية الأدمن ───────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash(' غير مصرح لك بالدخول', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated

# ─── لوحة الأدمن ──────────────────────────────────────
@admin_bp.route('/')
@login_required
@admin_required
def index():
    stats = {
        'users':    User.query.count(),
        'tasks':    Task.query.count(),
        'projects': Project.query.count(),
        'done':     Task.query.filter_by(status='done').count()
    }
    users        = User.query.order_by(User.created_at.desc()).all()
    recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(10).all()
    return render_template('admin.html',
                           stats=stats,
                           users=users,
                           recent_tasks=recent_tasks)

# ─── تبديل صلاحية المستخدم ────────────────────────────
@admin_bp.route('/users/<int:id>/toggle-role', methods=['POST'])
@login_required
@admin_required
def toggle_role(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('لا يمكنك تغيير صلاحيتك الخاصة', 'warning')
        return redirect(url_for('admin.index'))
    user.role = 'admin' if user.role == 'user' else 'user'
    db.session.commit()
    flash(f' تم تغيير صلاحية {user.username}', 'success')
    return redirect(url_for('admin.index'))

# ─── حذف مستخدم ───────────────────────────────────────
@admin_bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك من هنا', 'warning')
        return redirect(url_for('admin.index'))
    Task.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f' تم حذف المستخدم {user.username}', 'warning')
    return redirect(url_for('admin.index'))