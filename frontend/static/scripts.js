document.getElementById('logout-link').addEventListener('click', function (event) {
    event.preventDefault();
    fetch('/logout')
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                return response.json().then(data => console.error('Error:', data));
            }
        })
        .catch(error => console.error('Error al cerrar sesión:', error));
});

// document.getElementById('crearRecetalink').addEventListener("click", function (event) {
//     event.preventDefault();
//     fetch('/crearReceta')
//         .then(response => {
//             if (response.redirected) {
//                 window.location.href = response.url;
//             } else {
//                 return response.json().then(data => console.error("Error: " , data))
//             }
//         })
//         .catch(error => console.error('Error al dirigirse al html:', error));
// })