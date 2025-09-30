import pygame
from pygame.locals import *
from sys import exit
import os 
import cv2
import mediapipe as mp
import math 
import sys 

pygame.init()
pygame.mixer.init()

diretorio_atual = os.path.dirname(__file__)
diretorio_raiz_projeto = os.path.dirname(os.path.dirname(diretorio_atual))
diretorio_trilha = os.path.join(diretorio_raiz_projeto, 'audios', 'trilha')
caminho_musica = os.path.join(diretorio_trilha, 'trilhavoidtail.mp3')
diretorio_sprites = os.path.join(diretorio_raiz_projeto, 'frontend', 'sprites')
diretorio_fundo = os.path.join(diretorio_sprites, 'fundo')
diretorio_gatinho = os.path.join(diretorio_sprites, 'gatinho')

largura = 1180
altura = 680
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Void Tail :P')
relogio = pygame.time.Clock()

caminho_fundo = os.path.join(diretorio_fundo, 'background.png')
fundo = pygame.image.load(caminho_fundo).convert()
fundo = pygame.transform.scale(fundo, (largura, altura))

class GatoAnimado(pygame.sprite.Sprite):
    def __init__(self, largura_tela, altura_tela):
        super().__init__()
        self.sprites = []
        escala = 4
        caminho_gato = os.path.join(diretorio_gatinho, 'caminho_gato2.png')
        sprite_sheet_gato = pygame.image.load(caminho_gato).convert_alpha()
        largura_frame_gato = 64
        altura_frame_gato = 64
        num_frames_gato = sprite_sheet_gato.get_width() // largura_frame_gato
        for i in range(num_frames_gato):
            frame = sprite_sheet_gato.subsurface((i * largura_frame_gato, 0, largura_frame_gato, altura_frame_gato))
            frame = pygame.transform.scale(frame, (largura_frame_gato * escala, altura_frame_gato * escala))
            self.sprites.append(frame)

        caminho_ataque = os.path.join(diretorio_gatinho, 'Ataque_01-Sheet.png')
        sprite_sheet_ataque = pygame.image.load(caminho_ataque).convert_alpha()
        largura_frame_ataque = 64
        altura_frame_ataque = 64
        num_frames_ataque = sprite_sheet_ataque.get_width() // largura_frame_ataque
        for i in range(num_frames_ataque):
            frame = sprite_sheet_ataque.subsurface((i * largura_frame_ataque, 0, largura_frame_ataque, altura_frame_ataque))
            frame = pygame.transform.scale(frame, (largura_frame_ataque * escala, altura_frame_ataque * escala))
            self.sprites.append(frame)

        caminho_escudo = os.path.join(diretorio_gatinho, 'caminho_escudo2.png')
        sprite_sheet_escudo = pygame.image.load(caminho_escudo).convert_alpha()
        largura_frame_escudo = 64
        altura_frame_escudo = 64
        num_frames_escudo = 5
        for i in range(num_frames_escudo):
            frame = sprite_sheet_escudo.subsurface((i * largura_frame_escudo, 0, largura_frame_escudo, altura_frame_escudo))
            frame = pygame.transform.scale(frame, (largura_frame_escudo * escala, altura_frame_escudo * escala))
            self.sprites.append(frame)

        self.frame_atual = 0
        self.image = self.sprites[self.frame_atual]
        self.rect = self.image.get_rect(midbottom=(largura_tela // 2, altura_tela - 100))

    def atualizar_animacao(self):
        self.frame_atual = (self.frame_atual + 1) % len(self.sprites)
        self.image = self.sprites[self.frame_atual]
    
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

if os.path.exists(caminho_musica):
    pygame.mixer.music.load(caminho_musica)
    pygame.mixer.music.set_volume(0.8)
    pygame.mixer.music.play(-1) 
else:
    print('ERRO: O arquivo de música "trilhavoidtail.mp3" não foi encontrado.')
    print(f"Caminho esperado: {caminho_musica}")

gato = GatoAnimado(largura, altura)
todos_sprites = pygame.sprite.Group()
todos_sprites.add(gato)

rodando = True
while rodando:
    relogio.tick(60)
    ret, frame = cap.read()
    
    if ret:
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

            braço_esquerdo_levantado = pulso_esquerdo.y < ombro_esquerdo.y
            braço_direito_levantado = pulso_direito.y < ombro_direito.y
            ambos_braços_levantados = braço_esquerdo_levantado and braço_direito_levantado

            if braço_esquerdo_levantado:
                print("Braço esquerdo levantado! Ativar ataque do lado esquerdo.")

            elif braço_direito_levantado:
                print("Braço direito levantado! Ativar ataque do lado direito.")

            elif ambos_braços_levantados:
                print("Ambos os braços levantados! Ativar escudo!")
            
            else:
                print("Nenhum braço levantado. Animação de repouso.")
        
        frame_rgb_pygame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pygame_frame = pygame.surfarray.make_surface(frame_rgb_pygame)
        pygame_frame = pygame.transform.rotate(pygame_frame, -90)
        pygame_frame = pygame.transform.flip(pygame_frame, True, False)
        largura_camera = int(largura * 0.2)
        altura_camera = int(altura * 0.2)
        pygame_frame = pygame.transform.scale(pygame_frame, (largura_camera, altura_camera))
        
        tela.blit(fundo, (0, 0)) 
        tela.blit(pygame_frame, (10, 10)) 
        todos_sprites.draw(tela)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    pygame.display.flip()

cap.release()
cv2.destroyAllWindows() 
pygame.quit()
sys.exit()