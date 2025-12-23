import $ from 'jquery';
import { initializeSelectizeSearch } from './selectize';

window.WIDGET_INIT_REGISTER = window.WIDGET_INIT_REGISTER || [];

export function manageFormsets() {
    $(function () {
        function reinit_widgets($formset_form) {
            $(window.WIDGET_INIT_REGISTER).each(function (index, func)
            {
                func($formset_form);
            });
        }

        function set_index_for_fields($formset_form, index) {
            $formset_form.find(':input').each(function () {
                var $field = $(this);
                if ($field.attr("id")) {
                    $field.attr(
                        "id",
                        $field.attr("id").replace(/-__prefix__-/,
                         "-" + index + "-")
                    );
                }
                if ($field.attr("name")) {
                    $field.attr(
                        "name",
                        $field.attr("name").replace(
                            /-__prefix__-/, "-" + index + "-"
                        )
                    );
                }
            });
            $formset_form.find('label').each(function () {
                var $field = $(this);
                if ($field.attr("for")) {
                    $field.attr(
                        "for",
                        $field.attr("for").replace(
                            /-__prefix__-/, "-" + index + "-"
                        )
                    );
                }
            });
            $formset_form.find('div').each(function () {
                var $field = $(this);
                if ($field.attr("id")) {
                    $field.attr(
                        "id",
                        $field.attr("id").replace(
                            /-__prefix__-/, "-" + index + "-"
                        )
                    );
                }
            });
        }

        function add_delete_button($formset_form) {
            $formset_form.find('input:checkbox[id$=DELETE]')
             .each(function () {
                var $checkbox = $(this);
                var $deleteLink = $(
                    '<button type="button" class="btn btn-sm btn-danger delete">-</button>'
                );
                $formset_form.find('.delete-content').append($deleteLink);
                $(this).hide()
            });

        }

        function addNewForm($formset, $total_forms) {
            var $new_form = $formset.find('.empty-form').clone(true).attr("id", null);
            $new_form.removeClass('empty-form d-none').addClass('formset-form');
            var index = parseInt($total_forms.val(), 10);
            set_index_for_fields($new_form, index);
            $formset.find('.formset-forms').append($new_form);
            add_delete_button($new_form);
            $total_forms.val(index + 1);
            return { $new_form, index }; // Возвращаем как объект с $new_form и index
        }

        $('.add-inline-form').click(function (e) {
            e.preventDefault();
            var $formset = $(this).closest('.formset');
            var $total_forms = $formset.find('[id$="TOTAL_FORMS"]');
            addNewForm($formset, $total_forms);
        });

        $('.add-inline-selectize-form').click(function (e) {
            e.preventDefault();
            var $formset = $(this).closest('.formset');
            var $total_forms = $formset.find('[id$="TOTAL_FORMS"]');
            var { $new_form, index } = addNewForm($formset, $total_forms); // Получаем $new_form и index из addNewForm

            var selectize_element = $new_form.find('.selectize-element');
            if (selectize_element.length > 0) {
                var element_id = 'id_' + index;
                selectize_element.attr('id', element_id);
                var element = $(`#${element_id}`);
                var url = element.data('url');
                var valueField = element.attr('data-value');
                var labelField = element.attr('data-label');
                var searchField = element.attr('data-search');
                var placeholder = element.attr('data-placeholder');

                const selectizeOptions = {
                    valueField: valueField,
                    labelField: labelField,
                    searchField: searchField,
                    placeholder: placeholder,
                };
                console.log(selectizeOptions)
                initializeSelectizeSearch(`#${element_id}`, url, selectizeOptions,
                    function onChangeCallback(value, selectizeInstance) {
                        const data_split = value.split("_");
                        const object_id = data_split[0];
                        const content_type = data_split[1];
                        var formsetForm = selectizeInstance.$input.closest('.formset-form');
                        formsetForm.find('.content_type').val(content_type);
                        formsetForm.find('.object_id').val(object_id);
                    }
                );
            }
        });

        $('.formset-form').each(function () {
            var $formset = $(this);
            add_delete_button($formset);
            reinit_widgets($formset);
        });

        $(document).on('click', '.delete', function (e) {
            e.preventDefault();
            var $formset = $(this).closest('.formset-form');
            var $checkbox = $formset.find('input:checkbox[id$=DELETE]')
            $formset.find('input:checkbox[id$=DELETE]');
            $checkbox.attr("checked", "checked");
            $formset.hide();
        });
    });
}