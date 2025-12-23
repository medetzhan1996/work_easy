import $ from 'jquery';
import 'select2';

import { initializeSelectizeSearch, setSelectizeValue } from './selectize';
import { ajaxPost } from './ajax';

export function manageFormFields() {
    // Remove the commented code if not needed
    // $(".contenteditable-field.number").keypress(function(e) { /*...*/ });

    $('.select2').select2();




    $('.payment_method').on('change', function() {
        const selectedOption = $(this).find('option:selected')
        const commission = selectedOption.data('commission')

        const name = $(this).attr('name')
        const tr = $(this).closest('tr')
        const price_content = tr.find('input[data-associated="' + name + '"]')
        const price = parseFloat(price_content.val())
        const total = price - (price * commission / 100)
        const price_name = price_content.attr('name')

        const payment_after_commission = tr.find('span[data-associated="' + price_name + '"]').html(total)
    })

    // Note: Delete order handler moved to excel-table.js to avoid duplicate handlers

    $('.accepting_payment_by_commission').on('blur', function() {
        const tr = $(this).closest('tr')
        const associated_field_name = $(this).attr('data-associated')
        const price = parseFloat($(this).val())
        const price_name = $(this).attr('name')
        const associated_field = tr.find('select[name="' + associated_field_name + '"] option:selected')
        const commission = parseFloat(associated_field.data('commission'))
        const total = price - (price * commission / 100)
        const payment_after_commission = tr.find('span[data-associated="' + price_name + '"]').html(total)
    })

    function findNextLargerElementWithColor(currentElement) {
        let nextLargerElement = null;
        let resultElement = null;
        let largestLesserElement = null;
        let maxLesserValue = -Infinity;
        let currentIsMax = true;
        const currentSortingValue = Number($(currentElement).data('sorting'));
        const closestTr = $(currentElement).closest('tr');

        closestTr.find('.checkbox-field[data-sorting][data-color]:checked').each(function() {
            const sortingValue = Number($(this).data('sorting'));
            const color = $(this).attr('data-color');

            if (color.trim() !== '' && color.trim() !== 'None') {
                // Check if there is any element greater than current
                if (sortingValue > currentSortingValue) {
                    currentIsMax = false;
                    if (nextLargerElement === null || sortingValue < Number($(nextLargerElement).data('sorting'))) {
                        nextLargerElement = this;
                    }
                }

                // Finding the largest lesser element
                if (sortingValue < currentSortingValue && sortingValue > maxLesserValue) {
                    maxLesserValue = sortingValue;
                    largestLesserElement = this;
                }
            }
        });

        if (currentIsMax && $(currentElement).is(':checked')) {
            resultElement = currentElement;
        } else {
            if (nextLargerElement) {
                resultElement = nextLargerElement;
            } else {
                resultElement = largestLesserElement;
            }
        }

        return resultElement;
    }




    $('.checkbox-field').on('change', function() {
        const tr = $(this).closest('tr')
        const sorting = $(this).attr('data-sorting');
        const id = tr.data('id');
        const color = $(this).attr('data-color');

        let field_name = $(this).attr('name');
        let new_value = $(this).prop('checked');
        const url = `/orders/order/${id}/update/`;
        const formData = {
            field_name: field_name,
            new_value: new_value
        }
        ajaxUpdate(url, formData);
        const next_element = findNextLargerElementWithColor($(this))
        console.log('test....')
        console.log(next_element)
        const next_element_color = $(next_element).attr('data-color')
        console.log(next_element_color)
        console.log('test....')
        if(next_element_color){
            tr.css("background-color", next_element_color);
        }
        else{
            tr.css("background-color", "inherit");
        }
    });




    $('.select-bank').on('change', function() {
        var currentElement = $(this);
        var selectedBank = JSON.parse(currentElement.val())
        var selectedBankName = currentElement.attr('name');
        var closestRow = currentElement.closest('tr');
        const element =  closestRow.find('select[data-bank="' + selectedBankName + '"]')

        // скрыть все варианты оплаты
        closestRow.find('select[data-bank="' + selectedBankName + '"] option').addClass('d-none');

        // отобразить только варианты оплаты, связанные с выбранным банком
        closestRow.find('select[data-bank="' + selectedBankName + '"] option[data-bank="' + selectedBank.id + '"]').removeClass('d-none');

        // сделать связанный select пустым (для .select-bank)
        if (currentElement.hasClass('select-bank')) {
            closestRow.find('select[data-bank="' + selectedBankName + '"]').val('');
        }
    });

    $('.selected-bank').on('change', function() {
        var currentElement = $(this);
        var selectedBank = JSON.parse(currentElement.val())
        var selectedBankName = currentElement.attr('name');
        var closestRow = currentElement.closest('tr');
        const element =  closestRow.find('select[data-bank="' + selectedBankName + '"]')
        element.closest('td').find('.span-select-id-field').addClass('d-none')
        element.closest('td').find('div').removeClass('d-none')
        const element_id = element.data('id')
        var options = $(element_id).html();
        element.html(options).find('option[data-bank="' + selectedBank.id + '"]').removeClass('d-none')
    });

    function calculateTotalSum() {
        var surchargeTotalSum = 0;
        var discountTotalSum = 0;
        var acceptingTotalSum = 0;
        var productPriceTotalSum = 0;

        $(this).closest('tr').find('.discount, .surcharge, .accepting_payment, .product_price').each(function() {
            var value = parseFloat($(this).val());
            if (!isNaN(value)) {
                if ($(this).hasClass('surcharge')) {
                    surchargeTotalSum += value;
                }
                else if ($(this).hasClass('product_price')) {
                    productPriceTotalSum += value;
                }
                else if ($(this).hasClass('accepting_payment')) {
                    acceptingTotalSum += value;
                }
                else if ($(this).hasClass('discount')) {
                    var discountAmount = value * productPriceTotalSum / 100;
                    discountTotalSum += discountAmount;
                }
            }
        });

        // Calculate the final price
        var totalPrice = productPriceTotalSum + surchargeTotalSum - discountTotalSum;
        var discountPrice = productPriceTotalSum - discountTotalSum
        var remainder = totalPrice - acceptingTotalSum

        $(this).closest('tr').find('.remainder-content').html(remainder)
        $(this).closest('tr').find('.total_payment-content').html(totalPrice)
        $(this).closest('tr').find('.discounted_amount-content').html(discountPrice)
    }

    $('.discount, .surcharge, .accepting_payment, .product_price').on('blur', calculateTotalSum);

     $('.select-related').each(function() {
        var currentElement = $(this);
        var relatedElement = currentElement.data('bank');
        var relatedElementVal = currentElement.closest('tr').find('[name="' + relatedElement + '"]').val();
        currentElement.find('option').addClass('d-none');
        currentElement.find('option[data-bank="' + relatedElementVal + '"]').removeClass('d-none');
    });

    $('.select-field').on('change', function() {
        const id = $(this).closest('tr').data('id');
        let field_name = $(this).attr('name');
        let new_value = $(this).val();
        const url = `/orders/order/${id}/update/`;
        const formData = {
            field_name: field_name,
            new_value: new_value
        }
        ajaxUpdate(url, formData);
    })

    $('.date-field').on('blur', function() {
        const id = $(this).closest('tr').data('id');
        let field_name = $(this).attr('name');
        const new_value = $(this).val();
        const url = `/orders/order/${id}/update/`;
        const formData = {
            field_name: field_name,
            new_value: new_value
        }
        const format_value = formatDate(new_value)
        ajaxUpdate(url, formData, ()=>{
            $(this).addClass('d-none').closest('td').find('.span-field').text(format_value).removeClass('d-none');
        });
    });

    $('.input-field').on('blur', function() {
        const id = $(this).closest('tr').data('id');
        let field_name = $(this).attr('name');
        let new_value = $(this).val();
        const url = `/orders/order/${id}/update/`;
        const formData = {
            field_name: field_name,
            new_value: new_value
        }
        ajaxUpdate(url, formData, ()=>{
            if(!new_value){
                new_value = '.........'
            }
            $(this).addClass('d-none').closest('td').find('.span-field').text(new_value).removeClass('d-none');
        });
    });

//
//     $('.contenteditable-field').on('blur', function() {
//         const id = $(this).closest('tr').data('id');
//         let field_name = $(this).data('name');
//         let new_value = $(this).text();
//         const url = `/orders/order/${id}/update`;
//         const formData = {
//             field_name: field_name,
//             new_value: new_value
//         }
//         ajaxUpdate(url, formData);
//     });

    $('.span-field').on('click', function() {
        $(this).addClass('d-none')
        const Input = $(this).closest('td').find('input');
        Input.removeClass('d-none');
        Input.focus()
        var val = Input.val();
        Input.val('');
        Input.val(val);
    });

    $('.span-select-field').on('click', function() {
        const id = $(this).attr('data-id')
        const val = $(this).attr('data-val')
        const td = $(this).closest('td')
        const select = td.find('select')
        var options = $(id).html();
        $(this).addClass('d-none')
        select.html(options).val(val).trigger('change')
        select.closest('div').removeClass('d-none')
        td.addClass('opened-select')
    })


     $(document).click(function(event) {
        var $target = $(event.target);
        const $openedSelect = $('.opened-select');
        if (!$target.closest('.opened-select').length && $openedSelect.length > 0) {
            $('.opened-select').each(function() {
                var $this = $(this);
                var selectedElement = $this.find('select option:selected');
                var selectedText = selectedElement.text();
                if($this.find('.span-select-field').length){
                    var selectedVal = selectedElement.val();
                    $this.find('.span-select-field').attr("data-val", selectedVal).html(selectedText).removeClass('d-none');

                }
                else if($this.find('.span-select-id-field').length){
                    var selectedVal = selectedElement.attr('data-id')
                    $this.find('.span-select-id-field').attr("data-val", selectedVal).html(selectedText).removeClass('d-none');
                }
                $this.find('div').addClass('d-none');
                $this.removeClass('opened-select')

            });
        }
    });

    $('.span-select-id-field').on('click', function() {
        const id = $(this).attr('data-id')
        const val = $(this).attr('data-val')
        const associated = $(this).data('associated')
        var options = $(id).html();
        const select = $(this).closest('td').find('select')
        $(this).addClass('d-none')
        select.html(options).find('option[data-id="' + val + '"]').prop('selected', true)
        select.find('option[data-bank="' + associated + '"]').removeClass('d-none')
        select.closest('div').removeClass('d-none')
        $(this).closest('td').addClass('opened-select')
    })

}

function formatDate(dateString) {
    const date = new Date(dateString);
    const day = ('0' + date.getDate()).slice(-2);
    const month = ('0' + (date.getMonth() + 1)).slice(-2);
    const year = date.getFullYear();

    return `${day}.${month}.${year}`;
}

function ajaxUpdate(url, formData, callback = () => {}) {
    ajaxPost(url, formData,
        (data) => {
            callback()
        },
        (xhr, status, error) => {
            const response = JSON.parse(xhr.responseText);
            if (response.error) {
                for (const key in response.error) {
                    if (response.error.hasOwnProperty(key)) {
                        const errorMessages = response.error[key];
                        errorMessages.forEach((errorMessage) => {
                            // Instead of alerting the error message, you could change this to display the error in a more user-friendly manner
                            console.error(errorMessage);
                        });
                    }
                }
            }
        }
    );
}

$('tr').each(function() {
    const tr = $(this)
    // Get all checked checkboxes with a data-sorting attribute and a valid data-color
    let checkboxes = $(this).find('.checkbox-field:checked[data-sorting]').filter(function() {
        let color = $(this).data('color');
        return color && color !== 'None';
    });

    // Determine the checkbox with the largest data-sorting value
    let maxSortingCheckbox = checkboxes.sort(function(a, b) {
        return $(b).data('sorting') - $(a).data('sorting');
    }).first();
    // If such a checkbox is found, use its color to set the row's background
    if(maxSortingCheckbox.length) {
        tr.find('td').each(function() {
          $(this).css('background-color', '')
        });
        tr.css("background-color", maxSortingCheckbox.data('color'));
    }
});

$('.fixed-column').each(function(index, elem) {
    var leftPosition = $(elem).position().left;
    $(elem).css('left', leftPosition + 'px');
});
