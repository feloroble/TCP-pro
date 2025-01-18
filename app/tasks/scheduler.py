
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, datetime
from app.models.user import User  # Asegúrate de importar correctamente el modelo

def update_expired_licenses():
    """Función que actualiza las licencias expiradas."""
    today = date.today()
    today_datetime = datetime.combine(today, datetime.min.time())
    expired_users = User.select().where(
        User.rol == "usuario TCP",
        User.license_expiry < today_datetime
    )
    for user in expired_users:
        user.rol = "usuario"
        user.license_duration = None
        user.license_expiry = None
        user.save()
    print(f"Actualización completada: {len(expired_users)} usuarios actualizados.")

def initialize_scheduler(app):
    """Inicializa y configura APScheduler."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_expired_licenses, trigger="interval", days=1)
    scheduler.start()

    # Manejo de cierre de la aplicación Flask
    @app.before_request
    def setup_scheduler():
        if not scheduler.running:
            scheduler.start()

    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        scheduler.shutdown()
