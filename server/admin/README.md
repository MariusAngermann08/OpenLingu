# OpenLingu Admin Tools

This directory contains the administrative tools for managing the OpenLingu server. These tools are designed to be run directly on the server by administrators.

## Available Tools

### Contributor Management

- **Create new contributors**
- **List all contributors**
- **Delete contributors**

## How to Use

1. **Access the Admin Tools**
   ```bash
   # From the project root directory
   python -m server.admin.tools
   ```

2. **Follow the on-screen menu** to perform administrative tasks.

## Security Notes

- These tools should only be run by server administrators.
- The tools require direct server access to the database.
- Keep the admin tools secure and restrict access to authorized personnel.
- Always use strong, unique passwords for contributor accounts.

## Database Location

By default, the admin tools will use the database configured in your server settings:
- Users database: `server/db/users.db`
- Languages database: `server/db/languages.db`

## Troubleshooting

If you encounter any issues:
1. Verify database permissions
2. Check that the server is not running when making direct database changes
3. Ensure all dependencies are installed

## Dependencies

- Python 3.8+
- SQLAlchemy
- Passlib
- All other server dependencies
