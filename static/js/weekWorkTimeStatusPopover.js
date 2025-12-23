import Popover from 'bootstrap/js/dist/popover';
import { ajaxPost } from './ajax.js';

const statuses = [
    { id: 1, text: 'Рабочий день', name: 'working' },
    { id: 2, text: 'Выходной', name: 'non-working' }
];

const popoverContent = statuses.map(status => `
    <div class="container mt-2 mb-2">
        <div class="d-flex align-items-center week_work_time-status">
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

function initializeWeekWorkTimeStatusPopover() {
    const popoverTargets = document.querySelectorAll('.popoverWeekWorkTimeTarget');
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
        var week = target.getAttribute('data-week');
        var userId = target.closest('tr').getAttribute('data-user');

        var colorBoxes = popoverElement.querySelectorAll('.week_work_time-status');
        colorBoxes.forEach(function(box, index) {
            var statusId = statuses[index].id; // Get the ID directly from the statuses array
            box.addEventListener('click', function() {
                var status = statuses.find(status => status.id === statusId);
                var url = `/work_time/week/work_time/form/`;
                var name = status.name
                const data = {
                    status: name,
                    week: week,
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
    initializeWeekWorkTimeStatusPopover
};