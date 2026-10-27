const targetPositions = [
  "top_left",
  "top_center",
  "top_right",
  "center_left",
  "center",
  "center_right",
  "bottom_left",
  "bottom_center",
  "bottom_right"
];

// Ensure DOM elements exist for target dot
let targetDot = null;
function createTargetElement() {
  if (!targetDot) {
    targetDot = document.createElement("div");
    targetDot.className = "target-dot";
    document.getElementById("target-layer").appendChild(targetDot);
  }
}

// Hide target
function hideTarget() {
  if (targetDot) {
    targetDot.style.display = "none";
  }
}

// Show target according to target_index from status
function showTarget(status) {
   if (!status || !status.calib_started || status.calib_completed) {
    hideTarget();
    return;
  }

  const idx = status.target_index;

  if (idx == null || idx < 0 || idx >= targetPositions.length) {
    hideTarget();
    return;
  }

  const positionName = targetPositions[idx];

  createTargetElement();

  const container = document.getElementById("calib-zone");
  const rect = container.getBoundingClientRect();

  // Corner targets (further inset from edges)
  const cornerMarginX = rect.width * 0.015;
  const cornerMarginY = rect.height * 0.03;

  // Edge/center targets (smaller inset)
  const edgeMarginX = rect.width * 0.015;
  const edgeMarginY = rect.height * 0.03;

  let cx, cy;
  switch (positionName) {
    case "top_left":      cx = cornerMarginX;               cy = cornerMarginY;                 break;
    case "top_center":    cx = rect.width/2;                cy = edgeMarginY;                   break;
    case "top_right":     cx = rect.width - cornerMarginX;  cy = cornerMarginY;                 break;
    case "center_left":   cx = edgeMarginX;                 cy = rect.height/2;                 break;
    case "center":        cx = rect.width/2;                cy = rect.height/2;                 break;
    case "center_right":  cx = rect.width - edgeMarginX;    cy = rect.height/2;                 break;
    case "bottom_left":   cx = cornerMarginX;               cy = rect.height - cornerMarginY;   break;
    case "bottom_center": cx = rect.width/2;                cy = rect.height - edgeMarginY;     break;
    case "bottom_right":  cx = rect.width - cornerMarginX;  cy = rect.height - cornerMarginY;   break;
  }

  targetDot.style.display = "block";
  targetDot.style.left = `${cx}px`;
  targetDot.style.top  = `${cy}px`;
}