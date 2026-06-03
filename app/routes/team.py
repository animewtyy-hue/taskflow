from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Team, TeamMember, TeamInvite, User, Task
import secrets

team_bp = Blueprint('team', __name__, url_prefix='/team')

# ─── عرض الفريق ───────────────────────────────────────
@team_bp.route('/')
@login_required
def index():
    # الفرق التي أنشأها المستخدم
    owned_teams = Team.query.filter_by(owner_id=current_user.id).all()

    # الفرق التي هو عضو فيها
    memberships = TeamMember.query.filter_by(user_id=current_user.id).all()
    member_teams = [m.team for m in memberships
                    if m.team.owner_id != current_user.id]

    return render_template('team.html',
                           owned_teams=owned_teams,
                           member_teams=member_teams)

# ─── إنشاء فريق ───────────────────────────────────────
@team_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_team():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash(' اسم الفريق مطلوب', 'warning')
            return redirect(url_for('team.new_team'))

        new = Team(name=name, owner_id=current_user.id)
        db.session.add(new)
        db.session.flush()

        # إضافة المنشئ كعضو admin
        member = TeamMember(
            team_id = new.id,
            user_id = current_user.id,
            role    = 'admin'
        )
        db.session.add(member)
        db.session.commit()
        flash(' تم إنشاء الفريق!', 'success')
        return redirect(url_for('team.team_detail', id=new.id))

    return render_template('team_invite.html', mode='new')

# ─── تفاصيل الفريق ────────────────────────────────────
@team_bp.route('/<int:id>')
@login_required
def team_detail(id):
    team    = Team.query.get_or_404(id)
    members = TeamMember.query.filter_by(team_id=id).all()

    # التحقق أن المستخدم عضو
    is_member = TeamMember.query.filter_by(
        team_id=id, user_id=current_user.id).first()
    if not is_member:
        flash(' غير مصرح لك', 'danger')
        return redirect(url_for('team.index'))

    # مهام الفريق
    member_ids = [m.user_id for m in members]
    tasks      = Task.query.filter(
        Task.user_id.in_(member_ids)).order_by(
        Task.created_at.desc()).limit(10).all()

    invites = TeamInvite.query.filter_by(
        team_id=id, accepted=False).all()

    return render_template('team_detail.html',
                           team=team,
                           members=members,
                           tasks=tasks,
                           invites=invites,
                           is_owner=team.owner_id == current_user.id)

# ─── دعوة عضو ─────────────────────────────────────────
@team_bp.route('/<int:id>/invite', methods=['POST'])
@login_required
def invite_member(id):
    team  = Team.query.get_or_404(id)
    email = request.form.get('email', '').strip()

    if team.owner_id != current_user.id:
        flash(' فقط مالك الفريق يمكنه الدعوة', 'danger')
        return redirect(url_for('team.team_detail', id=id))

    # التحقق من وجود المستخدم
    user = User.query.filter_by(email=email).first()
    if not user:
        flash(' لا يوجد مستخدم بهذا البريد', 'warning')
        return redirect(url_for('team.team_detail', id=id))

    # التحقق أنه ليس عضواً بالفعل
    existing = TeamMember.query.filter_by(
        team_id=id, user_id=user.id).first()
    if existing:
        flash(' هذا المستخدم عضو بالفعل', 'warning')
        return redirect(url_for('team.team_detail', id=id))

    # إنشاء دعوة
    token  = secrets.token_urlsafe(32)
    invite = TeamInvite(team_id=id, email=email, token=token)
    db.session.add(invite)
    db.session.commit()

    flash(f' تم إرسال الدعوة إلى {email}', 'success')
    return redirect(url_for('team.team_detail', id=id))

# ─── قبول الدعوة ──────────────────────────────────────
@team_bp.route('/join/<token>')
@login_required
def join_team(token):
    invite = TeamInvite.query.filter_by(
        token=token, accepted=False).first_or_404()

    # إضافة العضو
    member = TeamMember(
        team_id = invite.team_id,
        user_id = current_user.id,
        role    = 'member'
    )
    db.session.add(member)
    invite.accepted = True
    db.session.commit()

    flash(' انضممت للفريق بنجاح!', 'success')
    return redirect(url_for('team.team_detail', id=invite.team_id))

# ─── حذف عضو ──────────────────────────────────────────
@team_bp.route('/<int:team_id>/remove/<int:user_id>', methods=['POST'])
@login_required
def remove_member(team_id, user_id):
    team = Team.query.get_or_404(team_id)
    if team.owner_id != current_user.id:
        flash(' غير مصرح', 'danger')
        return redirect(url_for('team.team_detail', id=team_id))

    member = TeamMember.query.filter_by(
        team_id=team_id, user_id=user_id).first()
    if member:
        db.session.delete(member)
        db.session.commit()
        flash(' تم حذف العضو', 'warning')

    return redirect(url_for('team.team_detail', id=team_id))

# ─── حذف فريق ─────────────────────────────────────────
@team_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_team(id):
    team = Team.query.get_or_404(id)
    if team.owner_id != current_user.id:
        flash(' غير مصرح', 'danger')
        return redirect(url_for('team.index'))

    db.session.delete(team)
    db.session.commit()
    flash(' تم حذف الفريق', 'warning')
    return redirect(url_for('team.index'))