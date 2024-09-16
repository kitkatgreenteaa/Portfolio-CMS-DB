from flask import Flask, request, send_from_directory, jsonify, render_template, make_response
from flask_cors import CORS
from datetime import datetime
import os
import uuid
import sqlite3

app = Flask(__name__, static_folder='FE/assets', template_folder='FE')
CORS(app)

# Paths and configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'skill_icons')
CV_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'cv')
DB_PATH = os.path.join(BASE_DIR, 'skills.db')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CV_UPLOAD_FOLDER'] = CV_UPLOAD_FOLDER

# Ensure the upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CV_UPLOAD_FOLDER'], exist_ok=True)

# Database connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Serve main and admin pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# ----- Skills Section Routes -----
# API to get the list of skills
@app.route('/api/skills', methods=['GET'])
def get_skills():
    conn = get_db_connection()
    skills = conn.execute('SELECT * FROM skills').fetchall()
    conn.close()

    # Convert rows to dictionary format for JSON serialization
    skills_list = [dict(skill) for skill in skills]
    for skill in skills_list:
        skill['icon_url'] = f"http://127.0.0.1:5000/uploads/skill_icons/{skill['icon']}"
    return jsonify(skills_list)

# API to add a new skill
@app.route('/api/skills', methods=['POST'])
def add_skill():
    name = request.form.get('name')
    level = request.form.get('level')
    file = request.files.get('icon')

    if not name or not level or not file:
        return jsonify({'status': 'error', 'message': 'Invalid input'}), 400

    # Save the file with a unique name to prevent overwriting
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Add skill to the SQLite database
    skill_id = str(uuid.uuid4())
    conn = get_db_connection()
    conn.execute('INSERT INTO skills (id, name, level, icon) VALUES (?, ?, ?, ?)',
                 (skill_id, name, int(level), filename))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': 'Skill added successfully'}), 201

# API to remove a skill
@app.route('/api/skills/<skill_id>', methods=['DELETE'])
def remove_skill(skill_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM skills WHERE id = ?', (skill_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Skill removed successfully'})

# ----- About Section Routes -----
# API to get the "About" section
@app.route('/api/about', methods=['GET'])
def get_about():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT title, description FROM about WHERE id = 1")
        row = cursor.fetchone()
        
        if row:
            return jsonify({"title": row['title'], "description": row['description']})
        else:
            return jsonify({"title": "", "description": ""})
    except Exception as e:
        print(f"Error fetching about section: {e}")
        return jsonify({"message": "Error fetching about section", "status": "error"})
    finally:
        conn.close()

# API to update the "About" section
@app.route('/api/about', methods=['POST'])
def update_about():
    data = request.get_json()
    if 'title' in data and 'description' in data:
        try:
            conn = get_db_connection()
            conn.execute('UPDATE about SET title = ?, description = ? WHERE id = 1', (data['title'], data['description']))
            conn.commit()
            return jsonify({'status': 'success', 'message': 'About section updated successfully'})
        except Exception as e:
            print(f"Error updating about section: {e}")
            return jsonify({'status': 'error', 'message': 'Error updating about section'})
        finally:
            conn.close()
    return jsonify({'status': 'error', 'message': 'Invalid input'}), 400

# ----- CV Section Routes -----
# API to get the CV status
@app.route('/api/cv_status', methods=['GET'])
def get_cv_status():
    conn = get_db_connection()
    cv = conn.execute('SELECT filename, upload_date FROM cv WHERE id = 1').fetchone()
    conn.close()

    if cv:
        return jsonify({
            'status': 'exists',
            'name': cv['filename'],
            'download_url': f"/uploads/cv/{cv['filename']}",
            'upload_date': cv['upload_date'] if cv['upload_date'] else 'Date not tracked'
        })
    return jsonify({'status': 'not_found'})

# API to upload a CV
@app.route('/api/upload_cv', methods=['POST'])
def upload_cv():
    file = request.files.get('cv')
    if not file:
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400

    # Save the CV
    filename = file.filename
    file.save(os.path.join(app.config['CV_UPLOAD_FOLDER'], filename))

    # Store the current date and time
    upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Save CV info to the database (replace if one already exists)
    conn = get_db_connection()
    conn.execute('REPLACE INTO cv (id, filename, upload_date) VALUES (1, ?, ?)', (filename, upload_date))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': 'CV uploaded successfully'}), 201

# Route to serve CVs
@app.route('/uploads/cv/<filename>')
def get_cv(filename):
    return send_from_directory(app.config['CV_UPLOAD_FOLDER'], filename)

# ----- Social Media Links Routes -----
# API to get social media links
@app.route('/api/social_links', methods=['GET'])
def get_social_links():
    conn = get_db_connection()
    social_links = conn.execute('SELECT platform, url FROM social_links').fetchall()
    conn.close()

    # Convert rows to dictionary format for JSON serialization
    social_links_list = [dict(link) for link in social_links]
    return jsonify(social_links_list)

# API to add a new social media link
# API to add a new social media link
@app.route('/api/social_links', methods=['POST'])
def add_social_link():
    data = request.get_json()
    platform = data.get('platform')
    url = data.get('url')

    if not platform or not url:
        return jsonify({'status': 'error', 'message': 'Invalid input'}), 400

    link_id = str(uuid.uuid4())
    conn = get_db_connection()
    conn.execute('INSERT INTO social_links (id, platform, url) VALUES (?, ?, ?)',
                 (link_id, platform, url))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Social media link added successfully'}), 201

# API to delete a social media link
@app.route('/api/social_links/<link_id>', methods=['DELETE'])
def delete_social_link(link_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM social_links WHERE id = ?', (link_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Social media link deleted successfully'})

# ----- Route to Serve Skill Icons -----
@app.route('/uploads/skill_icons/<filename>')
def get_skill_icon(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
