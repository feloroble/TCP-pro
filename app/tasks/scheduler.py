
from datetime import date, datetime, timedelta
from app.email_service import send_email
from app.models.user import User  # Asegúrate de importar correctamente el modelo



def update_expired_licenses():
    """Función que actualiza las licencias expiradas  y envía notificaciones de expiración cercana."""
    today = date.today()
    today_datetime = datetime.combine(today, datetime.min.time())  # Convierte a datetime
    warning_date = today + timedelta(days=7)  # Fecha de advertencia a 7 días
    
    expired_users = User.select().where(
        User.rol == "usuario TCP",
        User.license_expiry.is_null(False),  # Evita usuarios sin fecha de expiración
        User.license_expiry < today_datetime  # Filtra las licencias expiradas
    )

    for user in expired_users:
        user.rol = "usuario"  # Cambiar rol a usuario regular
        user.license_duration = None  # Eliminar duración de licencia
        user.license_expiry = None  # Eliminar fecha de expiración
        user.save()

    expiring_soon_users = User.select().where(
        User.rol == "usuario TCP",
        User.license_expiry.is_null(False),
        User.license_expiry.between(today_datetime, warning_date)
    )

    for user in expiring_soon_users:
        email = user.email
        print(email)
        renewal_link = f"https://wa.link/elzjtb"    
        send_email(
                 subject="Notificacion de Licencia",
                 recipients=[email],
                 template="email/license_warning.html",
                 title="Urgente, tienes que renovar tu licencia en la plataforma",
                 user=user,
                 renewal_link=renewal_link
            )

    print(f"Actualización completada: {len(expired_users)} usuarios actualizados.")
    
from apscheduler.schedulers.background import BackgroundScheduler

def initialize_scheduler(app):
    """Inicializa y configura APScheduler."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_expired_licenses, trigger="interval", days=1)
    scheduler.start()

    # Vincula el Scheduler a la configuración de Flask para evitar duplicados
    app.config['scheduler'] = scheduler

    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        """Apaga el Scheduler cuando la aplicación Flask se apaga."""
        if scheduler.state == 1:  # Estado 1 indica que está corriendo
            scheduler.shutdown(wait=False)  # Esperar o no las tareas en ejecución