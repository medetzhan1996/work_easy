// Import necessary modules and functions
import $ from 'jquery';
import bootstrap from 'bootstrap'
import Popover from 'bootstrap/js/dist/popover';
import AutoScroller from 'dom-autoscroller';
import { formSalesFunnel } from './salesFunnel';
import { manageFormFields  } from './manageFormFields';
import { globalEvent  } from './globalEvent';
import { manageFormsets  } from './formset';

import { initializeDragula } from './dragula';
import { ajaxPost } from './ajax';
import { initializeSelectizeSearch, initializeSelectizeSearchCrud,
        loadDetail, onDeleteForm, setSelectizeValue } from './selectize';

import { updatePayrollFields } from './payroll';
import { initializeAttendanceStatusPopover } from './attendanceStatusPopover';
import { initializeWeekWorkTimeStatusPopover } from './weekWorkTimeStatusPopover';

import { formSalesPlanning } from './salesPlanning';


const customerSelectizeOption = {
    valueField: 'id',
    labelField: 'full_name',
    searchField: 'full_name',
    placeholder: 'Поиск клиента...',
};


// Initialize the Dragula module for dragging elements with the .kanban-items class
initializeDragula('.kanban-items', function (drake) {
        drake.on('drop', function handleDropCallback(el, target, source, sibling){
            const itemID = el.getAttribute('data-id');
            const parentBoardId = target.getAttribute('id');
            const url = `/sales_funnel/card-ajax/${itemID}/update`;
            const data = { 'funnel': parentBoardId };
            try {
                ajaxPost(url, data);
            }
            catch (error) {
                console.error('Error updating card:', error);
            }
        })
        // Initialize the AutoScroller module for automatic page scrolling when dragging elements
        const kanbanContainer = document.getElementById('kanban-container')
        if(kanbanContainer){
            const autoScroller = new AutoScroller(kanbanContainer, {
                margin: 20,
                maxSpeed: 5,
                scrollWhenOutside: true,
                autoScroll: function () {
                    return this.down && drake.dragging;
                },
            });
        }
    }
);

initializeDragula('.kanban-funnel', function (drake) {
    drake.on('dragend', function (el) {
        const url = "/sales_funnel/sort_funnel/update"
        const container = document.getElementById('kanban-container');
        const cardMains = container.getElementsByClassName('card-main');
        const funnelIds = Array.from(cardMains).map(cardMain => cardMain.getAttribute('data-funnel-id'));
        const data = { 'sorted_funnels': JSON.stringify(funnelIds) };
        ajaxPost(url, data);
    });
})

initializeDragula('.kanban-form_field', function (drake) {
    const container = document.getElementById('kanban-container');
    drake.on('dragend', function (el) {
        const url = "/dynamic_forms/sort_form_field/update"
        const cardMains = container.getElementsByClassName('card-main');
        const formFieldIds = Array.from(cardMains).map(cardMain => cardMain.getAttribute('data-form_field-id'));
        const data = { 'sorted_form_fields': JSON.stringify(formFieldIds) };
        ajaxPost(url, data);
        // Initialize the AutoScroller module for automatic page scrolling when dragging elements

    });
    if(container){
        const autoScroller = new AutoScroller(container, {
            margin: 20,
            maxSpeed: 7,
            scrollWhenOutside: true,
            autoScroll: function () {
                return this.down && drake.dragging;
            },
        });
    }
})



const productSelectizeOption = {
    valueField: 'id',
    labelField: 'title',
    searchField: 'title',
    placeholder: 'Поиск товара...',
};

// Initialize Selectize.js for the element with the #id_customer identifier on the page
// initializeSelectizeSearch('#id_product', "/products/search/", productSelectizeOption, function onChangeCallback(value){
//     if(value){
//     }
// });

initializeSelectizeSearch('.product-selectize', '/products/products_materials/search/', productSelectizeOption,
    function onChangeCallback(data, selectizeInstance){
        const data_split = data.split("_")
        const object_id = data_split[0]
        const content_type = data_split[1]
        var formsetForm = selectizeInstance.$input.closest('.formset-form');
        formsetForm.find('.content_type').val(content_type); // Replace 'new_value' with the desired value
        formsetForm.find('.object_id').val(object_id);
    }
)

initializeSelectizeSearchCrud(
    '#id-customer',
    "/customers/search/",
    customerSelectizeOption,
    '.customer-form',
    '.customer-delete',
    '#id-customer-form',
    (value) => {
        if (value) {
            loadDetail(value, 'id-customer', '/customers/customer')
        }
    },
    () => {
        onDeleteForm('#id-customer')
    },
    (data) => {
        if(data.id){
            setSelectizeValue('#id-customer', {id: data.id, full_name: data.full_name});
            $('#id-form-content').removeClass('d-none')
            $('#id-customer-form-content').addClass('d-none').html('')
        }
        else{
            $('#id-form-content').addClass('d-none')
            $('#id-customer-form-content').removeClass('d-none').html(data)
        }

    }
);

updatePayrollFields()
initializeAttendanceStatusPopover()
initializeWeekWorkTimeStatusPopover()
globalEvent()
manageFormFields()
manageFormsets()
formSalesPlanning()
formSalesFunnel()