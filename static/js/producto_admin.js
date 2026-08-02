django.jQuery(function($) {
    var $categoria = $('#id_categoria');
    var $subcategoria = $('#id_subcategoria');

    function actualizarSubcategorias() {
        var categoriaId = $categoria.val();
        var actual = $subcategoria.val();
        if (!categoriaId) {
            $subcategoria.html('<option value="">---------</option>');
            return;
        }
        $.get('/api/catalogo/subcategorias/' + categoriaId + '/', function(data) {
            $subcategoria.html('<option value="">---------</option>');
            data.forEach(function(sub) {
                var selected = (String(sub.id) === String(actual)) ? 'selected' : '';
                $subcategoria.append('<option value="' + sub.id + '" ' + selected + '>' + sub.nombre + '</option>');
            });
        });
    }

    $categoria.on('change', actualizarSubcategorias);
});

django.jQuery(function($) {
    var $enOferta = $('#id_en_oferta');
    var $descuento = $('#id_porcentaje_descuento');

    $enOferta.on('change', function() {
        if ($(this).is(':checked')) {
            $descuento.focus();
        } else {
            $descuento.val(0);
        }
    });
});