from flask import Flask, render_template, request, jsonify, send_file
from cryptography.fernet import Fernet
import os
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Existing key generation and crypto functions remain the same
def generate_key():
    return Fernet.generate_key()

def sanitize_filename(filename):
    return secure_filename(filename)

def encrypt_file(file_path, key, output_dir):
    cipher = Fernet(key)
    with open(file_path, 'rb') as file:
        file_data = file.read()
    encrypted_data = cipher.encrypt(file_data)
    
    encrypted_file_path = os.path.join(output_dir, f"encrypted_{os.path.basename(file_path)}")
    with open(encrypted_file_path, 'wb') as file:
        file.write(encrypted_data)
    
    return encrypted_file_path

def decrypt_file(encrypted_file_path, key, output_dir):
    cipher = Fernet(key)
    with open(encrypted_file_path, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = cipher.decrypt(encrypted_data)
    
    decrypted_file_path = os.path.join(output_dir, f"decrypted_{os.path.basename(encrypted_file_path)}")
    with open(decrypted_file_path, 'wb') as file:
        file.write(decrypted_data)
    
    return decrypted_file_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_files():
    if 'files' not in request.files:
        return jsonify({'status': 'error', 'message': 'No files selected'}), 400
    
    files = request.files.getlist('files')
    key = generate_key().decode()
    encrypted_files = []
    file_details = []
    
    uploads_dir = 'uploads'
    encrypted_dir = 'encrypted_files'
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(encrypted_dir, exist_ok=True)
    
    for file in files:
        if file.filename:
            sanitized_filename = sanitize_filename(file.filename)
            file_path = os.path.join(uploads_dir, sanitized_filename)
            
            try:
                file.save(file_path)
                encrypted_file = encrypt_file(file_path, key.encode(), encrypted_dir)
                encrypted_files.append(encrypted_file)
                
                # Get file size
                file_size = os.path.getsize(encrypted_file)
                file_details.append({
                    'name': os.path.basename(encrypted_file),
                    'size': f"{file_size / 1024:.1f} KB"
                })
            except Exception as e:
                return jsonify({'status': 'error', 'message': f"Error processing {sanitized_filename}: {str(e)}"}), 500
    
    return jsonify({
        'status': 'success',
        'key': key,
        'files': file_details
    })

@app.route('/decrypt', methods=['POST'])
def decrypt_file_request():
    if 'file' not in request.files or 'key' not in request.form:
        return jsonify({'status': 'error', 'message': 'Missing file or key'}), 400
    
    encrypted_files = request.files.getlist('file')
    key = request.form['key']
    encrypted_dir = 'encrypted_files'
    decrypted_dir = 'decrypted_files'
    
    os.makedirs(decrypted_dir, exist_ok=True)
    
    decrypted_files = []
    file_details = []
    
    try:
        for encrypted_file in encrypted_files:
            if encrypted_file.filename:
                file_path = os.path.join(encrypted_dir, sanitize_filename(encrypted_file.filename))
                encrypted_file.save(file_path)
                
                decrypted_file = decrypt_file(file_path, key.encode(), decrypted_dir)
                decrypted_files.append(decrypted_file)
                
                # Get file size
                file_size = os.path.getsize(decrypted_file)
                file_details.append({
                    'name': os.path.basename(decrypted_file),
                    'size': f"{file_size / 1024:.1f} KB"
                })
        
        return jsonify({
            'status': 'success',
            'files': file_details
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f"Error downloading file: {str(e)}"}), 500

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('encrypted_files', exist_ok=True)
    os.makedirs('decrypted_files', exist_ok=True)
    app.run(debug=True)