console.log("AKATSUKI script loaded");

// GLOBAL variable to store selected hospital
let selectedHospital = null;

// --------------------------------------------
// HOSPITAL CARD SELECTION
// --------------------------------------------
function chooseHospital(name) {
  selectedHospital = name;
  console.log("Selected hospital:", selectedHospital);

  // Remove highlight from all cards
  document.querySelectorAll(".hospital-card").forEach(card => {
    card.classList.remove("active");
  });

  // Highlight selected card
  const card = document.getElementById(name);
  if (card) card.classList.add("active");
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

  const weekday = new Date().getDay();
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

  const url = "http://127.0.0.1:8000/predict";

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
  document.getElementById("result").style.display = "block";

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
    el.onclick = () => selectSlot(el, slot);
    slotArea.appendChild(el);
  });
}

// --------------------------------------------
// SLOT SELECTION
// --------------------------------------------
function selectSlot(el, val) {
  document.querySelectorAll(".slot").forEach(x => x.classList.remove("selected"));
  el.classList.add("selected");
  window.selectedSlot = val;
}
