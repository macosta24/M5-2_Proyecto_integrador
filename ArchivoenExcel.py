import cv2

import mediapipe as mp

import numpy as np

import requests

import mysql.connector

import time


# Función para obtener IP pública

def obtener_ip_publica():

    try:

        respuesta = requests.get('https://api.ipify.org?format=json')

        respuesta.raise_for_status()  # Lanza un error si la solicitud no fue exitosa

        ip_publica = respuesta.json()['ip']

        return ip_publica

    except requests.RequestException as e:

        return f"Error al obtener la IP pública: {e}"



# Función para insertar datos en MySQL

def insertar_datos(ip_privada, ip_publica, nombre_usuario):

    conexion = mysql.connector.connect(

        host='195.179.238.58',  # Cambia por la dirección de tu servidor MySQL

        database='u927419088_testing_sql',  # Cambia por el nombre de tu base de datos

        user='u927419088_admin',  # Cambia por tu usuario de MySQL

        password='#Admin12345#'  # Cambia por tu contraseña de MySQL

    )
# privada 164.36.41.190
    ip_privada = '164.36.41.190'
    cursor = conexion.cursor()


    query = "INSERT INTO datos_usuario (ip_privada, ip_publica, nombre_usuario) VALUES (%s, %s, %s)"

    valores = (ip_privada, ip_publica, nombre_usuario)


    cursor.execute(query, valores)

    conexion.commit()

    cursor.close()

    conexion.close()



# Inicializar Mediapipe FaceMesh

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)


mp_drawing = mp.solutions.drawing_utils

drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)


cap = cv2.VideoCapture(0)


def calcular_distancia(punto1, punto2):

    return np.linalg.norm(np.array(punto1) - np.array(punto2))


# Obtiene la IP pública

ip_publica = obtener_ip_publica()


# Nombre del usuario

nombre_usuario = "Miguel A"


boca_abierta = False

inicio_boca_abierta = 0

umbral_duracion = 2  # Segundos que la boca debe estar abierta para enviar datos


while cap.isOpened():

    success, frame = cap.read()

    if not success:

        print("No se puede acceder a la cámara")

        break


    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    image.flags.writeable = False


    results = face_mesh.process(image)


    image.flags.writeable = True

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


    if results.multi_face_landmarks:

        for face_landmarks in results.multi_face_landmarks:

            mp_drawing.draw_landmarks(

                image=image,

                landmark_list=face_landmarks,

                connections=mp_face_mesh.FACEMESH_TESSELATION,

                landmark_drawing_spec=drawing_spec,

                connection_drawing_spec=drawing_spec)


            labio_superior = face_landmarks.landmark[13]

            labio_inferior = face_landmarks.landmark[14]


            altura, ancho, _ = image.shape

            labio_superior = (int(labio_superior.x * ancho), int(labio_superior.y * altura))

            labio_inferior = (int(labio_inferior.x * ancho), int(labio_inferior.y * altura))


            distancia_boca = calcular_distancia(labio_superior, labio_inferior)


            umbral_boca_abierta = 20


            if distancia_boca > umbral_boca_abierta:

                if not boca_abierta:

                    boca_abierta = True

                    inicio_boca_abierta = time.time()

                elif time.time() - inicio_boca_abierta > umbral_duracion:

                    cv2.putText(image, '¡Boca Abierta!', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,

                                cv2.LINE_AA)


                    # Enviar datos a la base de datos

                    insertar_datos(ip_publica, nombre_usuario)

                    print("Se guardó el registro en la base de datos...")

                    inicio_boca_abierta = time.time()  # Reiniciar el temporizador para enviar nuevamente si se mantiene abierta

            else:

                boca_abierta = False  # Resetear si la boca se cierra


    cv2.imshow('Reconocimiento de Gestos Faciales', image)


    if cv2.waitKey(5) & 0xFF == ord('q'):

        break


cap.release()

cv2.destroyAllWindows()