"""
Script to create initial database migration
"""
import subprocess
import sys

def create_migration():
    """Create initial migration"""
    try:
        # Create migration
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "Initial migration"],
            check=True,
            capture_output=True,
            text=True
        )
        print("Migration created successfully!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating migration: {e.stderr}")
        return False

if __name__ == "__main__":
    success = create_migration()
    sys.exit(0 if success else 1)

