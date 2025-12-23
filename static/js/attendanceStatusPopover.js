import Popover from 'bootstrap/js/dist/popover';
import { ajaxPost } from './ajax.js';

const statuses = [
    { id: 1, text: 'Работает', name: 'working'},
    { id: 2, text: 'Выходной', name: 'day_off'},
    { id: 3, text: 'Праздничный', name: 'holiday'},
    { id: 4, text: 'Прогул', name: 'absent'},
];

const popoverContent = statuses.map(status => `
    <div class="container mt-2 mb-2">
        <div class="d-flex align-items-center attendance-status">
            <div class="color-box ${status.name}"></div>
            <span>&nbsp&nbsp${status.text}</span>
        </div>
    </div>
`).join('');

const popoverOptions = {
    content: popoverContent,
    title: 'Выберите статус',
    html: true,
    trigger: 'click',
    placement: 'bottom'
};

function initializeAttendanceStatusPopover() {
    const popoverTargets = document.querySelectorAll('.popoverAttendanceTarget');
    popoverTargets.forEach(function(target) {
    var popover = new Popover(target, popoverOptions);

     target.addEventListener('show.bs.popover', function() {
        // Закрыть все другие popovers
        popoverTargets.forEach(function(otherTarget) {
            if (otherTarget !== target) {
                var otherPopover = Popover.getInstance(otherTarget);
                if (otherPopover) {
                    otherPopover.hide();
                }
            }
        });
    });

    target.addEventListener('shown.bs.popover', function() {
        var popoverElement = document.getElementById(popover.tip.id);
        var date = target.getAttribute('data-date');
        var userId = target.closest('tr').getAttribute('data-user');

        var colorBoxes = popoverElement.querySelectorAll('.attendance-status');
        colorBoxes.forEach(function(box, index) {
            var statusId = statuses[index].id; // Get the ID directly from the statuses array
            box.addEventListener('click', function() {
                var status = statuses.find(status => status.id === statusId);
                var name = status.name
                var url = '/work_time/attendance/form/';
                const data = {
                    status: name,
                    date: date,
                    user: userId
                }
                
                ajaxPost(url, data, (response)=>{
                    if(response.status == 'success'){
                        statuses.forEach(status => {
                            target.classList.remove(status.name)
                        })
                        target.classList.add(name)
                    }
                    else if(response.error == 'error'){
                        alert(response.errors)
                    }
                })
                popover.hide();
            });
        });
    });
});
}

// Exporting the specific function for external use.
export {
    initializeAttendanceStatusPopover
};