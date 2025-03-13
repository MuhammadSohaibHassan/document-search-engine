# Document Search Engine 🔍
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

A powerful document search application for uploading, managing, and searching text documents with advanced capabilities. Built for organizations and individuals needing efficient document management and full-text search.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Admin](#admin)
- [Security](#security)
- [Updates](#updates)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Capabilities
- **Document Management**: Upload, organize, preview, and download documents
- **Advanced Search**: Full-text search with configurable options (partial matching, case sensitivity, etc.)
- **User Interface**: Responsive design with search result highlighting and context
- **Pakistan Standard Time**: All timestamps displayed in PKT (UTC+5)
- **Accounts**: User registration, authentication, and personal document collections
- **Administration**: User and document management, system maintenance

### Supported File Types
- Text: `.txt`, `.csv`, `.md`, `.log`
- Code: `.py`, `.js`, `.java`, `.c`, `.cpp`, `.h`, `.cs`, `.php`, `.rb`, `.go`, `.rs`
- Configuration: `.json`, `.yaml`, `.yml`, `.ini`, `.cfg`, `.conf`, `.xml`, `.toml`
- Scripts: `.sql`, `.sh`, `.bat`, `.ps1`
- Other: `.tex`, `.bib`

## Installation

### Prerequisites
- Python 3.6+
- pip (Python package manager)

### Quick Setup
1. **Get the code**:
   ```bash
   git clone https://github.com/yourusername/document-search-engine.git
   cd document-search-engine
   ```

2. **Create virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**:
   ```bash
   python init_db.py
   ```
   Default admin: username `admin`, password `admin123` (change after login)

5. **Run application**:
   ```bash
   python run.py
   ```

6. **Access application**: http://127.0.0.1:5000

## Configuration

Key settings in `config.py`:

| Option | Description | Default |
|--------|-------------|---------|
| SECRET_KEY | Session security key | dev-secret-key-change-in-production |
| SQLALCHEMY_DATABASE_URI | Database connection | sqlite:///docs_search.db |
| UPLOAD_FOLDER | Document storage location | app/static/uploads |
| ALLOWED_EXTENSIONS | Permitted file types | Various text and code files |
| WHOOSH_INDEX_DIR | Search index location | whoosh_index |

## Usage

### Account Management
- **Register**: Navigate to `/register`
- **Login**: Navigate to `/login`

### Document Operations
- **Upload**: Click "Upload Documents" and select files
- **Manage**: View, preview, download, or delete via "My Documents"

### Search
- **Basic**: Enter keywords in search box and press Enter
- **Advanced Options**:
  - Partial Matches: Find words containing your terms
  - Case Sensitive: Match exact letter case
  - All Documents: Search global documents or only yours
- **Results**: View highlighted matches with navigation between occurrences

## Admin

Access via `/admin` with admin credentials.

### Capabilities
- **User Management**: View, add, edit, and delete users
- **Document Management**: Review and manage all system documents
- **Index Maintenance**: Rebuild search index when needed

## Security

- **Authentication**: Secure password hashing, brute force protection
- **Forms**: CSRF protection, input validation, XSS prevention
- **API**: CSRF tokens, rate limiting
- **Data**: Document access control, secure file handling

## Updates

### Recent Enhancements
- **Pakistan Time Integration** (Aug 2023): PKT timestamp display across application
- **Search Improvements** (Jul 2023): Advanced options, query enhancements, interface upgrades
- **Security Updates** (Jun 2023): CSRF protection, login attempt limiting
- **Bug Fixes** (Jun 2023): Upload handling, form validation, error messaging
- **Feature Additions** (May 2023): Spell checking, result highlighting, UI improvements

## Troubleshooting

### Common Issues
1. **Search problems**: Rebuild index, check document upload success, try different terms
2. **Dependency errors**: Verify virtual environment activation, reinstall requirements
3. **Upload failures**: Confirm supported file type, verify content is text-readable
4. **Database issues**: Run `init_db.py` to reset database
5. **Login problems**: Reset admin password, verify credentials format

## Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/your-feature`)
3. Make changes following PEP 8 guidelines
4. Test (`python -m unittest discover tests`)
5. Submit Pull Request with description

## License

[MIT License](LICENSE)

---

© 2023 Document Search Engine. All rights reserved.

### Technical Details

#### Project Structure
```
docs_search/
├── app/                     # Application package
│   ├── static/              # Assets (CSS, JS, uploads)
│   ├── templates/           # HTML templates
│   ├── admin/               # Admin module
│   ├── auth/                # Authentication module
│   ├── documents/           # Document handling
│   ├── main/                # Core functionality
│   ├── search.py            # Search implementation
│   ├── models.py            # Database models
│   └── spell_checker.py     # Spell checking
├── config.py                # Configuration
├── init_db.py               # Database setup
├── requirements.txt         # Dependencies
└── run.py                   # Entry point
```

#### Process Flow
1. **Document Upload**: UI validation → Server validation → Storage → Indexing
2. **Search**: Query parsing → Index lookup → Result ranking → Highlighting
3. **Time Handling**: Server-side PKT conversion + client-side formatting
