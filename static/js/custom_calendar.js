var selectedEvents = []; // Declare globally
var deselectedEvents = []; 
var isAbonnementManuallyChanged = false;






function initHTMXCalendar(eventsData, checkAll = false) {
    selectedEvents = [];
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'customSwitch'
        },
        customButtons: {
            customSwitch: {
                text: '', // Leave text empty as we will replace it with custom HTML
                click: function() {
                    // Optional logic can go here
                    console.log('Switch toggled!');
                }
            }
          },
  
        slotMinTime: '06:00:00',
        slotDuration: '01:00:00',
        events: eventsData,
        selectable: true,
        eventDidMount: function(info) {
            var selectedEventsDiv = document.getElementById('eventsId');
            info.el.setAttribute('data-event-id', info.event.extendedProps.pk_event);
            
            // console.log("selectedEventsDiv.dataset.selected>>>>>", selectedEventsDiv.dataset.selectedEvents);
            if (selectedEventsDiv) {
                var selectedEventsData = selectedEventsDiv.dataset.selectedEvents ? JSON.parse(selectedEventsDiv.dataset.selectedEvents) : [];
                selectedEvents = selectedEventsData.length > 0 ? selectedEventsData : [];
            }
            var preSelectedEvent = selectedEvents.find(event => event.creneaux__pk === info.event.extendedProps.pk_event);
            if (preSelectedEvent) {
                info.el.classList.add('selected-event');
            }
            if (checkAll) {
                selectAllEvents(eventsData, calendar);
            }
            addSelectedEventsVals(selectedEvents);

        },
        eventClick: function(info) { // info c'est creneau
            info.jsEvent.preventDefault();
            var selectedEvent = {
                creneaux__pk: info.event.extendedProps.pk_event,
                creneaux__name: info.event.title,
                creneaux__hour_start: info.event.start.toISOString(),
                creneaux__hour_finish: info.event.end.toISOString(),
                url: info.event.url
            };

            var index = selectedEvents.findIndex(event => {
                return event.creneaux__pk === info.event.extendedProps.pk_event;
            });
            if (index === -1) {
                info.el.classList.add('selected-event');
                selectedEvents.push(selectedEvent);
            } else {
                info.el.classList.remove('selected-event');
                selectedEvents.splice(index, 1);  // Remove event from selectedEvents
            }
            addSelectedEventsVals(selectedEvents);
        }
    });
    calendar.render();

    // Replace the custom button with a switch
    const customSwitch = document.querySelector('.fc-customSwitch-button');
    if (customSwitch) {
        customSwitch.outerHTML = `
            <div class="form-check form-switch form-check-custom form-check-solid">
                <input class="form-check-input" type="checkbox" value="" id="flexSwitchChecked" ${checkAll ? 'checked' : ''} />
                <label class="form-check-label" for="flexSwitchChecked">
                    Selectionner tous
                </label>
            </div>
        `;
        // Add event listener to handle interactions with the switch
        const switchInput = document.getElementById('flexSwitchChecked');
        console.log("switchInput------", switchInput);
        
        switchInput.addEventListener('change', (e) => {
            if (e.target.checked) {
                console.log("switchInput.checked------", switchInput.checked);
                
                selectAllEvents(eventsData);
            } else {
                console.log("switchInput.UN checked------", switchInput.checked);
                deselectAllEvents();
            }
        });
    }
    // If `checkAll` is true, apply the initial state
    if (checkAll) {
        selectAllEvents();
    }
}
function selectAllEvents(eventsData) {
    console.log("selectAllEvents called with eventsData:", eventsData);
    selectedEvents = [];
    eventsData.forEach(event => {
        console.log("Processing event:", event);
        const eventElement = document.querySelector(`[data-event-id="${event.pk_event}"]`);
        if (eventElement) {
            console.log("Adding 'selected-event' class to eventElement:", eventElement);
            eventElement.classList.add('selected-event');
        }
        selectedEvents.push({
            creneaux__pk: event.pk_event,
            creneaux__name: event.title,
            // creneaux__hour_start: event.startTime.toISOString(),
            // creneaux__hour_finish: event.endTime.toISOString(),
            url: event.url
        });
    });
    console.log("Selected events after processing:", selectedEvents);
    addSelectedEventsVals(selectedEvents);
}


// Function to select all events
// function selectAllEvents() {
    
//     selectedEvents = [];
//     const allEventElements = document.querySelectorAll('.fc-event'); // Select all events with the class "fc-event"

//     console.log("allEventElements------", allEventElements);

//     allEventElements.forEach(eventElement => {
//         // Add the 'selected-event' class
//         eventElement.classList.add('selected-event');
        
//         // Find the corresponding event from FullCalendar using the event's ID
//         addSelectedEventsVals(selectedEvents);
//     });

// }

// Function to deselect all events
function deselectAllEvents() {
    selectedEvents = [];
    const allEventElements = document.querySelectorAll('.fc-event'); // Select all events with the class "fc-event"

    console.log("allEventElements------", allEventElements);

    allEventElements.forEach(eventElement => {
        // Add the 'selected-event' class
        eventElement.classList.remove('selected-event');
        // Find the corresponding event from FullCalendar using the event's ID
        addSelectedEventsVals(selectedEvents);
    });
}



function addSelectedEventsVals(selectedEvents) {
    var addAbonnementBtn = document.getElementById('add-abonnement-btn');
    
    if (selectedEvents.length > 0) {
        var eventPks = selectedEvents
            .filter(event => event.creneaux__pk && event.creneaux__pk !== 'null')  // Filter out null or invalid creneaux__pk
            .map(event => event.creneaux__pk);
            addAbonnementBtn.setAttribute('hx-vals', JSON.stringify({
                'event_pk': eventPks,
            }));
    } else {
        addAbonnementBtn.removeAttribute('hx-vals');
    }
}




function preInitHTMXCalendar() {
    const eventsBlock = document.querySelector("#eventsId");
    const events = JSON.parse(eventsBlock.dataset.events);
    initHTMXCalendar(events);

    var addAbonnementBtn = document.getElementById('add-abonnement-btn');
    addAbonnementBtn.addEventListener('click', function(event) {
        if (!document.getElementById("abonnement-select").value) {
            // Show custom styled alert using SweetAlert
            Swal.fire({
                icon: 'warning',
                title: 'Error',
                text: 'Veuillez choisir un abonnement type.',
                confirmButtonText: 'OK'
            });
            event.preventDefault();  // Prevent form submission
        } else if (selectedEvents.length === 0 || deselectedEvents.length === selectedEvents.length) {
            // Ensure that at least one event is selected
            Swal.fire({
                icon: 'warning',
                title: 'Error',
                text: 'Veuillez choisir un créneau ou des créneaux.',
                confirmButtonText: 'OK'
            });
            event.preventDefault();  // Prevent form submission
        }
    });
}









