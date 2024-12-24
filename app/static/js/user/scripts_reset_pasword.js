document.getElementById('resetPasswordForm').addEventListener('submit', function (e) {
    e.preventDefault();

    let valid = true;
    const email = document.getElementById('email');
    const generalError = document.getElementById('generalError');

    // Reset alerts
    document.querySelectorAll('.form-alert').forEach(alert => alert.style.display = 'none');
    generalError.style.display = 'none';

    // Validar Correo Electrónico
    if (!email.value.trim() || !/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(email.value)) {
        email.nextElementSibling.style.display = 'block';
        valid = false;
    }

    // Mostrar error general si no es válido
    if (!valid) {
        generalError.style.display = 'block';
    } else {
        alert('Se han enviado las instrucciones para restablecer la contraseña');
        // Aquí puedes implementar la lógica para enviar los datos al servidor
    }
});
