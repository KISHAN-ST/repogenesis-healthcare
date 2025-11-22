// script.js
console.log("AKATSUKI script loaded — fetch URL:", "http://127.0.0.1:8000/predict");
document.addEventListener("DOMContentLoaded", () => {
  const whenEl = document.getElementById("when");
  const pickRow = document.getElementById("pick-time-row");
  whenEl.addEventListener("change", () => {
    pickRow.style.display = whenEl.value === "pick_time" ? "block" : "none";
  });

  document.getElementById("detect").addEventListener("click", () => {
    if (!navigator.geolocation) {
      alert("Geolocation not supported");
      return;
    }
    navigator.geolocation.getCurrentPosition(async pos => {
      // for demo: use lat/lon to call a pincode lookup - here we mock it
      const p = "5600" + String(Math.floor(Math.random()*90)+10);
      document.getElementById("pincode").value = p;
      alert("Pincode detected (mock): " + p);
    }, err => {
      alert("Location denied or failed");
    });
  });

  document.getElementById("predictBtn").addEventListener("click", predictHandler);
  document.getElementById("bookNow").addEventListener("click", bookHandler);

  // slot selection
  let selectedSlot = null;
  window.selectSlot = function(slotEl, slotValue) {
    document.querySelectorAll(".slot").forEach(s => s.classList.remove("selected"));
    slotEl.classList.add("selected");
    selectedSlot = slotValue;
  }
});

async function predictHandler() {
  const hospital = document.getElementById("hospital").value;
  const when = document.getElementById("when").value;
  let hour = null;
  if (when === "now") {
    hour = new Date().getHours();
  } else if (when === "in_1_hour") {
    hour = new Date(new Date().getTime() + 60*60*1000).getHours();
  } else if (when === "today_evening") {
    hour = 18;
  } else if (when === "tomorrow_morning") {
    hour = 9;
  } else {
    const t = document.getElementById("picked_time").value || "09:00";
    hour = parseInt(t.split(":")[0]);
  }
  const weekday = new Date().getDay() === 0 ? 6 : new Date().getDay() - 1; // map JS day -> 0=Mon
  const problem = document.getElementById("problem").value;
  const pincode = document.getElementById("pincode").value || null;

  const payload = { hospital, hour, weekday, problem, pincode, want_booking: true };
  const url = "http://127.0.0.1:8000/predict";

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type":"application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.text();
      alert("Server error: " + err);
      return;
    }
    const data = await res.json();
    showResult(data);
  } catch (err) {
    console.error(err);
    alert("Failed to connect to backend. Make sure FastAPI server is running at http://127.0.0.1:8000");
  }
}

function showResult(data) {
  document.getElementById("result").style.display = "block";
  document.getElementById("res_hospital").innerText = data.hospital;
  document.getElementById("res_wait").innerText = (data.wait_minutes) + " mins";
  document.getElementById("res_inflow").innerText = "Est. inflow: " + data.inflow_est + " patients";
  // crowd badge
  const c = data.crowd_score;
  const badge = document.createElement("span");
  badge.className = "badge " + (data.crowd_category === "Low" ? "low" : (data.crowd_category==="Moderate"?"moderate":"high"));
  badge.innerText = data.crowd_category + " (" + data.crowd_score + ")";
  const resCrowd = document.getElementById("res_crowd");
  resCrowd.innerHTML = "";
  resCrowd.appendChild(badge);

  // suggestions
  const ul = document.getElementById("res_suggestions");
  ul.innerHTML = "";
  if (data.suggestions && data.suggestions.length) {
    data.suggestions.forEach(s => {
      const li = document.createElement("li");
      li.innerText = `${s.hospital} — est wait ${s.est_wait} mins`;
      ul.appendChild(li);
    });
  } else {
    const li = document.createElement("li");
    li.innerText = "No nearby alternatives found";
    ul.appendChild(li);
  }

  // show slots
  const slotArea = document.getElementById("slotArea");
  slotArea.innerHTML = "";
  if (data.recommended_slots && data.recommended_slots.length) {
    data.recommended_slots.forEach(s => {
      const el = document.createElement("div");
      el.className = "slot";
      el.innerText = s;
      el.onclick = (ev) => { window.selectSlot(ev.target, s); };
      slotArea.appendChild(el);
    });
  }
}

async function bookHandler() {
  const name = prompt("Enter your name (demo)");
  if (!name) return;
  const phone = prompt("Enter your phone (demo)");
  if (!phone) return;
  const hospital = document.getElementById("hospital").value;
  // find selected slot
  const selected = document.querySelector(".slot.selected");
  if (!selected) { alert("Please select a slot"); return; }
  const slot = selected.innerText;
  const payload = { hospital, slot, name, phone, fee_paid: 199.0 };
  try {
    const res = await fetch("http://127.0.0.1:8000/book", {
      method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload)
    });
    if (!res.ok) { alert("Booking failed"); return; }
    const data = await res.json();
    const el = document.getElementById("bookResult");
    el.innerHTML = `<div><strong>Booking confirmed</strong><br/>Booking ID: ${data.booking_id}<br/>Token: ${data.token}<br/>Estimated wait: ${data.estimated_wait} mins</div>`;
  } catch (err) {
    console.error(err);
    alert("Booking failed due to network error");
  }
}
