(function () {
    var cfg = document.currentScript.dataset;
    var PUNTO = 'position-absolute top-0 start-100 translate-middle p-1 bg-danger border border-light rounded-circle';
    var BADGE = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger';

    function enlace(url) { return document.querySelector('a[href="' + url + '"]'); }

    function pintarChat(n) {
        var a = enlace(cfg.chat);
        if (!a || location.pathname === cfg.chat) { return; }
        var b = a.querySelector('#punto-chat');
        if (n > 0) {
            if (!b) {
                b = document.createElement('span');
                b.id = 'punto-chat';
                b.className = BADGE;
                a.appendChild(b);
            }
            b.textContent = n;
        } else if (b) { b.remove(); }
    }

    function pintarPedidos(hay) {
        var a = enlace(cfg.pedidos);
        if (!a) { return; }
        var p = a.querySelector('.rounded-circle.bg-danger');
        if (hay && !p) {
            p = document.createElement('span');
            p.className = PUNTO;
            p.innerHTML = '<span class="visually-hidden">Novedades en tus pedidos</span>';
            a.appendChild(p);
        } else if (!hay && p) { p.remove(); }
    }

    function consultar() {
        if (document.hidden) { return; }
        fetch(cfg.url, { credentials: 'same-origin', headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (d) { if (d) { pintarChat(d.chat); pintarPedidos(d.pedidos); } })
            .catch(function () {});
    }
    setInterval(consultar, 20000);
    document.addEventListener('visibilitychange', consultar);
})();
