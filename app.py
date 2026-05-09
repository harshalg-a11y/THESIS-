from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g, send_from_directory
import os
import random
import uuid
from werkzeug.utils import secure_filename
from db import get_db, query_db, execute_db, init_db

app = Flask(__name__)
app.secret_key = 'super-secret-key-for-academic-sophistication'

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')

    from db import hash_password
    hashed = hash_password(password)

    user = query_db("SELECT * FROM users WHERE username = ? AND password = ? AND role = ?",
                   [username, hashed, role], one=True)

    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['full_name'] = user['full_name']
        return redirect(url_for('dashboard'))

    return render_template('login.html', error="Invalid credentials or role")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    role = session['role']
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'sender':
        return redirect(url_for('sender_dashboard'))
    else:
        return redirect(url_for('receiver_dashboard'))

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('dashboard'))

    stats = {
        'users': query_db("SELECT COUNT(*) as count FROM users", one=True)['count'],
        'requests': query_db("SELECT COUNT(*) as count FROM thesis_requests", one=True)['count'],
        'messages': query_db("SELECT COUNT(*) as count FROM messages", one=True)['count']
    }

    requests = query_db('''
        SELECT r.*, u1.full_name as student_name, u2.full_name as expert_name
        FROM thesis_requests r
        JOIN users u1 ON r.receiver_id = u1.id
        LEFT JOIN users u2 ON r.sender_id = u2.id
        ORDER BY r.created_at DESC
    ''')

    return render_template('dashboards/admin.html', stats=stats, requests=requests)

@app.route('/sender')
def sender_dashboard():
    if session.get('role') != 'sender': return redirect(url_for('dashboard'))

    requests = query_db('''
        SELECT r.*, u.full_name as student_name
        FROM thesis_requests r
        JOIN users u ON r.receiver_id = u.id
        WHERE r.sender_id = ?
        ORDER BY r.created_at DESC
    ''', [session['user_id']])

    return render_template('dashboards/sender.html', requests=requests)

@app.route('/receiver')
def receiver_dashboard():
    if session.get('role') != 'receiver': return redirect(url_for('dashboard'))

    requests = query_db('''
        SELECT r.*, u.full_name as expert_name
        FROM thesis_requests r
        LEFT JOIN users u ON r.sender_id = u.id
        WHERE r.receiver_id = ?
        ORDER BY r.created_at DESC
    ''', [session['user_id']])

    return render_template('dashboards/receiver.html', requests=requests)

# API Endpoints
@app.route('/api/requests', methods=['POST'])
def create_request():
    if session.get('role') != 'receiver': return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')

    # Supreme Randomizer Engine v2: Weighted Load Score
    experts = query_db("SELECT id, full_name, experience_level FROM users WHERE role = 'sender'")

    expert_scores = []
    for exp in experts:
        active_tasks = query_db("SELECT COUNT(*) as count FROM thesis_requests WHERE sender_id = ? AND status != 'delivered'",
                                [exp['id']], one=True)['count']
        # Weighted Score = Active Tasks / Experience Level (Higher experience handles more)
        # We add 1 to experience to avoid division by zero if it was 0, but here it's 1-3.
        score = active_tasks / exp['experience_level']
        expert_scores.append({'id': exp['id'], 'full_name': exp['full_name'], 'score': score})

    # Find minimum score
    min_score = min(e['score'] for e in expert_scores)
    best_experts = [e for e in expert_scores if e['score'] == min_score]
    assigned_expert = random.choice(best_experts)

    # Atomic Transaction
    from db import DB_TYPE
    db = get_db()
    try:
        if DB_TYPE == 'mysql':
            db.begin()
        else:
            db.execute("BEGIN TRANSACTION")

        execute_db("INSERT INTO thesis_requests (title, description, receiver_id, sender_id) VALUES (?, ?, ?, ?)",
                   [title, description, session['user_id'], assigned_expert['id']])
        execute_db("INSERT INTO audit_logs (user_id, action) VALUES (?, ?)",
                   [session['user_id'], f"Created thesis request: {title} assigned to {assigned_expert['full_name']}"])

        db.commit()
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

    return jsonify({
        'success': True,
        'expert_name': assigned_expert['full_name']
    })

@app.route('/api/guidelines', methods=['POST'])
def push_guideline():
    if session.get('role') != 'admin': return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    execute_db("INSERT INTO guidelines (admin_id, content) VALUES (?, ?)", [session['user_id'], data.get('content')])
    return jsonify({'success': True})

@app.route('/chat/<int:request_id>')
def chat_hub(request_id):
    if 'user_id' not in session: return redirect(url_for('index'))

    thesis = query_db("SELECT * FROM thesis_requests WHERE id = ?", [request_id], one=True)
    if not thesis: return redirect(url_for('dashboard'))

    # Security: check if user belongs to this chat
    if session['role'] != 'admin' and session['user_id'] != thesis['receiver_id'] and session['user_id'] != thesis['sender_id']:
        return redirect(url_for('dashboard'))

    other_party_id = thesis['sender_id'] if session['user_id'] == thesis['receiver_id'] else thesis['receiver_id']
    other_party = query_db("SELECT full_name FROM users WHERE id = ?", [other_party_id], one=True)

    return render_template('chat.html', thesis=thesis, other_party=other_party)

def is_participant(request_id):
    if session.get('role') == 'admin': return True
    thesis = query_db("SELECT * FROM thesis_requests WHERE id = ?", [request_id], one=True)
    if not thesis: return False
    return session.get('user_id') in [thesis['receiver_id'], thesis['sender_id']]

@app.route('/api/messages/<int:request_id>', methods=['GET', 'POST'])
def handle_messages(request_id):
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 403
    if not is_participant(request_id): return jsonify({'error': 'Forbidden'}), 403

    if request.method == 'POST':
        data = request.get_json()
        execute_db("INSERT INTO messages (request_id, sender_id, content) VALUES (?, ?, ?)",
                   [request_id, session['user_id'], data.get('content')])
        return jsonify({'success': True})

    messages = query_db('''
        SELECT m.*, u.role
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.request_id = ?
        ORDER BY m.created_at ASC
    ''', [request_id])

    return jsonify([dict(m) for m in messages])

@app.route('/api/lounge', methods=['GET', 'POST'])
def handle_lounge():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'POST':
        data = request.get_json()
        execute_db("INSERT INTO messages (sender_id, content, is_lounge) VALUES (?, ?, 1)",
                   [session['user_id'], data.get('content')])
        return jsonify({'success': True})

    messages = query_db('''
        SELECT m.*, u.full_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.is_lounge = 1
        ORDER BY m.created_at ASC
    ''')

    return jsonify([dict(m) for m in messages])

@app.route('/lounge')
def lounge():
    if 'user_id' not in session: return redirect(url_for('index'))
    return render_template('lounge.html')

@app.route('/api/guidelines', methods=['GET'])
def get_guidelines():
    guidelines = query_db("SELECT * FROM guidelines ORDER BY created_at DESC")
    return jsonify([dict(g) for g in guidelines])

@app.route('/api/files/<int:request_id>', methods=['GET', 'POST'])
def handle_files(request_id):
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 403
    if not is_participant(request_id): return jsonify({'error': 'Forbidden'}), 403

    if request.method == 'POST':
        if 'file' not in request.files: return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '': return jsonify({'error': 'No selected file'}), 400

        filename = secure_filename(file.filename)
        file_uuid = str(uuid.uuid4())
        file_path = os.path.join('uploads', file_uuid + '_' + filename)
        file.save(file_path)

        execute_db("INSERT INTO files (uuid, request_id, original_name, file_path) VALUES (?, ?, ?, ?)",
                   [file_uuid, request_id, filename, file_path])

        return jsonify({'success': True})

    files = query_db("SELECT * FROM files WHERE request_id = ?", [request_id])
    return jsonify([dict(f) for f in files])

@app.route('/download/<file_uuid>')
def download_file(file_uuid):
    if 'user_id' not in session: return redirect(url_for('index'))
    file_info = query_db("SELECT * FROM files WHERE uuid = ?", [file_uuid], one=True)
    if not file_info: return "File not found", 404

    directory = os.path.dirname(file_info['file_path'])
    filename = os.path.basename(file_info['file_path'])
    return send_from_directory(directory, filename, as_attachment=True, download_name=file_info['original_name'])

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, port=5000)
