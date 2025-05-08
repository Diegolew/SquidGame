import cv2
import numpy as np
from typing import Tuple, List

class DetectorMovimiento:
    def __init__(self, umbral_movimiento: float = 30.0, area_minima: int = 500):
        """
        :param umbral_movimiento: Sensibilidad para detectar cambios (píxeles).
        :param area_minima: Área mínima (en píxeles) para considerar como movimiento válido.
        """
        self.umbral = umbral_movimiento
        self.area_minima = area_minima
        self.fondo = None
        self.estado_luz = "verde"  # Estado inicial: luz verde (movimiento permitido)

    def actualizar_estado_luz(self, estado: str):
        """Actualiza el estado de la luz (verde/rojo)."""
        self.estado_luz = estado.lower()

    def detectar_movimiento(self, frame: np.ndarray) -> Tuple[bool, np.ndarray]:
        """
        Detecta movimiento en el frame actual (solo si la luz está en rojo).
        
        :return: (True si hay movimiento, frame con contornos dibujados)
        """
        if self.estado_luz != "rojo":
            return False, frame  # No penalizar si la luz es verde

        # Preprocesamiento
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gris = cv2.GaussianBlur(gris, (21, 21), 0)

        # Inicializar fondo si es la primera vez
        if self.fondo is None:
            self.fondo = gris
            return False, frame

        # Resta entre el fondo y el frame actual
        resta = cv2.absdiff(self.fondo, gris)
        _, thresh = cv2.threshold(resta, 25, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Encontrar contornos
        contornos, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        movimiento_detectado = False
        for contorno in contornos:
            if cv2.contourArea(contorno) < self.area_minima:
                continue

            # Dibujar rectángulo alrededor del movimiento
            (x, y, w, h) = cv2.boundingRect(contorno)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            movimiento_detectado = True

        # Actualizar fondo para el próximo frame (solo si no hay movimiento)
        if not movimiento_detectado:
            self.fondo = gris

        return movimiento_detectado, frame
    

















######################################





