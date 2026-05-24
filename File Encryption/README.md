# File Encryption Web App

A Flask-based web application that lets you **encrypt and decrypt files** right in your browser using military-grade symmetric encryption (Fernet / AES-128-CBC).

## Features

- 🔒 **Encrypt** one or more files at once — a unique encryption key is generated automatically.
- 🔓 **Decrypt** previously encrypted files using the saved key.
- 🖱️ **Drag-and-drop** file upload area (or click to browse).
- 📋 **One-click copy** for the generated encryption key.
- 📁 Supports **multiple files** per operation.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| Encryption | `cryptography` library — Fernet (AES-128-CBC + HMAC-SHA256) |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Icons | Font Awesome 6 |
| Clipboard | clipboard.js |

## How It Works

### Encryption

1. The user selects or drags files onto the **Encrypt** tab and clicks **Encrypt Files**.
2. The browser sends the files to the Flask `/encrypt` endpoint via a `multipart/form-data` POST request.
3. The server:
   - Generates a fresh **Fernet key** (a URL-safe base64-encoded 32-byte key).
   - Saves each uploaded file to the `uploads/` directory.
   - Reads each file, encrypts its bytes with the Fernet cipher, and writes the result as `encrypted_<original_name>` inside `encrypted_files/`.
4. The server returns the **encryption key** and a list of encrypted file names/sizes as JSON.
5. The UI displays the key (which the user must **save**) and the list of encrypted files.

### Decryption

1. The user switches to the **Decrypt** tab, uploads the encrypted file(s), pastes the saved key, and clicks **Decrypt Files**.
2. The browser sends the files and key to the Flask `/decrypt` endpoint.
3. The server:
   - Saves the uploaded files to `encrypted_files/`.
   - Decrypts each file using the provided Fernet key and writes the result as `decrypted_<filename>` inside `decrypted_files/`.
4. The server returns the list of decrypted file names/sizes as JSON.
5. The UI shows the completed decryption results.

### File Download

Decrypted (or encrypted) files can be fetched via the `/download/<path:filename>` endpoint, which streams the file as an attachment.

## Project Structure

```
File Encryption/
├── app.py               # Flask application — routes and crypto logic
├── templates/
│   └── index.html       # Single-page UI (encrypt & decrypt tabs)
├── static/
│   └── styles.css       # Stylesheet
├── uploads/             # Temporary storage for uploaded originals (auto-created)
├── encrypted_files/     # Output of encryption (auto-created)
└── decrypted_files/     # Output of decryption (auto-created)
```

## Setup & Running

### Prerequisites

- Python 3.8+
- pip

### Install Dependencies

```bash
pip install flask cryptography werkzeug
```

### Start the Server

```bash
python app.py
```

The app will start in debug mode at **http://127.0.0.1:5000**.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the main UI |
| `POST` | `/encrypt` | Encrypts uploaded files; returns key + file details |
| `POST` | `/decrypt` | Decrypts uploaded files using the provided key |
| `GET` | `/download/<path:filename>` | Downloads a processed file |

### `POST /encrypt`

**Request** — `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `files` | file(s) | One or more files to encrypt |

**Response** — JSON

```json
{
  "status": "success",
  "key": "<fernet-key-string>",
  "files": [
    { "name": "encrypted_example.txt", "size": "2.3 KB" }
  ]
}
```

### `POST /decrypt`

**Request** — `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | file(s) | One or more encrypted files |
| `key` | string | The Fernet key used during encryption |

**Response** — JSON

```json
{
  "status": "success",
  "files": [
    { "name": "decrypted_encrypted_example.txt", "size": "1.1 KB" }
  ]
}
```

## Security Notes

- The Fernet key is shown **once** after encryption — store it somewhere safe. Without the key, decryption is not possible.
- File names are sanitised with `werkzeug.utils.secure_filename` before being written to disk.
- Run behind a reverse proxy (e.g., Nginx) with HTTPS in production; do **not** use Flask's built-in debug server in a public environment.

## License

MIT