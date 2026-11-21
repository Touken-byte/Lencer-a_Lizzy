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

(function () {
    var CLAVE_SCROLL = 'jazzmin-sidebar-scroll';

    document.addEventListener('DOMContentLoaded', function () {
        var sidebar = document.querySelector('.sidebar-wrapper') || document.querySelector('#jazzy-sidebar');
        if (!sidebar) return;

        var guardado = sessionStorage.getItem(CLAVE_SCROLL);
        if (guardado !== null) {
            sidebar.scrollTop = parseInt(guardado, 10);
        }

        sidebar.addEventListener('scroll', function () {
            sessionStorage.setItem(CLAVE_SCROLL, sidebar.scrollTop);
        });

        sidebar.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                sessionStorage.setItem(CLAVE_SCROLL, sidebar.scrollTop);
            });
        });
    });
})();
;(function () {
    function poner(href, n) {
        var a = document.querySelector('.main-sidebar a.nav-link[href$="' + href + '"]');
        if (!a) { return; }
        var p = a.querySelector('p') || a;
        var b = a.querySelector('.aviso-menu');
        if (n > 0) {
            if (!b) {
                b = document.createElement('span');
                b.className = 'aviso-menu badge badge-danger ml-2';
                p.appendChild(b);
            }
            b.textContent = n;
        } else if (b) { b.remove(); }
    }
    function consultar() {
        if (document.hidden) { return; }
        fetch('/admin/avisos/', { credentials: 'same-origin' })
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (d) {
                if (!d) { return; }
                poner('/admin/chats/', d.chats);
                poner('/admin/pedidos/pedido/', d.pagos);
            })
            .catch(function () {});
    }
    document.addEventListener('DOMContentLoaded', consultar);
    setInterval(consultar, 30000);
})();
