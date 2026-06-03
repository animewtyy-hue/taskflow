import os
from app import create_app, db
from flask import redirect, url_for

app = create_app()

@app.route('/')
def home():
    return redirect(url_for('auth.landing'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ قاعدة البيانات جاهزة!")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)