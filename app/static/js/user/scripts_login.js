document.getElementById('loginForm').addEventListener('submit', function (e) {
    e.preventDefault();

    let valid = true;
    const userOrEmail = document.getElementById('userOrEmail');
    const password = document.getElementById('password');
    const generalError = document.getElementById('generalError');

    // Reset alerts
    document.querySelectorAll('.form-alert').forEach(alert => alert.style.display = 'none');
    generalError.style.display = 'none';

    // Validar Usuario o Correo
    if (!userOrEmail.value.trim() || (!userOrEmail.value.includes('@') && userOrEmail.value.length < 3)) {
        userOrEmail.nextElementSibling.style.display = 'block';
        valid = false;
    }

    // Validar Contraseña
    if (!password.value.trim()) {
        password.nextElementSibling.style.display = 'block';
        valid = false;
    }

    // Mostrar error general si no es válido
    if (!valid) {
        generalError.style.display = 'block';
    } else {
        alert('Inicio de sesión exitoso');
        // Aquí puedes implementar la lógica para enviar los datos al servidor
    }
});
