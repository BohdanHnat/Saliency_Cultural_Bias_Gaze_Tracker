from app.scripts.settings import LEFT_IRIS, RIGHT_IRIS, TARGET_POSITIONS, CALIB_FRAMES
from app.scripts.calculations import get_iris_center, normalize_iris
import numpy as np
import cv2

def calibrate_frame(frame, face_mesh, calib_started, target_index, current_target_frame, session_id, gaze_store):
    # Set up or fetch calibration state for the session
    if session_id in gaze_store and 'gaze_values' in gaze_store[session_id]:
        gaze_values = gaze_store[session_id]['gaze_values']
    else:
        gaze_values = {pos.lower(): [] for pos in TARGET_POSITIONS}
        if session_id not in gaze_store:
            gaze_store[session_id] = {}
        gaze_store[session_id]['gaze_values'] = gaze_values

    current_frame = current_target_frame

    status = {"calib_started": calib_started, "calib_completed": False, "target_index": target_index}

    if not calib_started:
        # Message flag for frontend display
        status["message"] = "Press 'Start' to begin calibration"
    else:
        idx = target_index
        if idx < len(TARGET_POSITIONS):
            pos = TARGET_POSITIONS[idx]

            # Target info and progress count for frontend
            status["message"] = f"Target {idx + 1} Frames Captured: {current_frame + 1}/{CALIB_FRAMES}"

            # Run landmark detection and collect gaze point
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                h, w, _ = frame.shape

                # Left and Right eye calculations
                left_iris = get_iris_center(landmarks, LEFT_IRIS, w, h)
                left_inner = [landmarks[133].x * w, landmarks[133].y * h]
                left_outer = [landmarks[33].x * w, landmarks[33].y * h]
                norm_left = normalize_iris(left_iris, left_inner, left_outer)

                right_iris = get_iris_center(landmarks, RIGHT_IRIS, w, h)
                right_inner = [landmarks[263].x * w, landmarks[263].y * h]
                right_outer = [landmarks[362].x * w, landmarks[362].y * h]
                norm_right = normalize_iris(right_iris, right_inner, right_outer)

                norm_iris = [
                    (norm_left[0] + norm_right[0]) / 2,
                    (norm_left[1] + norm_right[1]) / 2
                ]

                if current_frame < CALIB_FRAMES:
                    gaze_values[pos.lower()].append(norm_iris)
                    gaze_store[session_id]['gaze_values'] = gaze_values
                    current_frame += 1
        else:
            # Mark calibration as completed for frontend
            status["calib_completed"] = True
            status["message"] = "Calibration complete!"

            calibration_results = {}
            for pos in TARGET_POSITIONS:
                values = gaze_values[pos.lower()]
                if len(values) > 0:
                    mean = np.mean(values, axis=0)
                else:
                    mean = (0.0, 0.0)
                calibration_results[pos.lower()] = (mean[0], mean[1])

            all_means = np.array(list(calibration_results.values()))
            mean_x = np.mean(all_means[:, 0])
            mean_y = np.mean(all_means[:, 1])

            # Center all means around (0,0)
            for key in calibration_results:
                x, y = calibration_results[key]
                calibration_results[key] = (x - mean_x, y - mean_y)

            gaze_store[session_id].update({
                'calib_results': calibration_results,
                'mean_center': (mean_x, mean_y),
                'raw_values': gaze_values
            })

    # Status: {message, current_target, calib_completed}
    return status, current_frame
