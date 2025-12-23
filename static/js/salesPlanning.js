import $ from 'jquery';
import { ajaxPost } from './ajax';


export function formSalesPlanning() {
    $('.sales-planning-form').on('blur', function() {
        let startDate = $('#id_start_date').val()
        let endDate = $('#id_end_date').val()
        let contentType = $(this).data('content_type')
        let objectId = $(this).data('object_id')
        let targetSales = $(this).val();


        const data = {
            start_date: startDate,
            end_date: endDate,
            target_sales: targetSales,
            content_type: contentType,
            object_id: objectId,
        };
        console.log(data)

        // Send the data via AJAX
        ajaxPost('/sales_planning/sales_plan/form/', data, (response) => {
            if (response.status === 'success') {

            } else {
                alert('test..... error')
                console.log(response.errors);
            }
        });
    });
}