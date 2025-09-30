import pygame
from pygame.locals import *
from sys import exit
import os 
import cv2
import mediapipe as mp
import math 

pygame.init()
pygame.mixer.init()

diretorio_principal = os.path.dirname(__file__)
largura = 1180
altura = 680
tela_cor = (0, 0, 0)

tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('VOID TAIL')

relogio = pygame.time.Clock()

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

diretorio_atual = os.path.dirname(__file__)


diretorio_raix_projeto = os.path.dirname(os.path.dirname(diretorio_atual))

diretorio_trilha = os.path.join(diretorio_raix_projeto, 'audios', 'trilha')



caminho_musica = os.path.join(diretorio_trilha, 'trilhavoidtail.mp3')


if os.path.exists(caminho_musica):
    pygame.mixer.music.load(caminho_musica)
    pygame.mixer.music.set_volume(0.8)
    pygame.mixer.music.play(-1) 

else:
    print ('deu erroo :P')

while True:
    relogio.tick(60)

    ret, frame = cap.read()
    if not ret:
        continue
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS)
        
       
        ombro_esquerdo = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        pulso_esquerdo = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
        ombro_direito = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        pulso_direito = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
        
       
        pulso_esquerdo_pixel = (int(pulso_esquerdo.x * largura), int(pulso_esquerdo.y * altura))

        
        pulso_direito_pixel = (int(pulso_direito.x * largura), int(pulso_direito.y * altura))
        

        if pulso_esquerdo.y < ombro_esquerdo.y:
            print("Braço esquerdo levantado!")
     
        if pulso_direito.y < ombro_direito.y:
            print("Braço direito levantado!")
          

    frame_rgb_pygame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    pygame_frame = pygame.surfarray.make_surface(frame_rgb_pygame)
    pygame_frame = pygame.transform.rotate(pygame_frame, -90)
    pygame_frame = pygame.transform.flip(pygame_frame, True, False)
    
    largura_camera = int(largura * 0.9) 
    altura_camera = int(altura * 0.9)
    pygame_frame = pygame.transform.scale(pygame_frame, (largura_camera, altura_camera))
 
    tela.fill(tela_cor)

    tela.blit(pygame_frame, (int((largura - largura_camera) / 50), int((altura - altura_camera) / 90)))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            cv2.destroyAllWindows() 
            pygame.quit()
            exit()
    
    pygame.display.flip()