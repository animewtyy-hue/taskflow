from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Task
import os
import json
from groq import Groq

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

@ai_bp.route('/')
@login_required
def index():
    return render_template('ai.html')

@ai_bp.route('/generate', methods=['POST'])
@login_required
def generate_tasks():
    data = request.get_json()
    goal = data.get('goal', '').strip()

    if not goal:
        return jsonify({'success': False, 'error': 'Goal is required'}), 400

    try:
        completion = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a project management expert. Always respond with valid JSON only, no extra text.'
                },
                {
                    'role': 'user',
                    'content': f'''Generate 5-8 practical tasks to achieve this goal: "{goal}"

Respond ONLY with a JSON array like this:
[
  {{
    "title": "Task title here",
    "description": "Brief description here",
    "priority": "high"
  }}
]

Rules:
- title: max 50 characters
- description: max 100 characters
- priority: only low, medium, or high
- No extra text, only the JSON array'''
                }
            ],
            temperature=0.7,
            max_tokens=1024,
        )

        response_text = completion.choices[0].message.content.strip()

        # تنظيف الرد
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]

        tasks_data = json.loads(response_text)

        return jsonify({
            'success': True,
            'tasks':   tasks_data,
            'goal':    goal
        })

    except json.JSONDecodeError:
        return jsonify({
            'success': False,
            'error': 'AI response error, please try again'
        }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/save', methods=['POST'])
@login_required
def save_tasks():
    data  = request.get_json()
    tasks = data.get('tasks', [])

    if not tasks:
        return jsonify({'success': False, 'error': 'No tasks'}), 400

    saved = 0
    for task_data in tasks:
        task = Task(
            title       = task_data.get('title', ''),
            description = task_data.get('description', ''),
            priority    = task_data.get('priority', 'medium'),
            status      = 'todo',
            user_id     = current_user.id
        )
        db.session.add(task)
        saved += 1

    db.session.commit()
    return jsonify({
        'success': True,
        'saved':   saved,
        'message': f'{saved} tasks saved successfully'
    })