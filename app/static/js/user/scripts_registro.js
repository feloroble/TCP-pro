document.getElementById('registerForm').addEventListener('submit', function (e) {
    e.preventDefault();

    let valid = true;
    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const email = document.getElementById('email').value.trim();
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    const confirmPassword = document.getElementById('confirmPassword').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const generalError = document.getElementById('generalError');

    // Validaciones simplificadas aquí
    if (!firstName || !lastName || !email || !username || !password || !phone || password !== confirmPassword) {
        generalError.style.display = 'block';
        return;
    }

    // Ocultar errores generales
    generalError.style.display = 'none';

    // Crear el objeto con los datos
    const formData = {
        first_name: firstName,
        last_name: lastName,
        email: email,
        username: username,
        password: password,
        phone: phone
    };
    console.log(jsonData);  
    // Enviar la solicitud al backend
    fetch('/user/registro', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Registro exitoso');
            window.location.href = '/login';
        } else {
            generalError.textContent = data.message || 'Ocurrió un error';
            generalError.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error al enviar los datos:', error);
        generalError.textContent = 'Error al comunicarse con el servidor';
        generalError.style.display = 'block';
    });
});
