from app import app

from freelance.app.admin import admin_bp
app.register_blueprint(admin_bp)


if __name__ == '__main__':
  app.run(debug=True)