console.log("AKATSUKI script loaded");

// GLOBAL variables to store selected hospital/slot
let selectedHospital = null;
let selectedSlot = null;

// --------------------------------------------
// HOSPITAL CARD SELECTION
// --------------------------------------------
function chooseHospital(name) {
  selectedHospital = name;
  console.log("Selected hospital:", selectedHospital);

  // Remove highlight from all cards (predict.html uses class 'hcard' and 'sel')
  document.querySelectorAll(".hcard").forEach(card => {
    card.classList.remove("sel");
  });

  // Highlight the matching card by data-name or id
  const card = document.querySelector(`.hcard[data-name="${name}"]`) || document.getElementById(name);
  if (card) card.classList.add("sel");
}

// --------------------------------------------
// PREDICT HANDLER
// --------------------------------------------
async function predictHandler() {
  if (!selectedHospital) {
    alert("Please select a hospital before predicting.");
    return;
  }

  const when = document.getElementById("when").value;
  let hour = null;

  if (when === "now") hour = new Date().getHours();
  else if (when === "in_1_hour") hour = new Date(Date.now() + 3600000).getHours();
  else if (when === "today_evening") hour = 18;
  else if (when === "tomorrow_morning") hour = 9;
  else {
    const t = document.getElementById("picked_time").value || "09:00";
    hour = parseInt(t.split(":")[0]);
  }

  // Map JS getDay (0=Sun..6=Sat) to Python weekday (0=Mon..6=Sun)
  const jsDay = new Date().getDay();
  const weekday = (jsDay + 6) % 7;
  const problem = document.getElementById("problem").value;
  const pincode = document.getElementById("pincode").value || null;

  const payload = {
    hospital: selectedHospital,
    hour,
    weekday,
    problem,
    pincode,
    want_booking: true
  };

  console.log("Sending payload:", payload);

  // use relative path so the frontend works when served by backend at /static or /ui
  const url = "/predict";

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      alert("Backend error");
      return;
    }

    const data = await res.json();
    console.log("Backend response:", data);
    showResult(data);

  } catch (err) {
    console.error(err);
    alert("Cannot connect to backend. Make sure FastAPI (uvicorn) is running on port 8000.");
  }
}

// --------------------------------------------
// SHOW RESULT IN UI
// --------------------------------------------
function showResult(data) {
  // predict.html uses id `resultCard`
  const resultEl = document.getElementById("resultCard") || document.getElementById("result");
  if (resultEl) resultEl.style.display = "block";

  document.getElementById("res_hospital").innerText = data.hospital;
  document.getElementById("res_wait").innerText = `${data.wait_minutes} mins`;

  const badge = `
      <span class="badge ${data.crowd_category.toLowerCase()}">
        ${data.crowd_category} (${data.crowd_score})
      </span>
  `;
  document.getElementById("res_crowd").innerHTML = badge;

  const slotArea = document.getElementById("slotArea");
  slotArea.innerHTML = "";

  (data.recommended_slots || []).forEach(slot => {
    const el = document.createElement("div");
    el.className = "slot";
    el.innerText = slot;
    el.addEventListener('click', () => selectSlot(el, slot));
    slotArea.appendChild(el);
  });
}

// --------------------------------------------
// SLOT SELECTION
// --------------------------------------------
function selectSlot(el, val) {
  // predict.html uses class 'sel' for selected slot
  document.querySelectorAll(".slot").forEach(x => x.classList.remove("sel"));
  el.classList.add("sel");
  selectedSlot = val;
  window.selectedSlot = val;
}

function gotoBooking() {
  if (!selectedSlot && !window.selectedSlot) return alert('Select a slot first');
  const hosp = document.getElementById('res_hospital')?.innerText || selectedHospital;
  const slot = selectedSlot || window.selectedSlot;
  if (!hosp || !slot) return alert('Missing hospital or slot');
  localStorage.setItem('ak_booking_hospital', hosp);
  localStorage.setItem('ak_booking_slot', slot);
  // redirect to booking page served by backend
  window.location.href = '/static/booking.html';
}

// Wire up page events if elements exist
document.addEventListener('DOMContentLoaded', () => {
  // Attach hospital card click handlers if present
  document.querySelectorAll('.hcard').forEach(card => {
    // prefer data-name attribute
    const name = card.dataset.name || card.id || card.getAttribute('data-id');
    card.addEventListener('click', () => {
      if (name) chooseHospital(name);
    });
  });

  const predictBtn = document.getElementById('predictBtn');
  if (predictBtn) predictBtn.addEventListener('click', predictHandler);

  const goBook = document.getElementById('goBook');
  if (goBook) goBook.addEventListener('click', gotoBooking);
});