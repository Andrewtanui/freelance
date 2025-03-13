from app import app
from app.models import Project

with app.app_context():
    projects = Project.query.filter_by(status='open').all()
    print(f'Found {len(projects)} open projects:')
    for project in projects:
        print(f'- {project.title} (ID: {project.id})')
