(function () {
    var EXT = /\.(png|jpe?g|gif|webp)(\?.*)?$/i;
    var fondo = null;

    function cerrar() {
        if (fondo) { fondo.remove(); fondo = null; }
    }

    function abrir(src) {
        cerrar();
        fondo = document.createElement('div');
        fondo.setAttribute('style',
            'position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:99999;' +
            'display:flex;align-items:center;justify-content:center;padding:24px;');
        var img = document.createElement('img');
        img.src = src;
        img.setAttribute('style',
            'max-width:92vw;max-height:88vh;border-radius:8px;background:#fff;');
        var x = document.createElement('button');
        x.type = 'button';
        x.textContent = '\u2715';
        x.setAttribute('aria-label', 'Cerrar');
        x.setAttribute('style',
            'position:absolute;top:14px;right:18px;font-size:26px;line-height:1;' +
            'width:42px;height:42px;border:0;border-radius:50%;cursor:pointer;' +
            'background:#fff;color:#000;');
        x.addEventListener('click', cerrar);
        fondo.addEventListener('click', function (e) {
            if (e.target === fondo) { cerrar(); }
        });
        fondo.appendChild(img);
        fondo.appendChild(x);
        document.body.appendChild(fondo);
    }

    document.addEventListener('click', function (e) {
        var a = e.target.closest ? e.target.closest('a[href]') : null;
        if (!a || !EXT.test(a.getAttribute('href') || '')) { return; }
        e.preventDefault();
        abrir(a.getAttribute('href'));
    });
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { cerrar(); }
    });
})();
