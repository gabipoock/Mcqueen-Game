from tkinter import Tk, Label, Entry, Button, PhotoImage, messagebox, END, Canvas
from threading import Timer
from data import field
import os, pygame


class MainEngine(object):

    def __init__(self):

        # Inicializa os parâmetros da janela tkinter
        self.root = Tk()
        self.root.title("McQueen Game")  # Título da janela
        self.root.geometry("480x640")    # Define o tamanho da janela
        self.root.resizable(0, 0)        # Desabilita a possibilidade de redimensionar a janela

        # Inicializa algumas variáveis do motor do jogo
        self.currentLv = 1              # Nível padrão: nível 1
        self.isLevelGenerated = False   # Verifica se o nível (mapa) foi gerado ou não
        self.isPlaying = False          # Verifica se o jogo foi realmente iniciado (em movimento) ou não
        self.statusStartingTimer = 0    # Temporizador de contagem regressiva para a funcionalidade 'prepare-se'
        self.statusDeadTimer = 0        # Temporizador de contagem regressiva para o evento de morte
        self.statusFinishTimer = 0      # Temporizador de contagem regressiva para o evento de finalização
        self.statusScore = 0            # Pontuação
        self.statusLife = 2             # Vidas

        # Chama a próxima fase da inicialização: carregamento de recursos
        self.__initResource()


    def __initResource(self):
        ## Lê os arquivos de sprite
        # Todos os sprites serão salvos neste dicionário
        self.wSprites = {
            'getready': PhotoImage(file="resource/sprite_get_ready.png"),
            'gameover': PhotoImage(file="resource/sprite_game_over.png"),
            'wall': PhotoImage(file="resource/sprite_wall.png"),
            'cage': PhotoImage(file="resource/sprite_cage.png"),
            'pellet': PhotoImage(file="resource/sprite_pellet.png")
        }

        # Vincula sprites para objetos em movimento
        for i in range(4):
            # Pacman: pacman(direção)(índice)
            if i == 3:
                pass
            else:
                self.wSprites['pacmanL{}'.format(i+1)] = PhotoImage(file="resource/sprite_pacman_left{}.png".format(i+1))
                self.wSprites['pacmanR{}'.format(i+1)] = PhotoImage(file="resource/sprite_pacman_right{}.png".format(i+1))
                self.wSprites['pacmanU{}'.format(i+1)] = PhotoImage(file="resource/sprite_pacman_up{}.png".format(i+1))
                self.wSprites['pacmanD{}'.format(i+1)] = PhotoImage(file="resource/sprite_pacman_down{}.png".format(i+1))
            # Fantasmas: ghost(índice1)(direção)(índice2)
            self.wSprites['ghost{}L1'.format(i+1)] = PhotoImage(file="resource/sprite_ghost_{}_left1.png".format(i+1))
            self.wSprites['ghost{}L2'.format(i+1)] = PhotoImage(file="resource/sprite_ghost_{}_left2.png".format(i+1))
            self.wSprites['ghost{}R1'.format(i+1)] = PhotoImage(file="resource/sprite_ghost_{}_right1.png".format(i+1))
            self.wSprites['ghost{}R2'.format(i+1)] = PhotoImage(file="resource/sprite_ghost_{}_right2.png".format(i+1))
            self.wSprites['ghost{}U1'.format(i+1)] = PhotoImage(file="resource/sprite_ghost_{}_up1.png".format(i+1))
            self.wSprites['ghost{}U2'.format(i+1)] = PhotoImage(file="resource/sprite_ghost_{}_up2.png".format(i+1))
            self.wSprites['ghost{}D1'.format(i+1)] = PhotoImage(file="resource/sprite_ghost_{}_down1.png".format(i+1))
            self.wSprites['ghost{}D2'.format(i+1)] = PhotoImage(file="resource/sprite_ghost_{}_down2.png".format(i+1))

        # Sprites de morte do Pacman
        for i in range(11):
            self.wSprites['pacmanDeath{}'.format(i+1)] = PhotoImage(file="resource/sprite_pacman_death{}.png".format(i+1))

        # Carrega os arquivos de som
        self.wSounds = {
            'chomp1': pygame.mixer.Sound(file="resource/sound_chomp1.wav"),
            'chomp2': pygame.mixer.Sound(file="resource/sound_chomp2.wav")
        }

        # Chama a próxima fase da inicialização: gerar widgets
        self.__initWidgets()


    def __initWidgets(self):
        # Inicializa widgets para a seleção de nível
        self.wLvLabel = Label(self.root, text="Digite o nível")
        self.wLvEntry = Entry(self.root)
        self.wLvBtn = Button(self.root, text="Ok", command=self.lvSelect, width=5, height=1)

        # Inicializa widgets para o jogo
        self.wGameLabelScore = Label(self.root, text=("Score: " + str(self.statusScore)))
        self.wGameLabelLife = Label(self.root, text=("Life: " + str(self.statusLife)))
        self.wGameCanv = Canvas(width=480, height=600)
        self.wGameCanvLabelGetReady = self.wGameCanv.create_image(240,326,image=None)
        self.wGameCanvLabelGameOver = self.wGameCanv.create_image(240,327,image=None)
        self.wGameCanvObjects = [[self.wGameCanv.create_image(0,0,image=None) for j in range(32)] for i in range(28)]
        self.wGameCanv.config(background="black")
        self.wGameCanvMovingObjects = [self.wGameCanv.create_image(0,0,image=None) for n in range(5)] # 0: pacman, 1-4: fantasmas

        # Ligações de teclas para o controle do jogo
        self.root.bind('<Left>', self.inputResponseLeft)
        self.root.bind('<Right>', self.inputResponseRight)
        self.root.bind('<Up>', self.inputResponseUp)
        self.root.bind('<Down>', self.inputResponseDown)
        self.root.bind('<Escape>', self.inputResponseEsc)
        self.root.bind('<Return>', self.inputResponseReturn)

        # Chama a próxima fase da inicialização: seleção de nível
        self.__initLevelSelect()


    def __initLevelSelect(self):
        ## Seleção de nível, mostrando todos os widgets relevantes
        self.wLvLabel.pack()
        self.wLvEntry.pack()
        self.wLvBtn.pack()

        # Executa o jogo
        self.root.mainloop()


    def lvSelect(self):
        try:
            self.__initLevelOnce(self.wLvEntry.get())

        except ValueError:
            self.wLvEntry.delete(0, END)  # Limpa a caixa de texto
            messagebox.showinfo("Erro!", "Digite um nível válido.")

        except FileNotFoundError:
            self.wLvEntry.delete(0, END)  # Limpa a caixa de texto
            messagebox.showinfo("Erro!", "Digite um nível válido.")


    def __initLevelOnce(self, level):
        ## Esta função será chamada apenas uma vez

        self.__initLevel(level)

        # Remove recursos de seleção de nível
        self.wLvLabel.destroy()
        self.wLvEntry.destroy()
        self.wLvBtn.destroy()
        # Posiciona o canvas e define isPlaying como True
        self.wGameCanv.place(x=0, y=30)
        self.wGameLabelScore.place(x=10, y=5)
        self.wGameLabelLife.place(x=420, y=5)


    def __initLevel(self, level):

        self.currentLv = int(level)
        field.gameEngine.levelGenerate(level)   # Gera o nível selecionado

        # Verifica o nome do objeto, vincula o sprite e ajusta suas coordenadas
        for j in range(32):
            for i in range(28):

                if field.gameEngine.levelObjects[i][j].name == "empty":
                    pass
                elif field.gameEngine.levelObjects[i][j].name == "wall":
                    self.wGameCanv.itemconfig(self.wGameCanvObjects[i][j], image=self.wSprites['wall'], state='normal')
                    self.wGameCanv.coords(self.wGameCanvObjects[i][j], 3+i*17+8, 30+j*17+8)
                elif field.gameEngine.levelObjects[i][j].name == "cage":
                    self.wGameCanv.itemconfig(self.wGameCanvObjects[i][j], image=self.wSprites['cage'], state='normal')
                    self.wGameCanv.coords(self.wGameCanvObjects[i][j], 3+i*17+8, 30+j*17+8)
                elif field.gameEngine.levelObjects[i][j].name == "pellet":
                    if field.gameEngine.levelObjects[i][j].isDestroyed == False:
                        self.wGameCanv.itemconfig(self.wGameCanvObjects[i][j], image=self.wSprites['pellet'], state='normal')
                        self.wGameCanv.coords(self.wGameCanvObjects[i][j], 3+i*17+8, 30+j*17+8)
                    else:
                        pass

        # Vincula a sprite e da a coordenada atual do McQueen
        self.wGameCanv.coords(self.wGameCanvMovingObjects[0],
                            3+field.gameEngine.movingObjectPacman.coordinateRel[0]*17+8,
                            30+field.gameEngine.movingObjectPacman.coordinateRel[1]*17+8)
        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanL1'], state='normal')

        # Vincula a sprite e da a coordenada atual dos tratores
        for i in range(4):
            if field.gameEngine.movingObjectGhosts[i].isActive == True:
                self.wGameCanv.coords(self.wGameCanvMovingObjects[i+1],
                                    3+field.gameEngine.movingObjectGhosts[i].coordinateRel[0]*17+8,
                                    30+field.gameEngine.movingObjectGhosts[i].coordinateRel[1]*17+8)
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[i+1], image=self.wSprites['ghost{}L1'.format(i+1)], state='normal')


        # Avance para a próxima fase
        pygame.mixer.music.stop()
        pygame.mixer.music.load("resource/sound_intro.mp3")
        pygame.mixer.music.play(loops=0, start=0.0)
        self.isLevelGenerated = True
        self.timerReady = PerpetualTimer(0.55, self.__initLevelStarting)
        self.timerReady.start()


    def inputResponseLeft(self, event):
        field.gameEngine.movingObjectPacman.dirNext = "Left"

    def inputResponseRight(self, event):
        field.gameEngine.movingObjectPacman.dirNext = "Right"

    def inputResponseUp(self, event):
        field.gameEngine.movingObjectPacman.dirNext = "Up"

    def inputResponseDown(self, event):
        field.gameEngine.movingObjectPacman.dirNext = "Down"

    def inputResponseEsc(self, event):
        self.timerLoop.stop()
        messagebox.showinfo("Game Over!", "You hit the escape key!")

    def inputResponseReturn(self, event):
        # Pular recurso
        if self.isLevelGenerated == True and self.isPlaying == False:
            self.gameStartingTrigger()
        else:
            pass



    def __initLevelStarting(self):
        self.statusStartingTimer += 1   # Timer da função

        # Vincula o sprite ao widget
        self.wGameCanv.itemconfig(self.wGameCanvLabelGetReady, image=self.wSprites['getready'])

        if self.statusStartingTimer < 8:
            # Pisca a função
            if self.statusStartingTimer % 2 == 1:
                self.wGameCanv.itemconfigure(self.wGameCanvLabelGetReady, state='normal')
            else:
                self.wGameCanv.itemconfigure(self.wGameCanvLabelGetReady, state='hidden')

        else:   #Depois do 8 loop o jogo vai iniciar com a função loopFunction
            self.gameStartingTrigger()


    def gameStartingTrigger(self):
        ## Para de printar 'get ready' e começa o jogo
        self.timerReady.stop()
        self.wGameCanv.itemconfigure(self.wGameCanvLabelGetReady, state='hidden')
        self.statusStartingTimer = 0
        self.isPlaying = True
        field.gameEngine.movingObjectPacman.dirNext = "Left"

        # Som dos tratores e musica
        pygame.mixer.music.stop()
        pygame.mixer.music.load("resource/sound_ghost.ogg")
        pygame.mixer.music.play(-1)

        self.timerLoop = PerpetualTimer(0.045, self.loopFunction)
        self.timerLoop.start()


    def loopFunction(self):

        field.gameEngine.loopFunction()

        coordGhosts = {}

        for i in range(4):
            coordGhosts['RelG{}'.format(i+1)] = field.gameEngine.movingObjectGhosts[i].coordinateRel    # ghosts relative coordinate
            coordGhosts['AbsG{}'.format(i+1)] = field.gameEngine.movingObjectGhosts[i].coordinateAbs    # ghosts absolute coordinate

        self.spritePacman(field.gameEngine.movingObjectPacman.coordinateRel, field.gameEngine.movingObjectPacman.coordinateAbs)
        self.spriteGhost(coordGhosts)
        self.encounterEvent(field.gameEngine.movingObjectPacman.coordinateRel, field.gameEngine.movingObjectPacman.coordinateAbs)




    def spritePacman(self, coordRelP, coordAbsP):
        ## Recurso do sprite do McQueen
        # Isso vai ajustar a coordenada e transformar a sprite em animação, baseado na sua absoluteCoord.
        if field.gameEngine.movingObjectPacman.dirCurrent == "Left":

            #  Verifica o obejeto passado pelas bordas do campo
            if field.gameEngine.movingObjectPacman.dirEdgePassed == True:
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 17*27+17, 0)    # Note que isso vai mover a sprite 17*27+17 (not 17*27+12) ja que o sprite vai se mover mais uma vez abaixo
                field.gameEngine.movingObjectPacman.dirEdgePassed = False
            else:
                pass

            if coordAbsP[0] % 4 == 0:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanL2'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], -4, 0)
            elif coordAbsP[0] % 4 == 1:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanL3'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], -4, 0)
            elif coordAbsP[0] % 4 == 2:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanL2'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], -4, 0)
            elif coordAbsP[0] % 4 == 3:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanL1'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], -5, 0)


        elif field.gameEngine.movingObjectPacman.dirCurrent == "Right":

            # Verifica o obejeto passado pelas bordas do campo
            if field.gameEngine.movingObjectPacman.dirEdgePassed == True:
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], -(17*27+17), 0)
                field.gameEngine.movingObjectPacman.dirEdgePassed = False
            else:
                pass

            if coordAbsP[0] % 4 == 0:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanR2'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 4, 0)
            elif coordAbsP[0] % 4 == 1:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanR3'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 4, 0)
            elif coordAbsP[0] % 4 == 2:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanR2'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 4, 0)
            elif coordAbsP[0] % 4 == 3:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanR1'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 5, 0)


        elif field.gameEngine.movingObjectPacman.dirCurrent == "Up":

            # Verifica o obejeto passado pelas bordas do campo
            if field.gameEngine.movingObjectPacman.dirEdgePassed == True:
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, 17*31+17)
                field.gameEngine.movingObjectPacman.dirEdgePassed = False
            else:
                pass

            if coordAbsP[1] % 4 == 0:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanU2'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, -4)
            elif coordAbsP[1] % 4 == 1:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanU3'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, -4)
            elif coordAbsP[1] % 4 == 2:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanU2'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, -4)
            elif coordAbsP[1] % 4 == 3:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanU1'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, -5)


        elif field.gameEngine.movingObjectPacman.dirCurrent == "Down":

            # Verifica o obejeto passado pelas bordas do campo
            if field.gameEngine.movingObjectPacman.dirEdgePassed == True:
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, -(17*31+17))
                field.gameEngine.movingObjectPacman.dirEdgePassed = False
            else:
                pass

            if coordAbsP[1] % 4 == 0:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanD2'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, 4)
            elif coordAbsP[1] % 4 == 1:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanD3'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, 4)
            elif coordAbsP[1] % 4 == 2:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanD2'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, 4)
            elif coordAbsP[1] % 4 == 3:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanD1'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, 5)


    def spriteGhost(self, coordGhosts):
        ## Recurso da sprite dos tratores
        # Isso vai ajustar a coordenada e transformar a sprite em animação, baseado na sua absoluteCoord.
        for ghostNo in range(4):
            if field.gameEngine.movingObjectGhosts[ghostNo].isActive == True:   # Apenas o trator ativo será mostrado
                if field.gameEngine.movingObjectGhosts[ghostNo].dirCurrent == "Left":

                    # Verifica o obejeto passado pelas bordas do campo
                    if field.gameEngine.movingObjectGhosts[ghostNo].dirEdgePassed == True:
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 17*27+17, 0)
                        field.gameEngine.movingObjectGhosts[ghostNo].dirEdgePassed = False
                    else:
                        pass

                    if coordGhosts['AbsG{}'.format(ghostNo+1)][0] % 4 == 0:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}L1'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], -4, 0)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][0] % 4 == 1:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}L1'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], -4, 0)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][0] % 4 == 2:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}L2'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], -4, 0)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][0] % 4 == 3:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}L2'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], -5, 0)


                elif field.gameEngine.movingObjectGhosts[ghostNo].dirCurrent == "Right":

                    # Verifica o obejeto passado pelas bordas do campo
                    if field.gameEngine.movingObjectGhosts[ghostNo].dirEdgePassed == True:
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], -(17*27+17), 0)
                        field.gameEngine.movingObjectGhosts[ghostNo].dirEdgePassed = False
                    else:
                        pass

                    if coordGhosts['AbsG{}'.format(ghostNo+1)][0] % 4 == 0:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}R1'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 4, 0)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][0] % 4 == 1:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}R1'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 4, 0)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][0] % 4 == 2:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}R2'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 4, 0)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][0] % 4 == 3:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}R2'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 5, 0)


                elif field.gameEngine.movingObjectGhosts[ghostNo].dirCurrent == "Up":

                    # Verifica o obejeto passado pelas bordas do campo
                    if field.gameEngine.movingObjectGhosts[ghostNo].dirEdgePassed == True:
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, 17*31+17)
                        field.gameEngine.movingObjectGhosts[ghostNo].dirEdgePassed = False
                    else:
                        pass

                    if coordGhosts['AbsG{}'.format(ghostNo+1)][1] % 4 == 0:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}U1'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, -4)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][1] % 4 == 1:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}U1'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, -4)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][1] % 4 == 2:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}U2'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, -4)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][1] % 4 == 3:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}U2'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, -5)


                elif field.gameEngine.movingObjectGhosts[ghostNo].dirCurrent == "Down":

                    # Verifica o obejeto passado pelas bordas do campo
                    if field.gameEngine.movingObjectGhosts[ghostNo].dirEdgePassed == True:
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, -(17*31+17))
                        field.gameEngine.movingObjectGhosts[ghostNo].dirEdgePassed = False
                    else:
                        pass

                    if coordGhosts['AbsG{}'.format(ghostNo+1)][1] % 4 == 0:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}D1'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, 4)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][1] % 4 == 1:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}D1'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, 4)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][1] % 4 == 2:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}D2'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, 4)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][1] % 4 == 3:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}D2'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, 5)

            else:   # Trator inativo
                pass


    def encounterEvent(self, coordRelP, coordAbsP):
        ## Encontrar recursos

        encounterMov = field.gameEngine.encounterMoving(coordAbsP[0], coordAbsP[1]) # Chamar encounterEvent pra mover objetos

        if encounterMov == 'dead':
            self.encounterEventDead()

        else:
            pass

        # Verifica se o objeto acerta a coordenada do mapa
        if coordAbsP[0] % 4 == 0 and coordAbsP[1] % 4 == 0:
            encounterFix = field.gameEngine.encounterFixed(coordRelP[0], coordRelP[1]) # Chamar a função encounterEvent

            if encounterFix == "empty":
                pass
            elif encounterFix == "pellet":
                if field.gameEngine.levelObjects[coordRelP[0]][coordRelP[1]].isDestroyed == False:  # Verifica se o pellet está vivo
                    field.gameEngine.levelObjects[coordRelP[0]][coordRelP[1]].isDestroyed = True # Destrói o pellet
                    self.wGameCanv.itemconfigure(self.wGameCanvObjects[coordRelP[0]][coordRelP[1]], state='hidden') # Remove da tela

                    # Toca o som (wa, ka, wa, ka, ...)
                    if self.statusScore % 20 == 0:
                        self.wSounds['chomp1'].play(loops=0)
                    else:
                        self.wSounds['chomp2'].play(loops=0)

                    self.statusScore += 10 # Ajusta o score
                    self.wGameLabelScore.configure(text=("Score: " + str(self.statusScore))) # Mostra o quadro
                    field.gameEngine.levelPelletRemaining -= 1 # Ajusta os numeros de pellet restantes

                    if field.gameEngine.levelPelletRemaining == 0:
                        self.encounterEventLevelClear() # Level limpo
                    else:
                        pass


                else:   # Pellet já foi pego
                    pass

        else: # McQueen não está no mapa
            pass


    def encounterEventLevelClear(self):
        # Pausa o jogo
        pygame.mixer.music.stop()
        self.timerLoop.stop()
        self.isPlaying = False

        for i in range(5):  # Esconde as sprites se mexendo
            self.wGameCanv.itemconfigure(self.wGameCanvMovingObjects[i], state='hidden')

        self.timerClear = PerpetualTimer(0.4, self.encounterEventLevelClearLoop)
        self.timerClear.start()


    def encounterEventLevelClearLoop(self):
        self.statusFinishTimer += 1   # Cronometro da função

        if self.statusFinishTimer < 9:
            # Parede piscando
            if self.statusFinishTimer % 2 == 1:
                self.wSprites.update({'wall': PhotoImage(file="resource/sprite_wall2.png")})
                for j in range(32):
                    for i in range(28):
                        if field.gameEngine.levelObjects[i][j].name == "wall":
                            self.wGameCanv.itemconfig(self.wGameCanvObjects[i][j], image=self.wSprites['wall'])
                        else:
                            pass
            else:
                self.wSprites.update({'wall': PhotoImage(file="resource/sprite_wall.png")})
                for j in range(32):
                    for i in range(28):
                        if field.gameEngine.levelObjects[i][j].name == "wall":
                            self.wGameCanv.itemconfig(self.wGameCanvObjects[i][j], image=self.wSprites['wall'])
                        else:
                            pass

        else:   # Depois do 11 loop, o processo de level limpo vai ser continuado
            self.encounterEventLevelClearFinish()


    def encounterEventLevelClearFinish(self):
        self.timerClear.stop()
        self.statusFinishTimer = 0

        # Reseta todos os valores e esconde a sprite (ou o processo de geração de level será mostrado)
        for j in range(32):
            for i in range(28):
                field.gameEngine.levelObjects[i][j].reset('')
                #self.wGameCanv.itemconfigure(self.wGameCanvObjects[i][j], state='hidden')

        field.gameEngine.movingObjectPacman.reset('Pacman')

        for n in range(4):
            field.gameEngine.movingObjectGhosts[n].reset('Ghost')

        self.currentLv += 1
        self.isLevelGenerated = False
        self.__initLevel(self.currentLv)



    def encounterEventDead(self):

        self.statusLife -= 1    # Tira a vida restante

        if self.statusLife >= 0:
            self.wGameLabelLife.configure(text=("Life: " + str(self.statusLife))) # Mostra no quadro
        else:   # Previne de mostrar a vida restante (game over de qualquer jeito)
            pass

        # Pausa o jogo
        self.isPlaying = False
        pygame.mixer.music.stop()
        self.timerLoop.stop()

        # Chama o loop de morte
        self.timerDeath = PerpetualTimer(0.10, self.encounterEventDeadLoop)
        self.timerDeath.start()


    def encounterEventDeadLoop(self):

        self.statusDeadTimer += 1   # Cronômetro da função

        if self.statusDeadTimer <= 5:   # Espera um pouco
            pass

        elif self.statusDeadTimer == 6:
            # sfx
            pygame.mixer.music.load("resource/sound_death.mp3")
            pygame.mixer.music.play(loops=0, start=0.0)
            for i in range(4):  # Esconde a sprite do trator e inicia seus seus status
                self.wGameCanv.itemconfigure(self.wGameCanvMovingObjects[i+1], state='hidden')
                field.gameEngine.movingObjectGhosts[i].isActive = False
                field.gameEngine.movingObjectGhosts[i].isCaged = True

        elif 6 < self.statusDeadTimer <= 17:    # Anima a sprite de morte
            self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0],
                                        image=self.wSprites['pacmanDeath{}'.format(self.statusDeadTimer-6)])

        elif self.statusDeadTimer == 18:    # Pisca
            self.wGameCanv.itemconfigure(self.wGameCanvMovingObjects[0], state='hidden')

        elif 18 < self.statusDeadTimer <= 22:   # Espera um pouco
            pass

        else:
            self.encounterEventDeadRestart()


    def encounterEventDeadRestart(self):
        ## Para o evento de morte e reinicia o jogo
        if self.statusLife >= 0:
            self.statusDeadTimer = 0    # Reseta o tempo
            self.timerDeath.stop()      # Para o time do evento de morte
            self.isPlaying = False      # isPlaying é checadp
            field.gameEngine.levelPelletRemaining = 0   # Pellet contador é resetadp (em __initLevel)
            self.__initLevel(self.currentLv)

        else:   # game over
            self.statusDeadTimer = 0
            self.timerDeath.stop()
            self.gameOverTimer = PerpetualTimer(0.55, self.encounterEventDeadGameOver)
            self.gameOverTimer.start()



    def encounterEventDeadGameOver(self):
        self.statusDeadTimer += 1
        self.wGameCanv.itemconfig(self.wGameCanvLabelGameOver, image=self.wSprites['gameover'])

        if self.statusDeadTimer < 8:
            # Função piscando
            if self.statusDeadTimer % 2 == 1:
                self.wGameCanv.itemconfigure(self.wGameCanvLabelGameOver, state='normal')
            else:
                self.wGameCanv.itemconfigure(self.wGameCanvLabelGameOver, state='hidden')

        else:   # Depois do oitavo loop jogo é finalizado
            self.gameOverTimer.stop()




class PerpetualTimer(object):

    def __init__(self, interval, function, *args):
        self.thread = None
        self.interval = interval
        self.function = function
        self.args = args
        self.isRunning = False


    def _handleFunction(self):
        self.isRunning = False
        self.start()
        self.function(*self.args)

    def start(self):
        if not self.isRunning:
            self.thread = Timer(self.interval, self._handleFunction)
            self.thread.start()
            self.isRunning = True

    def stop(self):
            self.thread.cancel()
            self.isRunning = False


# Inicia pygame para sfx
pygame.mixer.init(22050, -16, 2, 64)
pygame.init()

mainEngine = MainEngine()