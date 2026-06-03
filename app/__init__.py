from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from config import Config

babel = Babel()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app)


    def get_local():
        return session.get('lang', 'ar')
    
    babel.init_app(app, locale_selector=get_local)
    # قاموس الترجمة
    translations = {
        'ar': {
            'dashboard':    'لوحة التحكم',
            'tasks':        'المهام',
            'projects':     'المشاريع',
            'statistics':   'الإحصائيات',
            'teams':        'الفرق',
            'notifications':'الإشعارات',
            'profile':      'الملف الشخصي',
            'logout':       'تسجيل الخروج',
            'new_task':     'مهمة جديدة',
            'edit_task':    'تعديل المهمة',
            'delete':       'حذف',
            'edit':         'تعديل',
            'save':         'حفظ',
            'cancel':       'إلغاء',
            'welcome':      'مرحباً',
            'total':        'الإجمالي',
            'done':         'مكتملة',
            'in_progress':  'قيد التنفيذ',
            'todo':         'قيد الانتظار',
            'progress':     'نسبة الإنجاز',
            'recent_tasks': 'آخر المهام',
            'task':         'المهمة',
            'priority':     'الأولوية',
            'status':       'الحالة',
            'date':         'التاريخ',
            'export_pdf':   'تصدير PDF',
            'export_excel': 'تصدير Excel',
            'no_tasks':     'لا توجد مهام بعد',
            'add_task':     'إضافة مهمة',
            'description':  'الوصف',
            'due_date':     'تاريخ الاستحقاق',
            'project':      'المشروع',
            'no_project':   'بدون مشروع',
            'members':      'الأعضاء',
            'invite':       'دعوة',
            'back':         'رجوع',
            'admin':        'الإدارة',
        },
        'en': {
            'dashboard':    'Dashboard',
            'tasks':        'Tasks',
            'projects':     'Projects',
            'statistics':   'Statistics',
            'teams':        'Teams',
            'notifications':'Notifications',
            'profile':      'Profile',
            'logout':       'Logout',
            'new_task':     'New Task',
            'edit_task':    'Edit Task',
            'delete':       'Delete',
            'edit':         'Edit',
            'save':         'Save',
            'cancel':       'Cancel',
            'welcome':      'Welcome',
            'total':        'Total',
            'done':         'Done',
            'in_progress':  'In Progress',
            'todo':         'Todo',
            'progress':     'Progress',
            'recent_tasks': 'Recent Tasks',
            'task':         'Task',
            'priority':     'Priority',
            'status':       'Status',
            'date':         'Date',
            'export_pdf':   'Export PDF',
            'export_excel': 'Export Excel',
            'no_tasks':     'No tasks yet',
            'add_task':     'Add Task',
            'description':  'Description',
            'due_date':     'Due Date',
            'project':      'Project',
            'no_project':   'No Project',
            'members':      'Members',
            'invite':       'Invite',
            'back':         'Back',
            'admin':        'Admin',
        }
    }

    @app.context_processor
    def inject_translations():
        lang = session.get('lang', 'ar')
        return dict(t=translations[lang], lang=lang)
    
    @app.route('/lang/<lang>')
    def set_lang(lang):
        from flask import redirect, request
        session['lang'] = lang if lang in ['ar', 'en'] else 'ar'
        return redirect(request.referrer or '/')

    from app.routes.auth import auth
    from app.routes.dashboard import dashboard
    from app.routes.api import api
    from app.routes.admin import admin_bp
    from app.routes.team import team_bp
    from app.routes.ai_routes import ai_bp
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(api)
    app.register_blueprint(admin_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(ai_bp)

    return app

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))