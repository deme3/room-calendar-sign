// create WebSocket connection
const socket = io.connect("ws://" + window.location.hostname + ":8080");
let last_updated_events = null;

// Connection opened
socket.on("connect", (event) => {
  console.log("WebSocket connected");
  document.querySelector("body").classList.add("connected");
  document.querySelector("#refresh-btn").removeAttribute("disabled");
});

// Listen for messages
socket.on("message", (data) => {
  const {
    latest_event,
    upcoming_events,
    occupied,
    almost_occupied,
    just_finished,
    available,
  } = data;

  // do something with the received data
  console.log("Upcoming activities:", upcoming_events);
  console.log("Occupied:", occupied);
  console.log("Just finished:", just_finished);
  console.log("Available:", available);

  let statusClass = "available";
  let latestEvent = (latest_event && {
    name: latest_event.event_name,
    start: new Date(latest_event.start_time),
    end: new Date(latest_event.end_time),
  }) || {
    name: "Nessuna attività",
    start: new Date(),
    end: new Date(),
  };

  if (occupied) {
    statusClass = "occupied";
  } else if (almost_occupied) {
    statusClass = "almost-occupied";
  } else if (just_finished) {
    statusClass = "just-finished";
  }

  // update the status
  const activityName = document.querySelector("main .room-status > .activity");
  const activityDuration = document.querySelector(
    "main .room-status > .duration"
  );
  document.querySelector("main").className = statusClass;

  if (statusClass === "available") {
    activityName.innerText = "Nessuna attività";
    activityDuration.innerText = "Aula libera";
  } else if (statusClass === "just-finished") {
    activityName.innerText = latestEvent.name;
    activityDuration.innerHTML =
      "Terminata alle " +
      latestEvent.end.toLocaleTimeString("it-IT", {
        hour: "2-digit",
        minute: "2-digit",
      });
  } else {
    activityName.innerText = latestEvent.name;
    activityDuration.innerHTML =
      latestEvent.start.toLocaleTimeString("it-IT", {
        hour: "2-digit",
        minute: "2-digit",
      }) +
      " &mdash; " +
      latestEvent.end.toLocaleTimeString("it-IT", {
        hour: "2-digit",
        minute: "2-digit",
      });
  }

  // update the upcoming activities only if they differ
  let do_update = false;

  if (last_updated_events !== null) {
    for (let i = 0; i < upcoming_events.length; i++) {
      if (
        upcoming_events[i].event_name !== last_updated_events[i].event_name ||
        upcoming_events[i].start_time !== last_updated_events[i].start_time ||
        upcoming_events[i].end_time !== last_updated_events[i].end_time
      ) {
        console.log("Found a difference in the upcoming events");
        do_update = true;
        break;
      }
    }
  } else do_update = true;

  if (!do_update) return;

  const upcomingEvents = document.querySelector("main .action-bar .upcoming");
  upcomingEvents.innerHTML = "";

  if (upcoming_events.length > 0) {
    const marqueeContainer = document.createElement("div");
    marqueeContainer.className = "marquee";

    const marquees = [
      document.createElement("div"),
      document.createElement("div"),
    ];
    upcoming_events.forEach((event) => {
      for (marquee of marquees) {
        const eventElement = document.createElement("div");
        eventElement.className = "event";

        const eventNameElement = document.createElement("span");
        eventNameElement.className = "event-name";

        const eventNameDuration = document.createElement("span");
        eventNameDuration.className = "event-duration";

        const eventName = document.createTextNode(event.event_name);
        const eventStart = new Date(event.start_time);
        const eventEnd = new Date(event.end_time);
        const eventDuration = document.createTextNode(
          " " +
            eventStart.toLocaleTimeString("it-IT", {
              hour: "2-digit",
              minute: "2-digit",
            }) +
            " &mdash; " +
            eventEnd.toLocaleTimeString("it-IT", {
              hour: "2-digit",
              minute: "2-digit",
            })
        );

        // if not today, specify the date
        if (
          eventStart.toLocaleDateString("it-IT", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
          }) !==
          new Date().toLocaleDateString("it-IT", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
          })
        ) {
          eventDuration.textContent =
            " " +
            eventStart.toLocaleDateString("it-IT", {
              weekday: "short",
              day: "2-digit",
              month: "short",
            }) +
            ", " +
            eventDuration.textContent;
        }

        eventNameElement.appendChild(eventName);
        eventNameDuration.innerHTML = eventDuration.textContent;
        eventElement.appendChild(eventNameElement);
        eventElement.appendChild(eventNameDuration);
        marquee.appendChild(eventElement);
      }
    });
    marqueeContainer.style = "--velocity: " + upcoming_events.length * 10 + "s";
    marqueeContainer.appendChild(marquees[0]);
    marqueeContainer.appendChild(marquees[1]);
    upcomingEvents.appendChild(marqueeContainer);
  } else {
    upcomingEvents.innerHTML =
      "<div class='no-events'>Nessun evento in programmazione.</div>";
  }
  last_updated_events = upcoming_events;
});

// Handle errors
socket.on("error", (event) => {
  console.error("WebSocket error:", event);
});

// Handle closed connection
socket.on("disconnect", (event) => {
  console.log("WebSocket closed:", event);
  document.querySelector("body").classList.remove("connected");
  document.querySelector("#refresh-btn").setAttribute("disabled", true);
});

document.addEventListener("DOMContentLoaded", () => {
  const refreshBtn = document.querySelector("#refresh-btn");
  refreshBtn.addEventListener("click", () => {
    socket.emit("update");
  });

  socket.emit("update");

  if (socket.connected) {
    document.querySelector("body").classList.add("connected");
    document.querySelector("#refresh-btn").removeAttribute("disabled");
  }
});
