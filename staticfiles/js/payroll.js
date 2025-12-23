import $ from 'jquery';
import { ajaxPost } from './ajax';


export function updatePayrollFields() {
    $('.sales-update-field').on('blur', function() {
        const inputField = $(this);
        const salaryId = inputField.closest('tr').data('id');
        const fieldName = inputField.attr('name');
        const fieldValue = inputField.val();

        const data = {
            user_id: salaryId,
            name: fieldName,
            value: fieldValue
        };

        // Send the data via AJAX
        ajaxPost('/payroll/update_salary/', data, (response) => {
            if (response.status === 'success') {

            } else {
                console.log(response)
            }
        });
    });
}