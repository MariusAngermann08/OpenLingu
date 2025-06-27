# OpenLingu CLI Tool

A command-line interface for managing OpenLingu content, including languages and lections, with contributor authentication.

## Features

- **User Authentication**
  - Register new contributors
  - Login with existing credentials
  - Secure token-based authentication

- **Language Management**
  - List all available languages
  - Add new languages
  - Delete existing languages

- **Lection Management**
  - List all lections for a language
  - Add new lections
  - Edit existing lections
  - Delete lections
  - View lection content

## Prerequisites

- Python 3.7 or higher
- `requests` library
- Access to OpenLingu server (default: http://localhost:8000)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd OpenLingu/dev
   ```

2. Install required dependencies:
   ```bash
   pip install requests
   ```

## Usage

### Running the CLI

```bash
python openlingu_cli.py
```

### Authentication

1. Register a new contributor account:
   ```
   Main Menu > 3. Register
   ```

2. Login with your credentials:
   ```
   Main Menu > 4. Login
   ```

### Managing Languages

- **List all languages**: `Main Menu > 1. Language Management > 1. List Languages`
- **Add a language**: `Main Menu > 1. Language Management > 2. Add Language`
- **Delete a language**: `Main Menu > 1. Language Management > 3. Delete Language`

### Managing Lections

- **List lections**: `Main Menu > 2. Lection Management > 1. List Lections`
- **Add a lection**: `Main Menu > 2. Lection Management > 2. Add Lection`
- **Edit a lection**: `Main Menu > 2. Lection Management > 3. Edit Lection`
- **Delete a lection**: `Main Menu > 2. Lection Management > 4. Delete Lection`
- **View lection**: `Main Menu > 2. Lection Management > 5. View Lection`

## Configuration

By default, the CLI connects to `http://localhost:8000`. To change this, modify the `BASE_URL` constant in `openlingu_cli.py`.

## Error Handling

The CLI provides detailed error messages for common issues:
- Authentication failures
- Invalid input
- Server connection issues
- Permission errors

## Security

- Passwords are never displayed when typed
- Authentication tokens are stored in memory only
- All API calls use HTTPS when available

## Troubleshooting

- Ensure the OpenLingu server is running and accessible
- Verify your internet connection if using a remote server
- Check that your authentication token is valid (will expire after some time)
- For detailed debug information, enable debug mode by setting environment variable `DEBUG=1`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

