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
    app.run(debug=True)