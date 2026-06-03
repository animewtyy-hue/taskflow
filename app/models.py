from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80), unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    role       = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks      = db.relationship('Task', backref='owner', lazy=True)

class Project(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    tasks       = db.relationship('Task', backref='project', lazy=True)

class Task(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status      = db.Column(db.String(20), default='todo')
    priority    = db.Column(db.String(20), default='medium')
    due_date    = db.Column(db.DateTime)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'))
    project_id  = db.Column(db.Integer, db.ForeignKey('project.id'))
    comments = db.relationship('Comment', backref='task', lazy=True, cascade='all, delete-orphan')
class Comment(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'))
    task_id    = db.Column(db.Integer, db.ForeignKey('task.id'))
    author     = db.relationship('User', backref='comments')
    
class Team(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id   = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner      = db.relationship('User', backref='owned_teams')
    members    = db.relationship('TeamMember', backref='team',
                                  lazy=True,
                                  cascade='all, delete-orphan')

class TeamMember(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    team_id   = db.Column(db.Integer, db.ForeignKey('team.id'))
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'))
    role      = db.Column(db.String(20), default='member')
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    user      = db.relationship('User', backref='team_memberships')

class TeamInvite(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    team_id    = db.Column(db.Integer, db.ForeignKey('team.id'))
    email      = db.Column(db.String(120), nullable=False)
    token      = db.Column(db.String(100), unique=True)
    accepted   = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    team       = db.relationship('Team', backref='invites')        
class Notification(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'))
    message    = db.Column(db.String(255), nullable=False)
    link       = db.Column(db.String(255))
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user       = db.relationship('User', backref='notifications')