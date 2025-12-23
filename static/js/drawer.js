import $ from 'jquery';
import { ajaxPost, ajaxGet } from './ajax';

const initializeDrawerAndFormAjax = (formSelector, getFormCallback, submitFormCallback = '') => {
    const formButton = `.${formSelector}-form`;
    const idForm = `#id-${formSelector}-form`;
    const idFormContent = `#id-form-content`;
    const elementDrawer = `id-${formSelector}-drawer`;

    const getDrawerOptions = () => ({
        placement: 'right',
        backdrop: true,
        bodyScrolling: false,
        edge: false,
        edgeOffset: '',
        backdropClasses: 'bg-gray-900 bg-opacity-50 dark:bg-opacity-80 fixed inset-0 z-30',
        onHide: () => {
        },
        onShow: () => {
          console.log('drawer is shown');
        },
        onToggle: () => {
          console.log('drawer has been toggled');
        }
    });

  $(document).on("click", formButton, function() {
      alert('test...')
      const $targetEl = document.getElementById(elementDrawer);
      const url = $(this).data('url')
      const funnel = $(this).data('id')
      const options = getDrawerOptions()
      ajaxGet(url, {'funnel': funnel}, (data) => {
        $(idFormContent).html(data);
        getFormCallback(data)
      }, (error) => {
        console.error('An error occurred during the AJAX request:', error);
      });
  });



  $(document).on("submit", idForm, (event) => {
    event.preventDefault();
    const url = $(event.currentTarget).attr('action')
    const formData = $(event.currentTarget).serialize()
    ajaxPost(url, formData, (data) => {
        if(data.success){
            location.reload()
        }
    })
  });

};

export {
  initializeDrawerAndFormAjax
};