import $ from 'jquery';
import Modal from 'bootstrap/js/dist/modal';
import { ajaxPost, ajaxGet } from './ajax';

export function formSalesFunnel() {
    function handleCardModalClick() {
        const url = $(this).data('url');
        const card_order_url = $(this).data('card_order_url');
        const funnel = $(this).data('funnel');

        ajaxGet(url, { 'funnel': funnel },
            (data) => {
                $('#id-form-content').html(data);
                showCardModal(card_order_url);
            },
            (error) => {
                console.error('An error occurred during the AJAX request:', error);
            }
        );
    }

    // Функция для отображения модального окна
    function showCardModal(card_order_url) {
        let modal = new Modal('#universalModal');
        modal.show();

        if (card_order_url) {
            ajaxGet(card_order_url, {},
                (data) => {
                    $('#order-list-content').html(data);
                },
                (error) => {
                    console.error('An error occurred during the AJAX request:', error);
                }
            );
        }
    }

    function handleCardFormSubmit(form, successCallback) {
        const url = form.attr('action');
        const formData = form.serialize();
        ajaxPost(url, formData, (data) => {
            successCallback(data)

        });
    }

    // Регистрация обработчика события клика на элементе с классом '.open-card-modal'
    $(document).on("click", '.open-card-modal', handleCardModalClick);

    $(document).on("submit", '#id-card-form', (event) => {
        event.preventDefault();
        const form = $(event.currentTarget);
        const submittedButtonAddOrder = form.find('input[name="submit_button"]:focus').data('add-order')
        handleCardFormSubmit(form, function(data) {
            console.log(data)
            if (data.success) {
                if(submittedButtonAddOrder){
                    const url = `/orders/order/card/${data.card_id}/form`
                    ajaxGet(url, {},
                        (data) => {
                            $('#id-form-content').addClass('d-none')
                            $('#id-order-form-content').removeClass('d-none').html(data)

                        },
                        (error) => {
                            console.error('An error occurred during the AJAX request:', error);
                        }
                    );
                }
                else{
                    location.reload()
                }

            }
        });
    });

      $(document).on("click", '#id-add-order', function() {
          var url = $(this).attr('data-url');

      });

      $(document).on("click", '#id-back-funnel', function() {
        $('#id-form-content').removeClass('d-none')
        $('#id-order-form-content').addClass('d-none')
      })

      $(document).on("submit", '#id-order-form', (event) => {
        event.preventDefault();
        const url = $(event.currentTarget).attr('action')
        const card_order_url = $(event.currentTarget).data('card_order_url');
        const formData = $(event.currentTarget).serialize()
        ajaxPost(url, formData, (data) => {
            if(data.success){
                showCardModal(card_order_url)
                $('#id-form-content').removeClass('d-none')
                $('#id-order-form-content').addClass('d-none')
            }
        })
      });


}

