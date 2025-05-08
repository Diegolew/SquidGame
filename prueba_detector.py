import cv2
import numpy as np
import mediapipe as mp
from collections import defaultdict, deque

# Configuración de MediaPipe
mp_pose = mp.solutions.pose
mp_selfie_segmentation = mp.solutions.selfie_segmentation
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
segmentacion = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
mp_drawing = mp.solutions.drawing_utils

# Inicialización
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: No se pudo abrir la cámara")
    exit()

estado_luz = "verde"
MAX_JUGADORES = 3
jugadores_activos = {}
historico_posiciones = defaultdict(deque)
jugadores_penalizados = set()

# Parámetros
UMBRAL_MOVIMIENTO = 0.01
MAX_HISTORICO = 5
COLOR_ACTIVO = (245, 117, 66)
COLOR_PENALIZADO = (0, 0, 255)

def calcular_distancia(p1, p2):
    return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def calcular_centroide(landmarks):
    puntos_clave = [
        mp_pose.PoseLandmark.NOSE,
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.RIGHT_SHOULDER,
        mp_pose.PoseLandmark.LEFT_HIP,
        mp_pose.PoseLandmark.RIGHT_HIP
    ]
    x = np.mean([landmarks.landmark[p].x for p in puntos_clave])
    y = np.mean([landmarks.landmark[p].y for p in puntos_clave])
    return x, y

def distancia_centroide(c1, c2):
    return np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)

def calcular_centroide(landmarks):
    puntos_clave = [
        mp_pose.PoseLandmark.NOSE,
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.RIGHT_SHOULDER,
        mp_pose.PoseLandmark.LEFT_HIP,
        mp_pose.PoseLandmark.RIGHT_HIP
    ]
    x = np.mean([landmarks.landmark[p].x for p in puntos_clave])
    y = np.mean([landmarks.landmark[p].y for p in puntos_clave])
    return x, y

def distancia_centroide(c1, c2):
    return np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)

def actualizar_jugadores(landmarks_detectados):
    jugadores_temporales = {}
    landmarks_por_asignar = landmarks_detectados.copy()
    
    # Calcular centroides de actuales
    centroides_actuales = {jugador_id: calcular_centroide(landmarks) for jugador_id, landmarks in jugadores_activos.items()}
    
    for jugador_id in range(1, MAX_JUGADORES + 1):
        mejor_landmark = None
        mejor_dist = float('inf')
        mejor_idx = -1
        
        if jugador_id in centroides_actuales:
            centroide_existente = centroides_actuales[jugador_id]
            
            for idx, landmarks in enumerate(landmarks_por_asignar):
                centroide = calcular_centroide(landmarks)
                dist = distancia_centroide(centroide_existente, centroide)
                
                if dist < mejor_dist:
                    mejor_dist = dist
                    mejor_landmark = landmarks
                    mejor_idx = idx
        
        if mejor_landmark is not None and mejor_dist < 0.2:  # un poco más tolerante
            jugadores_temporales[jugador_id] = mejor_landmark
            if mejor_idx != -1 and mejor_idx < len(landmarks_por_asignar):
                landmarks_por_asignar.pop(mejor_idx)

    # Asignar nuevos jugadores
    for landmarks in landmarks_por_asignar:
        for jugador_id in range(1, MAX_JUGADORES + 1):
            if jugador_id not in jugadores_temporales:
                jugadores_temporales[jugador_id] = landmarks
                break
    
    jugadores_activos.clear()
    jugadores_activos.update({k: v for k, v in jugadores_temporales.items() if k <= MAX_JUGADORES})

    ids_actuales = set(jugadores_activos.keys())
    ids_para_borrar = set(historico_posiciones.keys()) - ids_actuales
    for id_ in ids_para_borrar:
        historico_posiciones.pop(id_, None)

# Crear la ventana una sola vez antes del bucle
cv2.namedWindow("Luz Verde / Luz Roja - Máximo 3 Jugadores", cv2.WINDOW_NORMAL)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo capturar el frame")
            break

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            estado_luz = "rojo" if estado_luz == "verde" else "verde"
            if estado_luz == "verde":
                jugadores_penalizados.clear()
        elif key == ord('q'):
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultado_segmentacion = segmentacion.process(frame_rgb)
        mask = resultado_segmentacion.segmentation_mask > 0.3
        mask = mask.astype(np.uint8) * 255

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        jugadores_en_frame = []

        for contour in contours:
            if cv2.contourArea(contour) > 1000:
                x, y, w, h = cv2.boundingRect(contour)
                persona_crop = frame_rgb[y:y+h, x:x+w]
                resultado_pose = pose.process(persona_crop)

                if resultado_pose.pose_landmarks:
                    for lm in resultado_pose.pose_landmarks.landmark:
                        lm.x = (lm.x * w + x) / frame.shape[1]
                        lm.y = (lm.y * h + y) / frame.shape[0]
                    jugadores_en_frame.append(resultado_pose.pose_landmarks)

        barra_estado = np.zeros((80, frame.shape[1], 3), dtype=np.uint8)
        color_barra = (0, 255, 0) if estado_luz == "verde" else (0, 0, 255)
        barra_estado[:] = color_barra
        cv2.putText(barra_estado, f"LUZ: {estado_luz.upper()} | Jugadores: {len(jugadores_activos)}/{MAX_JUGADORES}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        if jugadores_en_frame:
            actualizar_jugadores(jugadores_en_frame)

        for jugador_id, landmarks in jugadores_activos.items():
            if jugador_id > MAX_JUGADORES:
                continue
                
            color = COLOR_PENALIZADO if jugador_id in jugadores_penalizados else COLOR_ACTIVO
            
            mp_drawing.draw_landmarks(
                frame, landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=color, thickness=2),
                mp_drawing.DrawingSpec(color=color, thickness=2))
            
            nariz = landmarks.landmark[mp_pose.PoseLandmark.NOSE]
            x, y = int(nariz.x * frame.shape[1]), int(nariz.y * frame.shape[0])
            cv2.putText(frame, f"Jugador {jugador_id}", (x, y - 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

            if estado_luz == "rojo":
                if jugador_id not in historico_posiciones:
                    historico_posiciones[jugador_id] = deque(maxlen=MAX_HISTORICO)
                
                historico_posiciones[jugador_id].append(nariz)
                
                if len(historico_posiciones[jugador_id]) == MAX_HISTORICO:
                    distancia = calcular_distancia(
                        historico_posiciones[jugador_id][-1],
                        historico_posiciones[jugador_id][0]
                    )
                    if distancia > UMBRAL_MOVIMIENTO:
                        jugadores_penalizados.add(jugador_id)
                        cv2.putText(frame, "PENALIZADO!", (x, y + 40),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        if jugadores_penalizados:
            cv2.putText(barra_estado, f"Penalizados: {', '.join(map(str, jugadores_penalizados))}", 
                        (frame.shape[1] - 300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        pantalla_completa = np.vstack((barra_estado, frame))
        cv2.imshow("Luz Verde / Luz Roja - Máximo 3 Jugadores", pantalla_completa)

finally:
    cap.release()
    cv2.destroyAllWindows()