django.jQuery(function($) {
    var $categoria = $('#id_categoria');
    var $subcategoria = $('#id_subcategoria');

    var TALLAS_LETRA = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'UNICA'];
    var TALLAS_BRASSIERE = ['70A','70B','70C','75A','75B','75C','80A','80B','80C','85A','85B','85C'];

            function filtrarTallasVariantes(tipoTalla) {
        var permitidas = (tipoTalla === 'brassiere') ? TALLAS_BRASSIERE.concat(['UNICA'])
                        : (tipoTalla === 'sin_talla') ? ['UNICA']
                        : TALLAS_LETRA;

        $('select[id^="id_variantes-"][id$="-talla"]').each(function() {
            var $select = $(this);

            if (tipoTalla === 'sin_talla') {
                $select.val('UNICA');
                $select.closest('td').hide();
                return;
            }
            $select.closest('td').show();

            var valorActual = $select.val();
            $select.find('option').each(function() {
                var val = $(this).val();
                if (val === '') return;
                $(this).toggle(permitidas.indexOf(val) !== -1);
            });
            if (permitidas.indexOf(valorActual) === -1) {
                $select.val('');
            }
        });
    }

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
                $subcategoria.append(
                    '<option value="' + sub.id + '" data-tipo-talla="' + sub.tipo_talla + '" ' + selected + '>' + sub.nombre + '</option>'
                );
            });
            $subcategoria.trigger('change');
        });
    }

    $subcategoria.on('change', function() {
        var tipoTalla = $(this).find('option:selected').data('tipo-talla');
        filtrarTallasVariantes(tipoTalla);
    });

    $categoria.on('change', actualizarSubcategorias);

    // Al cargar la página, si ya hay subcategoría seleccionada, filtra de una vez
    $subcategoria.trigger('change');
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