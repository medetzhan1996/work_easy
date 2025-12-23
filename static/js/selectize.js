import $ from 'jquery';
import 'selectize';

import { ajaxGet, ajaxPost } from './ajax';


function initializeSelectizeSearch(selector, searchUrl, options, onChangeCallback) {
    $(selector).selectize({
        ...options,
        load: function (query, callback) {
            if (query && query.length >= 2) {
                ajaxGet(searchUrl, {'q': query}, function(data){
                    if (data.length === 0) {
                        callback([{value: 'not_found', full_name: 'Данные не найдены!'}]);
                    } else {
                        callback(data);
                    }
                })
            } else {
                callback();
            }
        },
		onChange: function (value) {
		    onChangeCallback(value, this)
		}
    });
}

const initializeSelectizeSearchCrud = (selectizeId, searchUrl, selectizeOption, formClass,
    deleteClass, idForm, onChange, onDelete, onSubmit) => {
    initializeSelectizeSearch(selectizeId, searchUrl, selectizeOption, onChange);

    $(document).on("click", formClass, function() {
        const url = $(this).data('url')
        ajaxGet(url, {}, onSubmit, (error) => {
            console.error('Error in formClass click:', error);
        })
    })

    $(document).on("click", deleteClass, onDelete)

    $(document).on("submit", idForm, (event) => {
        event.preventDefault();
        const url = $(event.currentTarget).attr('action')
        const formData = $(event.currentTarget).serialize()
        ajaxPost(url, formData, (data) => {
            try {
                if (data.success) {
                    onSubmit(data);
                }
            } catch (error) {
                console.error('Error in onSubmitForm:', error);
            }
        }, (error) => {
            console.error('Error in idForm submit:', error);
        })
    })
}

function setSelectizeValue(selector, values){
    var $select = $(selector).selectize()
    var selectize = $select[0].selectize
    selectize.addOption(values)
    selectize.setValue(values.id)
}

function loadDetail(itemId, detailContentId, loadUrl) {
    const url = `${loadUrl}/${itemId}/detail`;
    ajaxGet(url, {}, (data) => {
        $(`#${detailContentId}-search-content`).addClass('d-none');
        $(`#${detailContentId}-detail-content`).removeClass('d-none').html(data);
        $(`#${detailContentId}-form-content`).addClass('d-none');
    }, (error) => {
        console.error('Error in loadDetail:', error);
    });
}

function onDeleteForm(selectizeId) {
    $(`${selectizeId}`)[0].selectize.clear()
    $(`${selectizeId}-search-content`).removeClass('d-none')
    $(`${selectizeId}-detail-content`).html('').addClass('d-none')
}

export {
  initializeSelectizeSearch,
  initializeSelectizeSearchCrud,
  setSelectizeValue,
  loadDetail,
  onDeleteForm
};