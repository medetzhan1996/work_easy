import $ from 'jquery';
import Cookies from 'js-cookie'

var csrftoken = Cookies.get('csrftoken');
function csrfSafeMethod(method) {
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function ajaxGet(url, data = {}, callback = () => {}) {
  $.ajax({
    url: url,
    method: "GET",
    data: data,
    success: (response) => {
      callback(response);
    },
    error: (xhr, status, error) => {
      callback(error);
    },
  });
}


function ajaxPost(url, data, callback = () => {}, errorCallback = () => {}) {
  $.ajax({
    url: url,
    method: "POST",
    data: data,
    success: (data) => {
      callback(data);
    },
    error: (xhr, status, error) => {
      errorCallback(xhr, status, error)
    },
  });
}


function ajaxSubmitForm(formElement, callback) {
  const url = formElement.action;
  const method = formElement.method;
  const data = new FormData(formElement);

  $.ajax({
    url: url,
    method: method,
    data: data,
    processData: false,
    contentType: false,
    success: (data) => {
      callback(null, data);
    },
    error: (xhr, status, error) => {
      callback(error);
    },
  });
}

export {
  ajaxGet,
  ajaxPost,
  ajaxSubmitForm
};


