import $ from 'jquery';

export function globalEvent() {
    $('.change-submitted').on('change', function() {
        $(this).closest('form').submit()
    })

     $(".change-clearable-submitted").change(function() {
        // Очищаем все остальные поля формы
        $(".clearable").removeAttr("name");
         $(this).closest('form').submit();
     });



}