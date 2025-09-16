htmx.on("closeModal", (event) => {
	
	if (event.detail.value) {
	var myModalEl = document.getElementById(event.detail.value);
	}else {
	var myModalEl = document.getElementById("kt_modal");
	}
	var modal = bootstrap.Modal.getInstance(myModalEl)
	// const modal = new bootstrap.Modal(document.getElementById("kt_modal"))
	// console.log("closeModal",event.detail.value);
	// console.log("modal",modal);
	if (modal) {
	// console.log("LOGGING MODAL ", modal);
	modal.hide()
	} 
})

// htmx.logAll();



htmx.onLoad(function(){
	KTComponents.init();
})

htmx.on('total_revenu', (e) => {
    // KTComponents.init();
    console.log("YOYAL REVENUE", e.detail);
    console.log("YOYAL ISDDDDD", document.getElementById('theTotalId'));
    
    document.getElementById('theTotalId').innerHTML = e.detail.value;
    
});


document.addEventListener('htmx:afterSettle', (e) => {
    // console.log("htmx:afterSettle");
    const eventsBlock = document.querySelector("#eventsId");

    if (eventsBlock) {
        setTimeout(function(){
            preInitHTMXCalendar(); 
        },100)
    }
});




document.addEventListener('DOMContentLoaded', function () {
    // console.log("Document loaaaded lets call the callendar");
    
    const eventsBlock = document.querySelector("#eventsId");
    if (eventsBlock) {
        preInitHTMXCalendar();
    }
});


document.addEventListener("htmx:load", function() {
    KTComponents.init();
});


window.addEventListener('load', () => {
    const toastrMessages = localStorage.getItem('toastrMessages');
    if (toastrMessages) {
        const messages = JSON.parse(toastrMessages);
        messages.forEach(msg => {
            if (msg.tags.includes('toastr')) {
                // Display Toastr notifications based on the message type
                if (msg.tags.includes('error')) {
                    toastr.error(msg.message);
                } else if (msg.tags.includes('warning')) {
                    toastr.warning(msg.message);
                } else if (msg.tags.includes('info')) {
                    toastr.info(msg.message);
                } else if (msg.tags.includes('success')) {
                    toastr.success(msg.message);
                }
            }
        });
        // Clear the stored messages to avoid showing them again
        localStorage.removeItem('toastrMessages');
    }
});









var start = moment().subtract(29, "days");
var end = moment();

function cb(start, end) {
    $("#kt_daterangepicker_4").html(start.format("MMMM D, YYYY") + " - " + end.format("MMMM D, YYYY"));
    // console.log("date changes-----", document.querySelector('input[name="start_date"]').value);
    document.querySelector('input[name="start_date"]').value = start.format("YYYY-MM-DD");
    document.querySelector('input[name="end_date"]').value = end.format("YYYY-MM-DD");
    var chartContainers = document.querySelectorAll('.chart-container');
    
    // Trigger 'date_changed' event on each chart container
    chartContainers.forEach(function(el) {
        htmx.trigger(el, 'date_changed');
    });

}

$("#kt_daterangepicker_4").daterangepicker({
    startDate: start,
    endDate: end,
    ranges: {
        "aujourd'hui": [moment(), moment()],
        "hier": [moment().subtract(1, "days"), moment().subtract(1, "days")],
        "dernier 7 jours": [moment().subtract(6, "days"), moment()],
        "dernier 30 jours": [moment().subtract(29, "days"), moment()],
        "ce mois": [moment().startOf("month"), moment().endOf("month")],
        "mois dernier": [moment().subtract(1, "month").startOf("month"), moment().subtract(1, "month").endOf("month")]
    }
}, cb);




function isModalOpen(modalId) {
    const modalElm = document.getElementById(modalId);
    
    if (!modalElm) return false;

    return modalElm.classList.contains('show')
}


function optionFormat(item) {
    if (!item.id) {
        return item.text;
    }

    // pull the attributes once
    const iconUrl = item.element.getAttribute('data-kt-rich-content-icon');
    const subText = item.element.getAttribute('data-kt-rich-content-subcontent');

    // build your template string conditionally
    let template = '<div class="d-flex align-items-center">';

    if (iconUrl) {
        template +=
          '<img src="' + iconUrl + 
          '" class="rounded-circle h-40px me-3" alt="' + item.text + '"/>';
    }

    template += '<div class="d-flex flex-column">';
    template += '<span class="fs-4 fw-bold lh-1">' + item.text + '</span>';

    if (subText) {
        template +=
          '<span class="text-muted fs-5">' + subText + '</span>';
    }

    template += '</div></div>';

    const span = document.createElement('span');
    span.innerHTML = template;
    return $(span);
}


function initializeSelect2() {
    const isModalVisible = isModalOpen('kt_modal');
    const dropdownParent = isModalVisible ? $('#kt_modal_content') : null;

    document.querySelectorAll('[data-control="select2"]').forEach((element) => {
        const options = { dropdownParent: dropdownParent };

        if (element.getAttribute('data-hide-search') === 'true') {
            options.minimumResultsForSearch = Infinity;
        }
        if (element.getAttribute('data-kt-rich-content') === 'true') {
            options.templateResult = optionFormat;
            options.templateSelection = optionFormat;
        }
        $(element).select2(options);
    });
}


htmx.on('htmx:afterSwap', () => {
    KTMenu.createInstances();
    setTimeout(() => {
        initializeSelect2();
    }, 100);








});

// Run after Bootstrap modal hidden
window.addEventListener('hidden.bs.modal', () => {
    initializeSelect2();
});


window.addEventListener("DOMContentLoaded", (e) => {
    document.addEventListener("htmx:load", function() {
        $('.per-page-select').on('select2:select select2:unselect', function (e) {
            const form = document.getElementById('filterForm');
            if (form) {
                form.dispatchEvent(new Event('change'));
            }
        });
        $('.form-select').on('select2:select select2:unselect', function (e) {
            $(this).closest('select').get(0).dispatchEvent(new Event('changed'));
            // console.log("AFFECT SELECT CHANGED");

            const form = $(this).closest('form');
            if (form.length > 0) {
                form.get(0).dispatchEvent(new Event('change'));
            }
        });
 
    });
});



htmx.on('htmx:beforeSend', (e) => {
    var button = document.querySelector("#submitButton");
    if (button){
        button.setAttribute("data-kt-indicator", "on");
    }
});

htmx.on('htmx:afterRequest', (e) => {
    var button = document.querySelector("#submitButton");
    if (button && button.hasAttribute("data-kt-indicator")) {
        button.removeAttribute("data-kt-indicator");
    }
});

