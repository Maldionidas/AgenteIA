###SIN BOMBAS 
import pygame, random
pygame.init()

#### --- Constantes cortas ---
T=50; R,C=11,13
W,H=C*T, R*T
SCR=pygame.display.set_mode((W,H))
pygame.display.set_caption("Rompe directo (mini)")
CLK=pygame.time.Clock()

#### colores
VAC=(200,200,200); 
MUR=(60,60,60); 
DES=(160,100,40)
PLY=(50,100,255); 
GRD=(100,100,100); OUT=(60,200,120)

#### celdas
E=0; 
X=1; 
B=2; 
S=3    # vacía, muro, rompible, salida

def mapa_nuevo():
    m=[[E]*C for _ in range(R)]
    for f in range(R):
        for c in range(C):
            if f in (0,R-1) or c in (0,C-1) or (f%2==0 and c%2==0):
                m[f][c]=X
            else:
                m[f][c]=B if random.random()<0.30 else E
    m[1][1]=m[1][2]=m[2][1]=E
    return m

def elegir_salida(m):
    proh={(1,1),(1,2),(2,1)}
    ops=[(f,c) for f in range(1,R-1) for c in range(1,C-1) if m[f][c]==B and (f,c) not in proh]
    if ops: return random.choice(ops)
    vac=[(f,c) for f in range(1,R-1) for c in range(1,C-1) if m[f][c]==E]
    return random.choice(vac) if vac else (1,3)

def dibujar(m,px,py,win,tw):
    SCR.fill((0,0,0))
    for f in range(R):
        for c in range(C):
            v=m[f][c]; col=VAC if v==E else MUR if v==X else DES if v==B else OUT
            pygame.draw.rect(SCR,col,(c*T,f*T,T,T)); pygame.draw.rect(SCR,GRD,(c*T,f*T,T,T),1)
    pygame.draw.circle(SCR,PLY,(px,py),T//2-6)
    if win:
        o=pygame.Surface((W,H),pygame.SRCALPHA); o.fill((60,200,120,80)); SCR.blit(o,(0,0))
        if pygame.time.get_ticks()-tw>1200: return True
    pygame.display.flip()
    return False

def colision(rect,m):
    for (px,py) in [(rect.left,rect.top),(rect.right-1,rect.top),(rect.left,rect.bottom-1),(rect.right-1,rect.bottom-1)]:
        if m[py//T][px//T] in (X,B): return True
    return False

def juego():
    m=mapa_nuevo()
    exf,exc=elegir_salida(m); salida_revelada=False
    px,py=T+T//2,T+T//2; dx,dy=1,0; vel=3
    last=0; win=False; twin=0
    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: return
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_r: return juego()
                if e.key in (pygame.K_SPACE,pygame.K_e,pygame.K_f):
                    now=pygame.time.get_ticks()
                    if now-last>140:
                        last=now
                        f,c=py//T,px//T
                        tf,tc=f+dy,c+dx
                        if 0<=tf<R and 0<=tc<C and m[tf][tc]==B:
                            if (tf,tc)==(exf,exc) and not salida_revelada:
                                m[tf][tc]=S; salida_revelada=True
                            else:
                                m[tf][tc]=E

        k=pygame.key.get_pressed()
        ddx=ddy=0
        if k[pygame.K_w] or k[pygame.K_UP]: ddy=-vel; dx,dy=0,-1
        if k[pygame.K_s] or k[pygame.K_DOWN]: ddy=vel; dx,dy=0,1
        if k[pygame.K_a] or k[pygame.K_LEFT]: ddx=-vel; dx,dy=-1,0
        if k[pygame.K_d] or k[pygame.K_RIGHT]: ddx=vel; dx,dy=1,0

        r=pygame.Rect(px-(T-5)//2, py-(T-5)//2, T-5, T-5).move(ddx,ddy)
        if not colision(r,m): px+=ddx; py+=ddy

        # ¿ganó?
        if not win and m[py//T][px//T]==S: win=True; twin=pygame.time.get_ticks()

        if dibujar(m,px,py,win,twin): return juego()
        CLK.tick(60)

if __name__=="__main__": juego(); pygame.quit()

