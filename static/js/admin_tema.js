(function () {
    function aplicarTema(tema) {
        document.documentElement.setAttribute('data-bs-theme', tema);
        localStorage.setItem('jazzmin-theme-mode', tema);
    }

    document.addEventListener('DOMContentLoaded', function () {
        var contenedor = document.querySelector('#jazzy-navbar .navbar-nav.ms-auto');
        if (!contenedor) return;

        var li = document.createElement('li');
        li.className = 'nav-item';
        li.innerHTML = '<a class="nav-link btn" href="#" id="botonTemaAdmin" title="Cambiar tema"><i class="fas fa-moon" id="iconoTemaAdmin"></i></a>';
        contenedor.insertBefore(li, contenedor.firstChild);

        var boton = document.getElementById('botonTemaAdmin');
        var icono = document.getElementById('iconoTemaAdmin');

        function actualizarIcono() {
            var actual = document.documentElement.getAttribute('data-bs-theme') || 'light';
            icono.className = actual === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
        actualizarIcono();

        boton.addEventListener('click', function (e) {
            e.preventDefault();
            var actual = document.documentElement.getAttribute('data-bs-theme') || 'light';
            aplicarTema(actual === 'dark' ? 'light' : 'dark');
            actualizarIcono();
        });
    });
})();