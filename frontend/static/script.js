/**
 * AI Orthopaedic Assistant — Interactive Dashboard Script
 * Handles drag & drop, AJAX prediction, GSAP animations, Chart.js,
 * theme toggling, tab switching, healing prediction, rehab, and nearby real hospital finder.
 */

// Global State
let weeklyChartInstance = null;
let monthlyChartInstance = null;

let historyRecordsCache = [];
let userCurrentCoords = { lat: 16.7305, lng: 74.4724 }; // Fallback to Ichalkaranji/Kolhapur coords
let currentPredictionState = { prediction: "Fractured", severity: "Moderate", confidence: 95.0 };

let currentUserId = "";

function savePredictionToVault(record) {
  try {
    const raw = localStorage.getItem("drx_history_vault");
    const list = raw ? JSON.parse(raw) : [];
    list.unshift(record);
    localStorage.setItem("drx_history_vault", JSON.stringify(list));
  } catch (e) {
    console.warn("Vault save prediction notice:", e);
  }
}

window.handleLogout = function () {
  localStorage.removeItem("drx_user");
  window.location.href = "/";
};

document.addEventListener("DOMContentLoaded", () => {
  // 0. AUTH SESSION CHECK
  const localUser = localStorage.getItem("drx_user");
  if (!localUser && !window.location.pathname.includes("/login")) {
    window.location.href = "/login";
    return;
  }
  if (localUser) {
    try {
      const parsedUser = JSON.parse(localUser);
      currentUserId = parsedUser.id || "";
      const userNameElem = document.getElementById("userNameDisplay");
      if (userNameElem && parsedUser.name) {
        userNameElem.textContent = parsedUser.name;
      }
    } catch (e) {
      console.warn("Invalid user session");
    }
  }

  // DOM Elements
  const currentDateDisplay = document.getElementById("currentDateDisplay");
  const dropZone = document.getElementById("dropZone");
  const imageFileInput = document.getElementById("imageFileInput");
  const uploadDropzoneUI = document.getElementById("uploadDropzoneUI");
  const previewUI = document.getElementById("previewUI");
  const previewImg = document.getElementById("previewImg");
  const previewFileName = document.getElementById("previewFileName");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const analyzeBtnText = document.getElementById("analyzeBtnText");
  const analyzeSpinner = document.getElementById("analyzeSpinner");
  const resultDashboard = document.getElementById("resultDashboard");
  const resultImage = document.getElementById("resultImage");
  const heatmapContainer = document.getElementById("heatmapContainer");
  const heatmapImage = document.getElementById("heatmapImage");
  const predictionPill = document.getElementById("predictionPill");
  const predictionLabel = document.getElementById("predictionLabel");
  const confidenceProgressRing = document.getElementById("confidenceProgressRing");
  const confidenceValue = document.getElementById("confidenceValue");
  const subInferenceTime = document.getElementById("subInferenceTime");
  const subSeverity = document.getElementById("subSeverity");
  const subEmergency = document.getElementById("subEmergency");
  const suggestionContent = document.getElementById("suggestionContent");
  const healingSection = document.getElementById("healingSection");
  const doctorsSection = document.getElementById("doctorsSection");

  let selectedFile = null;

  // ========================================================================
  // 1. GSAP INITIAL LOAD ANIMATIONS
  // ========================================================================
  gsap.from(".sidebar", { x: -60, opacity: 0, duration: 0.5, ease: "power3.out" });
  gsap.from(".top-bar", { y: -20, opacity: 0, duration: 0.4, delay: 0.15, ease: "power2.out" });
  gsap.fromTo(
    ".hero-glass",
    { y: 25, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.5, delay: 0.25, ease: "power2.out", clearProps: "opacity,transform" }
  );

  // Initial History Load for Rehab Selector
  loadRehabPatientHistory();

  // Read URL query parameter for tab selection (e.g. /?tab=analytics)
  const urlParams = new URLSearchParams(window.location.search);
  const initialTab = urlParams.get("tab");
  const targetPatientId = urlParams.get("patient_id");

  if (initialTab && ["dashboard", "analysis", "analytics", "rehab", "doctors"].includes(initialTab)) {
    window.switchTab(initialTab);
    if (initialTab === "rehab" && targetPatientId) {
      setTimeout(() => {
        const select = document.getElementById("rehabPatientSelect");
        if (select) {
          select.value = targetPatientId;
          onRehabPatientSelected();
        }
      }, 500);
    }
  }

  // ========================================================================
  // 2. DATE DISPLAY
  // ========================================================================
  const updateCurrentDate = () => {
    const options = { weekday: "long", month: "short", day: "numeric", year: "numeric" };
    currentDateDisplay.textContent = new Date().toLocaleDateString("en-US", options);
  };
  updateCurrentDate();

  // ========================================================================
  // 3. THEME SUPPORT
  // ========================================================================
  function initTheme() {
    const saved = localStorage.getItem("drx-theme") || "light";
    applyTheme(saved);

    document.querySelectorAll(".theme-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const theme = btn.dataset.theme;
        localStorage.setItem("drx-theme", theme);
        applyTheme(theme);
      });
    });

    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
      if (localStorage.getItem("drx-theme") === "system") {
        applyTheme("system");
      }
    });
  }

  function applyTheme(theme) {
    document.querySelectorAll(".theme-btn").forEach((b) => b.classList.remove("active"));
    const targetBtn = document.querySelector(`.theme-btn[data-theme="${theme}"]`);
    if (targetBtn) targetBtn.classList.add("active");

    let resolvedTheme;
    if (theme === "system") {
      resolvedTheme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    } else {
      resolvedTheme = theme;
    }

    gsap.to("body", {
      duration: 0.4,
      ease: "power2.inOut",
      onStart: () => {
        document.documentElement.setAttribute("data-theme", resolvedTheme);
      },
    });
  }

  initTheme();

  // ========================================================================
  // 4. AI ANALYTICS — Load Stats & Charts
  // ========================================================================
  async function loadDashboardStats() {
    try {
      const response = await fetch("/api/dashboard", {
        headers: { "X-User-ID": currentUserId }
      });
      const data = await response.json();

      animateCounterElement("statTotalPredictions", data.total_predictions);
      animateCounterElement("statFractures", data.fractures_detected);
      animateCounterElement("statNormal", data.normal_cases);
      const elAcc = document.getElementById("statAccuracy");
      if (elAcc) elAcc.textContent = `${data.model_accuracy}%`;
      const elConf = document.getElementById("statAvgConfidence");
      if (elConf) elConf.textContent = `${data.avg_confidence}%`;
      const elTime = document.getElementById("statAvgTime");
      if (elTime) elTime.textContent = `${data.avg_inference_time}s`;
    } catch (error) {
      console.error("Analytics stats error:", error);
    }
  }

  async function loadCharts() {
    try {
      const response = await fetch("/api/dashboard/charts", {
        headers: { "X-User-ID": currentUserId }
      });
      const data = await response.json();

      const isDark = document.documentElement.getAttribute("data-theme") === "dark";
      const textColor = isDark ? "#CBD5E1" : "#475569";
      const gridColor = isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)";

      // Analytics Tab Charts
      const weeklyCanvas = document.getElementById("weeklyChart");
      if (weeklyCanvas) {
        if (weeklyChartInstance) weeklyChartInstance.destroy();
        weeklyChartInstance = new Chart(weeklyCanvas, {
          type: "bar",
          data: {
            labels: data.weekly.labels,
            datasets: [
              {
                label: "Fractures",
                data: data.weekly.fractures,
                backgroundColor: "rgba(239, 68, 68, 0.75)",
                borderRadius: 8,
                barPercentage: 0.55,
              },
              {
                label: "Normal",
                data: data.weekly.normal,
                backgroundColor: "rgba(34, 197, 94, 0.75)",
                borderRadius: 8,
                barPercentage: 0.55,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: textColor, font: { family: "'Plus Jakarta Sans'", weight: "600" } } } },
            scales: {
              x: { ticks: { color: textColor, font: { weight: "600" } }, grid: { color: gridColor } },
              y: { beginAtZero: true, ticks: { color: textColor, stepSize: 1 }, grid: { color: gridColor } },
            },
          },
        });
      }

      const monthlyCanvas = document.getElementById("monthlyChart");
      if (monthlyCanvas) {
        if (monthlyChartInstance) monthlyChartInstance.destroy();
        monthlyChartInstance = new Chart(monthlyCanvas, {
          type: "line",
          data: {
            labels: data.monthly.labels,
            datasets: [
              {
                label: "Fractures",
                data: data.monthly.fractures,
                borderColor: "#EF4444",
                backgroundColor: "rgba(239, 68, 68, 0.12)",
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 8,
              },
              {
                label: "Normal",
                data: data.monthly.normal,
                borderColor: "#22C55E",
                backgroundColor: "rgba(34, 197, 94, 0.12)",
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 8,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: textColor, font: { family: "'Plus Jakarta Sans'", weight: "600" } } } },
            scales: {
              x: { ticks: { color: textColor, font: { weight: "600" } }, grid: { color: gridColor } },
              y: { beginAtZero: true, ticks: { color: textColor, stepSize: 1 }, grid: { color: gridColor } },
            },
          },
        });
      }
    } catch (error) {
      console.error("Charts error:", error);
    }
  }

  loadDashboardStats();
  loadCharts();

  // Try auto-detect location silently on load
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        userCurrentCoords = { lat: pos.coords.latitude, lng: pos.coords.longitude };
      },
      () => {}
    );
  }

  // ========================================================================
  // 5. DRAG & DROP EVENT LISTENERS
  // ========================================================================
  if (dropZone) {
    ["dragenter", "dragover"].forEach((eventName) => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add("drag-over");
      });
    });

    ["dragleave", "drop"].forEach((eventName) => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove("drag-over");
      });
    });

    dropZone.addEventListener("drop", (e) => {
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        handleFileSelection(files[0]);
      }
    });
  }

  if (imageFileInput) {
    imageFileInput.addEventListener("change", (e) => {
      if (e.target.files.length > 0) {
        handleFileSelection(e.target.files[0]);
      }
    });
  }

  // ========================================================================
  // 6. FILE SELECTION & PREVIEW
  // ========================================================================
  function handleFileSelection(file) {
    const validTypes = ["image/png", "image/jpeg", "image/jpg"];
    if (!validTypes.includes(file.type)) {
      alert("Please upload a valid image file (PNG, JPG, JPEG).");
      return;
    }

    selectedFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewFileName.textContent = file.name;
      uploadDropzoneUI.style.display = "none";
      previewUI.style.display = "flex";
      analyzeBtn.disabled = false;

      gsap.from(previewUI, { scale: 0.9, opacity: 0, duration: 0.4, ease: "back.out(1.7)" });
    };
    reader.readAsDataURL(file);
  }

  // ========================================================================
  // 7. PREDICTION REQUEST
  // ========================================================================
  if (analyzeBtn) {
    analyzeBtn.addEventListener("click", async () => {
      if (!selectedFile) return;

      analyzeBtn.disabled = true;
      analyzeSpinner.style.display = "inline-block";
      analyzeBtnText.textContent = "Running Analysis...";

      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("patient_name", document.getElementById("patientNameInput")?.value || "Unknown");

      try {
        const response = await fetch("/predict", {
          method: "POST",
          headers: { "X-User-ID": currentUserId },
          body: formData,
        });

        const data = await response.json();

        if (data.status === "success") {
          currentPredictionState = {
            prediction: data.prediction,
            severity: data.severity,
            confidence: data.confidence,
          };
          savePredictionToVault({
            id: Date.now(),
            user_id: currentUserId,
            patient_name: document.getElementById("patientNameInput")?.value || "Unknown",
            prediction_date: new Date().toISOString().replace('T', ' ').substring(0, 19),
            bone_type: "Bone X-ray",
            prediction: data.prediction,
            confidence: data.confidence,
            severity: data.severity,
            emergency_level: data.emergency_level,
            inference_time: data.inference_time,
            image_path: data.image_url,
            heatmap_path: data.heatmap_url
          });
          displayResults(data);
          loadDashboardStats();
          loadCharts();
          loadRehabPatientHistory();
        } else {
          alert(`Prediction Error: ${data.message}`);
        }
      } catch (error) {
        console.error("Inference Error:", error);
        alert("Failed to process prediction request. Please try again.");
      } finally {
        analyzeSpinner.style.display = "none";
        analyzeBtnText.textContent = "Analyze X-ray";
        analyzeBtn.disabled = false;
      }
    });
  }

  // ========================================================================
  // 8. DISPLAY RESULTS WITH GSAP ANIMATIONS
  // ========================================================================
  function displayResults(data) {
    resultDashboard.style.display = "block";
    resultImage.src = data.image_url;

    if (data.heatmap_url) {
      heatmapContainer.style.display = "block";
      heatmapImage.src = data.heatmap_url;
      gsap.from(heatmapContainer, { opacity: 0, x: 20, duration: 0.6, delay: 0.3, ease: "power2.out" });
    }

    const isFractured = data.prediction === "Fractured";
    predictionLabel.textContent = isFractured ? "Fractured Bone Detected" : "Not Fractured (Normal)";

    if (isFractured) {
      predictionPill.className = "prediction-pill fractured";
      confidenceProgressRing.style.stroke = "#EF4444";
    } else {
      predictionPill.className = "prediction-pill not-fractured";
      confidenceProgressRing.style.stroke = "#22C55E";
    }

    subInferenceTime.textContent = `${data.inference_time} s`;
    subSeverity.textContent = data.severity || "N/A";
    subEmergency.textContent = data.emergency_level || "None";
    suggestionContent.textContent = data.suggestion || "Analysis complete.";

    const severityColors = { Low: "#22C55E", Moderate: "#F59E0B", High: "#EF4444", Critical: "#DC2626" };
    subSeverity.style.color = severityColors[data.severity] || "var(--text-dark)";

    const circumference = 2 * Math.PI * 52;
    const strokeDashoffset = circumference - (circumference * data.confidence) / 100;
    confidenceProgressRing.style.strokeDashoffset = strokeDashoffset;

    animateCounter(data.confidence, confidenceValue);

    gsap.from(resultDashboard, { y: 40, opacity: 0, duration: 0.6, ease: "power3.out" });
    gsap.from(".sub-info-card", { y: 15, opacity: 0, duration: 0.3, stagger: 0.1, delay: 0.3, ease: "power2.out" });
    gsap.from("#suggestionCard", { y: 15, opacity: 0, duration: 0.4, delay: 0.6, ease: "power2.out" });

    resultDashboard.scrollIntoView({ behavior: "smooth", block: "start" });

    if (isFractured) {
      healingSection.style.display = "block";
      const healingSeveritySelect = document.getElementById("healingSeverity");
      if (healingSeveritySelect && data.severity !== "N/A") {
        healingSeveritySelect.value = data.severity;
      }
      gsap.from(healingSection, { y: 30, opacity: 0, duration: 0.5, delay: 0.7, ease: "power2.out" });
      if (doctorsSection) doctorsSection.style.display = "block";
      loadNearbyDoctors();
    } else {
      healingSection.style.display = "none";
      if (doctorsSection) doctorsSection.style.display = "none";
    }
  }

  // ========================================================================
  // 9. ANIMATED COUNTERS
  // ========================================================================
  function animateCounter(targetValue, element) {
    if (!element) return;
    let startValue = 0;
    const duration = 1000;
    const stepTime = 20;
    const steps = duration / stepTime;
    const increment = targetValue / steps;

    const timer = setInterval(() => {
      startValue += increment;
      if (startValue >= targetValue) {
        startValue = targetValue;
        clearInterval(timer);
      }
      element.textContent = `${startValue.toFixed(1)}%`;
    }, stepTime);
  }

  function animateCounterElement(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) return;

    let startValue = 0;
    const duration = 800;
    const stepTime = 25;
    const steps = duration / stepTime;
    const increment = targetValue / steps;

    const timer = setInterval(() => {
      startValue += increment;
      if (startValue >= targetValue) {
        startValue = targetValue;
        clearInterval(timer);
      }
      element.textContent = Math.round(startValue);
    }, stepTime);
  }

  // ========================================================================
  // 10. NEARBY DOCTORS
  // ========================================================================
  async function loadNearbyDoctors() {
    try {
      const response = await fetch(`/api/nearby-doctors?lat=${userCurrentCoords.lat}&lng=${userCurrentCoords.lng}`);
      const data = await response.json();
      if (data.status !== "success") return;

      doctorsSection.style.display = "block";
      renderDoctors(data.doctors, "doctorsGrid");
    } catch (error) {
      console.error("Nearby doctors error:", error);
    }
  }

  function renderDoctors(doctors, gridId) {
    const grid = document.getElementById(gridId);
    if (!grid) return;

    if (!doctors || doctors.length === 0) {
      grid.innerHTML = '<div class="empty-row" style="grid-column: 1/-1; text-align: center; padding: 40px;">No matching orthopedic hospitals found for this region/search.</div>';
      return;
    }

    grid.innerHTML = doctors.map(
      (doc) => `
      <div class="doctor-card">
        <div class="doctor-header">
          <div class="doctor-icon">🏥</div>
          <div>
            <h4>${doc.hospital_name}</h4>
            <p class="doctor-name">${doc.doctor_name}</p>
          </div>
        </div>
        <div class="doctor-details">
          <div class="doctor-detail"><span>📍 Distance</span><strong>${doc.distance_text}</strong></div>
          <div class="doctor-detail"><span>⭐ Rating</span><strong>${doc.rating}/5</strong></div>
          <div class="doctor-detail"><span>📞 Phone</span><strong>${doc.phone}</strong></div>
          <div class="doctor-detail"><span>🏙️ City</span><strong>${doc.city}</strong></div>
        </div>
        <p class="doctor-address">${doc.address}</p>
        <div class="doctor-actions-group">
          <a href="${doc.maps_url}" target="_blank" class="btn-maps primary">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
            </svg>
            Get Directions in Google Maps
          </a>
          <a href="${doc.maps_place_url}" target="_blank" class="btn-maps secondary">
            Open Place Card
          </a>
        </div>
      </div>
    `
    ).join("");

    gsap.from(`#${gridId} .doctor-card`, { y: 25, opacity: 0, duration: 0.4, stagger: 0.08, ease: "power2.out" });
  }
});

// ========================================================================
// DEDICATED NEARBY HOSPITALS TAB ENGINE
// ========================================================================
window.detectLiveLocation = function () {
  const statusBar = document.getElementById("locationStatusBar");
  if (statusBar) statusBar.textContent = "⌛ Requesting browser geolocation permission...";

  if (!navigator.geolocation) {
    if (statusBar) statusBar.textContent = "⚠️ Geolocation not supported by your browser. Using local region coordinates.";
    loadDedicatedNearbyDoctors();
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      userCurrentCoords = {
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      };
      if (statusBar) {
        statusBar.textContent = `✅ Live location detected: Lat ${userCurrentCoords.lat.toFixed(4)}, Lng ${userCurrentCoords.lng.toFixed(4)}. Showing closest hospitals!`;
      }
      loadDedicatedNearbyDoctors();
    },
    (err) => {
      if (statusBar) {
        statusBar.textContent = "📍 Geolocation permission denied or unavailable. Showing top local hospitals for your region.";
      }
      loadDedicatedNearbyDoctors();
    }
  );
};

window.onDoctorFilterChange = function () {
  let searchTimeout;
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    loadDedicatedNearbyDoctors();
  }, 300);
};

async function loadDedicatedNearbyDoctors() {
  const citySelect = document.getElementById("dedicatedDoctorCitySelect");
  const searchInput = document.getElementById("dedicatedDoctorSearch");

  const city = citySelect ? citySelect.value : "all";
  const search = searchInput ? searchInput.value : "";

  const params = new URLSearchParams({
    lat: userCurrentCoords.lat,
    lng: userCurrentCoords.lng,
    city: city,
    search: search,
  });

  try {
    const response = await fetch(`/api/nearby-doctors?${params}`);
    const data = await response.json();
    if (data.status !== "success") return;

    renderDedicatedDoctors(data.doctors);
  } catch (error) {
    console.error("Dedicated doctors error:", error);
  }
}

function renderDedicatedDoctors(doctors) {
  const grid = document.getElementById("dedicatedDoctorsGrid");
  if (!grid) return;

  if (!doctors || doctors.length === 0) {
    grid.innerHTML = '<div class="empty-row" style="grid-column: 1/-1; text-align: center; padding: 40px;">No matching real orthopedic hospitals found for your search query or region.</div>';
    return;
  }

  grid.innerHTML = doctors.map(
    (doc) => `
    <div class="doctor-card">
      <div class="doctor-header">
        <div class="doctor-icon">🏥</div>
        <div>
          <h4>${doc.hospital_name}</h4>
          <p class="doctor-name">${doc.doctor_name}</p>
        </div>
      </div>
      <div class="doctor-details">
        <div class="doctor-detail"><span>📍 Distance</span><strong>${doc.distance_text}</strong></div>
        <div class="doctor-detail"><span>⭐ Rating</span><strong>${doc.rating}/5</strong></div>
        <div class="doctor-detail"><span>📞 Phone</span><strong>${doc.phone}</strong></div>
        <div class="doctor-detail"><span>🏙️ City</span><strong>${doc.city}</strong></div>
      </div>
      <p class="doctor-address">${doc.address}</p>
      <div class="doctor-actions-group">
        <a href="${doc.maps_url}" target="_blank" class="btn-maps primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
          </svg>
          Get Directions in Google Maps
        </a>
        <a href="${doc.maps_place_url}" target="_blank" class="btn-maps secondary">
          Open Place Card
        </a>
      </div>
    </div>
  `
  ).join("");

  gsap.from("#dedicatedDoctorsGrid .doctor-card", { y: 25, opacity: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" });
}

// ========================================================================
// REHABILITATION PATIENT HISTORY SELECTOR & GENERATOR
// ========================================================================
async function loadRehabPatientHistory() {
  try {
    const response = await fetch("/api/history?page=1&per_page=100", {
      headers: { "X-User-ID": currentUserId }
    });
    const data = await response.json();

    if (data.status === "success" && data.records) {
      historyRecordsCache = data.records;
      const select = document.getElementById("rehabPatientSelect");
      if (!select) return;

      select.innerHTML = '<option value="">-- Choose Patient Record from History --</option>';

      data.records.forEach((r) => {
        const dateStr = r.prediction_date ? r.prediction_date.substring(0, 10) : "";
        select.innerHTML += `<option value="${r.id}">Patient #${r.id}: ${r.patient_name} — ${r.prediction} (${r.severity}) — ${dateStr}</option>`;
      });
    }
  } catch (error) {
    console.error("Failed to load patient history for rehab selector:", error);
  }
}

window.onRehabPatientSelected = function () {
  const select = document.getElementById("rehabPatientSelect");
  const recordId = parseInt(select ? select.value : 0);
  const infoCard = document.getElementById("patientRehabInfoCard");

  if (!recordId) {
    if (infoCard) infoCard.style.display = "none";
    generateCustomRehabPlan();
    return;
  }

  const record = historyRecordsCache.find((r) => r.id === recordId);
  if (!record) return;

  if (infoCard) {
    infoCard.style.display = "flex";
    document.getElementById("rehabPatientName").textContent = `Patient: ${record.patient_name} (#${record.id})`;
    document.getElementById("rehabPatientMeta").textContent = `${record.prediction_date.substring(0, 10)} • ${record.bone_type} • Confidence: ${record.confidence}%`;

    const predPill = document.getElementById("rehabPatientPredictionPill");
    predPill.textContent = record.prediction;
    predPill.className = `table-pill ${record.prediction === "Fractured" ? "fractured" : "normal"}`;

    const sevBadge = document.getElementById("rehabPatientSeverityBadge");
    sevBadge.textContent = record.severity;
    sevBadge.className = `severity-badge ${record.severity.toLowerCase().replace('/', '')}`;

    gsap.from(infoCard, { opacity: 0, y: -10, duration: 0.3, ease: "power2.out" });
  }

  fetchRehabPlanForParams(record.prediction, record.severity, record.confidence);
};

window.generateCustomRehabPlan = function () {
  const infoCard = document.getElementById("patientRehabInfoCard");
  if (infoCard) infoCard.style.display = "none";

  const select = document.getElementById("rehabSelectSeverity");
  const selectedVal = select ? select.value : "Moderate";

  let prediction = "Fractured";
  let severity = selectedVal;

  if (selectedVal === "Normal") {
    prediction = "Not Fractured";
    severity = "N/A";
  }

  fetchRehabPlanForParams(prediction, severity, 95.0);
};

async function fetchRehabPlanForParams(prediction, severity, confidence) {
  try {
    const response = await fetch("/api/rehab-recommendation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prediction, severity, confidence }),
    });

    const data = await response.json();
    if (data.status !== "success") return;

    const plan = data.plan;

    const summaryEl = document.getElementById("rehabSummary");
    if (summaryEl) summaryEl.innerHTML = `<p>${plan.summary}</p>`;

    const accordion = document.getElementById("rehabAccordion");
    if (!accordion) return;

    accordion.innerHTML = "";

    if (plan.exercises && plan.exercises.length) {
      accordion.innerHTML += buildAccordionSection("💪 Recommended Exercises", plan.exercises.map(
        (ex) => `<div class="rehab-item"><h5>${ex.name}</h5><p>${ex.description}</p><span class="rehab-duration">${ex.duration}</span></div>`
      ).join(""));
    }

    if (plan.recovery_stages && plan.recovery_stages.length) {
      accordion.innerHTML += buildAccordionSection("📅 Recovery Stages Timeline", `<div class="timeline">${plan.recovery_stages.map(
        (stage) => `<div class="timeline-item"><div class="timeline-marker"></div><div class="timeline-content"><h5>${stage.stage}</h5><span class="timeline-period">${stage.timeline}</span><p>${stage.description}</p><ul>${stage.activities.map((a) => `<li>${a}</li>`).join("")}</ul></div></div>`
      ).join("")}</div>`);
    }

    if (plan.physiotherapy) {
      accordion.innerHTML += buildAccordionSection("🏥 Physiotherapy Guidance", `<p>${plan.physiotherapy}</p>`);
    }

    if (plan.precautions && plan.precautions.length) {
      accordion.innerHTML += buildAccordionSection("⚠️ Precautions (Do's & Don'ts)", plan.precautions.map(
        (p) => `<div class="precaution-item ${p.type}"><span class="precaution-icon">${p.type === "do" ? "✅" : "❌"}</span><p>${p.text}</p></div>`
      ).join(""));
    }

    if (plan.followup_schedule && plan.followup_schedule.length) {
      accordion.innerHTML += buildAccordionSection("📋 Follow-up Schedule", `<table class="followup-table"><tbody>${plan.followup_schedule.map(
        (f) => `<tr><td class="followup-week">${f.week}</td><td>${f.action}</td></tr>`
      ).join("")}</tbody></table>`);
    }

    gsap.from("#tabContentRehab .accordion-section", { y: 20, opacity: 0, duration: 0.3, stagger: 0.08, ease: "power2.out" });
  } catch (error) {
    console.error("Custom rehab error:", error);
  }
}

function buildAccordionSection(title, content) {
  return `
    <div class="accordion-section">
      <button class="accordion-header" onclick="toggleAccordion(this)">
        <span>${title}</span>
        <svg class="accordion-arrow" xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
        </svg>
      </button>
      <div class="accordion-body">${content}</div>
    </div>
  `;
}

// ========================================================================
// GLOBAL TAB SWITCHING & ACCORDION FUNCTIONS
// ========================================================================
window.switchTab = function (tabId, event) {
  if (event && event.preventDefault) {
    event.preventDefault();
  }
  const tabNames = {
    dashboard: "tabContentDashboard",
    analysis: "tabContentAnalysis",
    analytics: "tabContentAnalytics",
    rehab: "tabContentRehab",
    doctors: "tabContentDoctors",
  };

  const targetContentId = tabNames[tabId];
  if (!targetContentId) return;

  document.querySelectorAll(".sidebar .nav-item").forEach((el) => el.classList.remove("active"));
  const navMap = {
    dashboard: "navDashboard",
    analysis: "navAnalysis",
    analytics: "navAnalytics",
    rehab: "navRehab",
    doctors: "navDoctors",
  };
  const targetNav = document.getElementById(navMap[tabId]);
  if (targetNav) targetNav.classList.add("active");

  document.querySelectorAll(".tab-pill").forEach((el) => el.classList.remove("active"));
  const pillMap = {
    dashboard: "tabPillDashboard",
    analysis: "tabPillAnalysis",
    analytics: "tabPillAnalytics",
    rehab: "tabPillRehab",
    doctors: "tabPillDoctors",
  };
  const targetPill = document.getElementById(pillMap[tabId]);
  if (targetPill) targetPill.classList.add("active");

  const subtitles = {
    dashboard: "Welcome to your AI Diagnostic Suite",
    analysis: "Upload X-ray images for immediate fracture detection",
    analytics: "Real-time trends, classification metrics, & AI accuracy",
    rehab: "Select a patient from history or preset condition to view recovery guidance",
    doctors: "Verified real orthopedic hospitals & specialists with Google Maps navigation",
  };
  const subtitleEl = document.getElementById("topBarSubtitle");
  if (subtitleEl) subtitleEl.textContent = subtitles[tabId] || "";

  document.querySelectorAll(".tab-content").forEach((el) => {
    el.classList.remove("active");
  });
  const targetContent = document.getElementById(targetContentId);
  if (targetContent) {
    targetContent.classList.add("active");
    gsap.fromTo(targetContent, { opacity: 0, y: 15 }, { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" });
  }

  const splineBg = document.querySelector(".dashboard-spline-bg");
  if (splineBg) {
    splineBg.style.display = tabId === "dashboard" ? "block" : "none";
  }

  if (tabId === "analytics") {
    loadDashboardStats();
    loadCharts();
  }

  if (tabId === "rehab") {
    loadRehabPatientHistory();
  }

  if (tabId === "doctors") {
    loadDedicatedNearbyDoctors();
  }

  if (tabId === "analytics") {
    setTimeout(() => {
      if (weeklyChartInstance) weeklyChartInstance.resize();
      if (monthlyChartInstance) monthlyChartInstance.resize();
    }, 100);
  }
};

window.toggleAccordion = function (header) {
  const section = header.parentElement;
  const body = section.querySelector(".accordion-body");
  const arrow = section.querySelector(".accordion-arrow");
  const isOpen = section.classList.contains("open");

  if (isOpen) {
    gsap.to(body, { height: 0, opacity: 0, duration: 0.3, ease: "power2.inOut", onComplete: () => { body.style.display = "none"; } });
    gsap.to(arrow, { rotation: 0, duration: 0.3 });
    section.classList.remove("open");
  } else {
    body.style.display = "block";
    const fullHeight = body.scrollHeight;
    gsap.fromTo(body, { height: 0, opacity: 0 }, { height: fullHeight, opacity: 1, duration: 0.3, ease: "power2.inOut" });
    gsap.to(arrow, { rotation: 180, duration: 0.3 });
    section.classList.add("open");
  }
};

window.predictHealingTime = async function () {
  const age = document.getElementById("healingAge").value;
  const fracture_type = document.getElementById("healingFractureType").value;
  const bone = document.getElementById("healingBone").value;
  const smoking = document.getElementById("healingSmoking").checked;
  const diabetes = document.getElementById("healingDiabetes").checked;
  const severity = document.getElementById("healingSeverity").value;

  if (!age || age < 1) {
    alert("Please enter a valid age.");
    return;
  }

  try {
    const response = await fetch("/api/healing-prediction", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ age: parseInt(age), fracture_type, bone, smoking, diabetes, severity }),
    });

    const data = await response.json();

    if (data.status === "success") {
      const resultCard = document.getElementById("healingResultCard");
      resultCard.style.display = "block";

      document.getElementById("healingWeeksText").textContent = data.range_text;
      document.getElementById("healingConfidenceValue").textContent = `${data.confidence}%`;

      const ring = document.getElementById("healingConfidenceRing");
      const circumference = 2 * Math.PI * 34;
      ring.style.strokeDasharray = circumference;
      const offset = circumference - (circumference * data.confidence) / 100;
      ring.style.strokeDashoffset = offset;
      ring.style.stroke = "#2563EB";

      const confText = document.getElementById("healingConfidenceText");
      let current = 0;
      const target = data.confidence;
      const timer = setInterval(() => {
        current += target / 40;
        if (current >= target) {
          current = target;
          clearInterval(timer);
        }
        confText.textContent = `${current.toFixed(0)}%`;
      }, 25);

      gsap.from(resultCard, { scale: 0.9, opacity: 0, duration: 0.5, ease: "back.out(1.7)" });
    } else {
      alert(data.message || "Healing prediction failed.");
    }
  } catch (error) {
    console.error("Healing prediction error:", error);
    alert("Failed to predict healing time.");
  }
};
