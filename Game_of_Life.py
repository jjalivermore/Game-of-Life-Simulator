# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 21:34:50 2023

@author: james
"""

import pygame
import numpy as np
import random
import time
import pickle

def main(fname=None):
    global screen
    # pygame setup
    pygame.init()
    config = {}
    size = [1600, 900]
    maxfps = 60
    pixsize = 5
    textsize = {}
    textsize['L'] = int(size[0] / 20)
    textsize['M'] = int(textsize['L'] * .75)
    textsize['S'] = int(textsize['L'] * .5)
    textsize['XS'] = int(textsize['L'] * .3)
    screen = pygame.display.set_mode((size[0], size[1]))
    pygame.display.set_caption('Game of Life')
    clock = pygame.time.Clock()
    dt = 0
    
    # colours: [live cell & text, new cell, cell to be placed, background, anticell, new anticell]
    colours = [['white','red','gray','black','blue','green'],
               ['black','red','gray','white','blue','green'],
               ['red','white','gray','purple','green','blue']]
    colourset = 0
    wrap = False
    
    config['size'] = size
    config['textsize'] = textsize
    config['pixsize'] = pixsize
    config['dt'] = dt
    config['colours'] = colours
    config['colourset'] = colourset
    config['wrap'] = wrap
    config['shapes'] = init_shapes()
    config['maxfps'] = maxfps
    config['update_rules'] = {'survive':[2,3],'birth':[3],
                    'survive_am':[-2,-3],'birth_am':[-3]}
    
    steps = 0
    pause = True
    equil = False
    pmode = False
    rerun = False
    cells = []
    if fname is None:
        vals, cols, running, config = start_mode(config)
    else:
        with open(fname, 'rb') as handle:
            nowload = pickle.load(handle)
        config = nowload['config']
        vals = nowload['vals']
        cols = np.zeros_like(vals)
        cols[vals==-1] = 4
        pause = False
        running = True
    colourset = config['colourset']
    histvals = list([vals])
    
    while running:
        #font = pygame.font.SysFont('None', textsize['S'])
        
        # editing grid while paused
        if pause and not equil:
            vals, running, rerun, config = edit_mode(vals, cols, histvals, config)
            pause = False
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        keys = pygame.key.get_pressed()
    
        # fill the screen with a color to wipe away anything from last frame
        screen.fill(colours[colourset][3])
            
        render_grid(vals,cols,config,extra=None)
        
        if (steps > 3) and np.all(histvals[-3]==histvals[-1]):
                pause = True
                equil = True
                textequil = pygame.font.Font.render(pygame.font.SysFont('None', textsize['L']), 'Equilibrium reached!', True, colours[colourset][0])
                screen.blit(textequil, (size[0]/2 - textequil.get_rect().width/2, size[1]/2 - textequil.get_rect().height/2)) # - text.get_rect().width/2
                
        if keys[pygame.K_SPACE]:
            if equil:
                equil = False
                pause = False
                steps = 0
            pause = not pause
            pmode = False
            pygame.display.flip()
            time.sleep(.2)
        
        if not pause:
            vals, cols = update_vals(vals, cols, config)
            steps += 1
            histvals.append(vals.copy())
        
        #if (steps > 10000) and not pause: # Uncomment to prevent overflow histvals
        #    histvals = histvals[1:]
    
        cells.append(np.sum(np.sum(vals)))
        try:
            fps = np.round(np.divide(1,dt),1)
        except:
            fps = 0
            
        text = [f'CELLS: {cells[-1]}', f'STEPS: {steps}', f'FPS: {fps}']
        colour = colours[colourset][0]
        tsize = textsize['S']
        gap = tsize + 10
        xpos = int(size[0]*.875)
        top_right_corner_text(text,colour,tsize,xpos,gap) 
    
        if keys[pygame.K_ESCAPE] or rerun:
            steps = 0
            pause = True
            rerun = False
            time.sleep(.2)
            vals, cols, running, config = start_mode(config)
        if keys[pygame.K_p]:
            pmode = True
        if pmode:
            colourset = np.mod(colourset+1,len(colours))

        pygame.display.flip()
        
        # limits FPS to 120
        dt = clock.tick(config['maxfps']) / 1000    
    
    pygame.quit()
    
    return cells, histvals


# shapes
def init_shapes():
    shapes = {}
    shapes['SINGLE BLOCK'] = np.array([1])
    shapes['GOSPER GUN'] = np.array([[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
                                     [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                                     [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                                     [1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                     [1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
                                     [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
                                     [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                     [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]])
    shapes['R-PENTOMINO'] = np.array([[0,1,1],
                                      [1,1,0],
                                      [0,1,0]])
    shapes['GLIDER'] = np.array([[0,0,1],
                                 [1,0,1],
                                 [0,1,1]])
    
    shapes['SPACE RAKE'] = np.array([[0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,1,1,1,1],
                                     [0,0,0,0,0,0,0,0,0,0,1,1,0,1,1,0,0,0,1,0,0,0,1],
                                     [0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,1],
                                     [0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,1,0,0,1,0],
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                     [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                     [0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0],
                                     [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0],
                                     [0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,1,0,0,1,0,0],
                                     [0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,1,1,0,1,1,0,0],
                                     [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,1,0,0,0,0],
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1],
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
                                     [0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                                     [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0],
                                     [0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                     [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]])
    
    return shapes
    

# functions
def initialise_grid(config):
    pixsize = config['pixsize']
    size = config['size']
    gridx, gridy=(np.mgrid[0:size[0]:pixsize+2,0:size[1]:pixsize+2])
    vals = np.zeros_like(gridx)
    cols = np.zeros_like(gridx)
    vx = vals.shape[0]
    vy = vals.shape[1]
    config['gridx'] = gridx
    config['gridy'] = gridy
    config['vx'] = vx
    config['vy'] = vy
    
    return vals, cols, config


def start_mode(config):
    vals, cols, config = initialise_grid(config)
    colours = config['colours']
    colourset = config['colourset']
    textsize = config['textsize']
    vx = config['vx']
    vy = config['vy']
    wrap = config['wrap']
    maxfps = config['maxfps']
    update_rules = config['update_rules']
    running = True
    antimatter = False
    config['antimatter'] = antimatter
    
    
    birth = ''
    survive = ''
    for num in config['update_rules']['birth']:
        birth += str(num)
    for num in config['update_rules']['survive']:
        survive += str(num)
    
    while running:
        text = ['Welcome to Conway\'s Game of Life!',
                '1: Start with empty grid',
                '2: Start with randomised grid',
                '3: Start with demo grid',
                '4: Load saved configuration',
                '5: Options']
        textsizes=['L','M','M','M','M','M']
        responsekeys=[pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_ESCAPE]
        response, running = text_menu(text,textsizes,responsekeys,config)
        
        if response == pygame.K_1:
            break
        elif response == pygame.K_2:
            prompt = 'Enter probability for each cell to be live:'
            tsize = textsize['M']
            p, running = get_response(prompt,tsize,'0.',config)
            p = float(p)
            for i in range(vx):
                for j in range(vy):
                    vals[i,j] = int(random.random() < p)
                    if antimatter: vals[i,j] *= (2 * int(random.random() < .5) - 1)
            cols[vals==-1] = 4
            break
        elif response == pygame.K_3:
            vals[100,:] = 1
            vals = add_shape(vals, config['shapes']['GOSPER GUN'], [0,0])
            break
        elif response == pygame.K_4:
            time.sleep(.2)
            prompt = 'Enter filename to load:'
            tsize = textsize['M']
            fname, running = get_response(prompt,tsize,'',config,letters=True)
            fname += '.pkl'
            try:
                with open(fname, 'rb') as handle:
                    nowload = pickle.load(handle)
                config = nowload['config']
                vals = nowload['vals']
                cols = np.zeros_like(vals)
                cols[vals==-1] = 4
                break
            except:
                _, running = get_response(f'Filename {fname} not found! Press enter to continue.',tsize,'',config,numbers=False,letters=False) 
        elif response == pygame.K_5:
            textsizes = ['L','M','M','M','M','M','M','M']
            responsekeys=[pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_ESCAPE]
            onoff = ['on', 'off']
            endis = ['Enable', 'Disable']
            while True:
                text = ['Options',
                        f'1: Turn wrap {onoff[1] if wrap else onoff[0]}',
                        '2: Choose block size',
                        f'3: Change max FPS - currently {maxfps}',
                        '4: Change colour set',
                        f'5: Choose rule set - currently B{birth}/S{survive}',
                        f'6: {endis[1] if antimatter else endis[0]} antimatter mode',
                        '7: Return to main menu']
                response, running = text_menu(text,textsizes,responsekeys,config)
                if response == pygame.K_1:
                    wrap = not wrap
                    config['wrap'] = wrap
                if response == pygame.K_2:
                    prompt = 'Enter size of block in pixels:'
                    tsize = textsize['M']
                    pixsize, running = get_response(prompt,tsize,'7',config)
                    config['pixsize'] = int(pixsize)
                    vals, cols, config = initialise_grid(config)
                if response == pygame.K_3:
                    prompt = 'Enter max FPS:'
                    tsize = textsize['M']
                    maxfps, running = get_response(prompt,tsize,'',config)
                    maxfps = int(maxfps)
                    config['maxfps'] = maxfps
                if response == pygame.K_4:
                    colourset = np.mod(colourset+1, len(colours))
                    config['colourset'] = colourset
                if response == pygame.K_5:
                    update_rules['survive'] = []
                    update_rules['birth'] = []
                    update_rules['survive_am'] = []
                    update_rules['birth_am'] = []
                    prompt = 'Enter # of neighbour(s) to birth cell (B):'
                    tsize = textsize['M']
                    birth, running = get_response(prompt,tsize,'',config)
                    prompt = 'Enter # of neighbour(s) for cell to survive (S):'
                    survive, running = get_response(prompt,tsize,'',config)
                    for i in birth:
                        update_rules['birth'].append(int(i))
                        update_rules['birth_am'].append(-int(i))
                    for i in survive:
                        update_rules['survive'].append(int(i))
                        update_rules['survive_am'].append(-int(i))
                    config['update_rules'] = update_rules
                if response == pygame.K_6:
                    antimatter = not antimatter
                    config['antimatter'] = antimatter
                if (response == pygame.K_7) or (response == pygame.K_ESCAPE):
                    time.sleep(.2)
                    break
        elif response == pygame.K_ESCAPE:
            running = False
    
    return vals, cols, running, config


def text_menu(text,textsizes,responsekeys,config):
    colours = config['colours']
    colourset = config['colourset']
    textsize = config['textsize']
    size = config['size']
    
    screen.fill(colours[colourset][3])
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
        keys = pygame.key.get_pressed()
        for n,t in enumerate(text):
            nowtext = pygame.font.Font.render(pygame.font.SysFont('None', textsize[textsizes[n]]), t, True, colours[colourset][0])
            textds = [nowtext.get_rect().width/2, nowtext.get_rect().height/2]
            screen.blit(nowtext, (int(size[0]/2) - textds[0], int(size[1]*.75) - textds[1]*(len(text)-n)*3))
            
        pygame.display.flip()
        
        for k in responsekeys:
            if keys[k]:
                time.sleep(.2)
                break
        else:
            continue
        break
            
    return k, running
        

def get_response(prompt,tsize,string,config,numbers=True,letters=False):
    size = config['size']
    colours = config['colours']
    colourset = config['colourset']
    listenkeys = {}
    if numbers or letters:
        listenkeys = {pygame.K_BACKSPACE: '', pygame.K_PERIOD: '.'}
    if numbers:
        for i in range(10):
            listenkeys[getattr(pygame,'K_' + str(i))] = str(i)
    if letters:
        for i in 'abcdefghijklmnopqrstuvwxyz':
            listenkeys[getattr(pygame,'K_' + i)] = i
        listenkeys[pygame.K_UNDERSCORE] = '_'
        listenkeys[pygame.K_MINUS] = '-'
    text = [prompt, string]
    running = True
    while running:
        screen.fill(colours[colourset][3])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
        keys = pygame.key.get_pressed()
        for n,t in enumerate(text):
            nowtext = pygame.font.Font.render(pygame.font.SysFont('None', tsize), t, True, colours[colourset][0])
            textds = [nowtext.get_rect().width/2, nowtext.get_rect().height/2]
            screen.blit(nowtext, (size[0]/2 - textds[0], size[1]/2 - textds[1]*(len(text)-n)*3))
            
        pygame.display.flip()
        
        for k, s in listenkeys.items():
            if keys[k]:
                if k == pygame.K_BACKSPACE:
                    string = string[:-1]
                else:
                    string = string + s
                time.sleep(.2)
                text = [prompt, string]
                break
        if keys[pygame.K_RETURN]:
            time.sleep(.2)
            break
            
    return string, running


def top_right_corner_text(text,colour,tsize,xpos,gap):   
    if type(tsize) == int:
        tsize = np.repeat(tsize, len(text))
    
    for n,t in enumerate(text):
        text = pygame.font.Font.render(pygame.font.SysFont('None', tsize[n]), t, True, colour)
        screen.blit(text, (xpos, gap*(n+1)))


def add_shape(grid, shape, pos=[0,0], flip=False, rotate=False, remove=False):
    pos = [np.max(pos[0],0), np.max(pos[1],0)]
    if remove:
        shape[:] = 0
    if flip:
        try:
            shape = np.fliplr(shape)
        except:
            pass
    if rotate:
        try:
            shape = np.rot90(shape, rotate)
        except:
            pass
    xpos = pos[0]+shape.shape[0]
    try:
        ypos = pos[1]+shape.shape[1]
    except:
        ypos = pos[1]+shape.shape[0]
    if xpos > grid.shape[0]:
        xpos = grid.shape[0]
        pos[0] = xpos - shape.shape[0]
    if ypos > grid.shape[1]:
        ypos = grid.shape[1] 
        pos[1] = ypos - shape.shape[1]
    grid[pos[0]:xpos, pos[1]:ypos] = shape
    
    return grid


def update_vals(vals, cols, config):    

    wrap = config['wrap']
    update_rules = config['update_rules']
    vx = config['vx']
    vy = config['vy']
    antimatter = config['antimatter']
    
    # update with rules for next
    oldvals = vals.copy()
    
    check = np.zeros_like(vals)
    check[:,0] = 1       
    check[0,:] = 1    
    if wrap:
        check[:,-1] = 1
        check[-1,:] = 1
    for i in range(1,vals.shape[0]):
        for el in np.nonzero(np.diff(vals[i,:]))[0]:
            #print(el)
            
            check[i-1:i+2,el:el+3] = 1
    for j in range(1,vals.shape[1]):
        for el in np.nonzero(np.diff(vals[:,j]))[0]:
            check[el:el+3,j-1:j+2] = 1
    checkinds = np.argwhere(check==1)
    for inds in checkinds:
        i = inds[0]
        j = inds[1]
        irange = np.array([i-1,i,i+1])
        jrange = np.array([j-1,j,j+1])
        
        if not((i > 0) and (i < vx-1) and (j > 0) and (j < vy-1)):
            if (i==0) and not wrap:
                irange = irange[1:]
            elif i==0:
                irange[0] = vx-1
            elif (i==vx-1) and not wrap:
                irange = irange[:2]
            elif (i==vx-1) and wrap:
                irange[2] = 0
            if (j==0) and not wrap:
                jrange = jrange[1:]
            elif j==0:
                jrange[0] = vy-1
            elif (j==vy-1) and not wrap:
                jrange = jrange[:2]
            elif (j==vy-1) and wrap:
                jrange[2] = 0            
        
            xinds = np.repeat(irange,len(jrange))
            yinds = np.tile(jrange,len(irange))
            neighbours = np.sum(oldvals[xinds,yinds])         
        else:
            neighbours = np.sum(oldvals[i-1:i+2,j-1:j+2])

        if vals[i,j] == 1:
            neighbours -= 1
            cols[i,j] = 0
            if neighbours not in update_rules['survive']:
                vals[i,j] = 0
        elif vals[i,j] == 0:
            if neighbours in update_rules['birth']:
                vals[i,j] = 1
                cols[i,j] = 1   
            elif antimatter and neighbours in update_rules['birth_am']:
                vals[i,j] = -1
                cols[i,j] = 5
        elif antimatter and vals[i,j] == -1:
            neighbours += 1
            cols[i,j] = 4
            # Anti-Rule 1
            if neighbours not in update_rules['survive_am']:
                vals[i,j] = 0
            
            
    return vals, cols


def render_grid(vals,cols,config,extra=None):
    gridx = config['gridx']
    gridy = config['gridy']
    pixsize = config['pixsize']
    colours = config['colours']
    colourset = config['colourset']
    if extra is not None:
        vals = (vals.astype(bool) | extra.astype(bool)).astype(int)
        cols[extra==1] = 2
    live = np.where(np.abs(vals) == 1)
        
    for ind in range(0,live[0].shape[0]):
        i = live[0][ind]
        j = live[1][ind]
        pygame.draw.rect(screen, colours[colourset][cols[i,j]], pygame.Rect(gridx[i,j],gridy[i,j],pixsize,pixsize))


def pix_to_grid_space(pos,config):
    gridx = config['gridx']
    gridy = config['gridy']
    
    try:
        xpos = np.argwhere(gridx[:,0]>pos[0])[0][0]-1
    except:
        xpos = np.argmax(gridx[:,0])
    try:
        ypos = np.argwhere(gridy[0,:]>pos[1])[0][0]-1
    except:
        ypos = np.argmax(gridy[0,:])
        
    return [xpos,ypos]


def edit_mode(vals,cols,histvals,config):
    size = config['size']
    textsize = config['textsize']
    colours = config['colours']
    colourset = config['colourset']
    shapes = config['shapes']
    shapenames = list(shapes.keys())
    wrap = config['wrap']
    antimatter = config['antimatter']
    
    flip = False
    rotate = 0
    extra = None
    shapeind = 0
    pause=True
    running = True
    rerun = False
    nowantimatter = False
    while pause:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pause = False
                break
        screen.fill(colours[colourset][3])

        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()
        extra = add_shape(np.zeros_like(vals), shapes[shapenames[shapeind]], pos=pix_to_grid_space(pos,config), flip=flip, rotate=rotate)
        if mouse[0]:
            s = shapes[shapenames[shapeind]]
            if nowantimatter:
                s = s*-1
            vals = add_shape(vals, s, pos=pix_to_grid_space(pos,config), flip=flip, rotate=rotate)
            time.sleep(.15)
        if mouse[2]:
            s = shapes[shapenames[shapeind]]
            vals = add_shape(vals, s, pos=pix_to_grid_space(pos,config), flip=flip, rotate=rotate, remove=True)
            time.sleep(.15)
        render_grid(vals,cols,config,extra=extra)
        
        onoff = ['ON', 'OFF']
        anti = ['ANTI','']
        text = ['EDITING MODE', 'SPACE: RESUME', 'ESC: MAIN MENU', 'S: SAVE CONFIG', '> ' + shapenames[shapeind],
                'LEFT / RIGHT ARROW: CYCLE SHAPE', 'R: ROTATE SHAPE', 'F: FLIP SHAPE',
                f'W: TURN WRAP {onoff[1] if wrap else onoff[0]}',
                f'A: SWITCH TO PLACING {anti[0] if not nowantimatter else anti[1]}MATTER']
        if not antimatter:
            text[-1]=''
        colour = colours[colourset][0]
        tsize = np.array([textsize['S'], textsize['XS'], textsize['XS'], textsize['XS'], textsize['S'],
                          textsize['XS'], textsize['XS'], textsize['XS'], textsize['XS'], 
                          textsize['XS']])
        xpos = int(size[0]*.8)
        gap = tsize[0] + 10
        
        top_right_corner_text(text,colour,tsize,xpos,gap)
        
        if keys[pygame.K_SPACE]:
            pause = not pause
            time.sleep(.2)
            break
        if keys[pygame.K_s]:
            time.sleep(.2)
            prompt = 'Enter filename to save:'
            tsize = textsize['M']
            fname, running = get_response(prompt,tsize,'',config,letters=True)
            nowsave = {'config': config, 'vals': histvals[0]}
            with open(fname + '.pkl', 'wb') as handle:
                pickle.dump(nowsave, handle, protocol=pickle.HIGHEST_PROTOCOL)
        if keys[pygame.K_f]:
            flip = not flip
            time.sleep(.2)
        if keys[pygame.K_r]:
            rotate += 1
            time.sleep(.2)
        if keys[pygame.K_LEFT]:
            shapeind = np.mod(shapeind-1,len(shapes))
            time.sleep(.2)
        if keys[pygame.K_RIGHT]:
            shapeind = np.mod(shapeind+1,len(shapes))
            time.sleep(.2)
        if keys[pygame.K_w]:
            wrap = not wrap
            time.sleep(.2)
        if (keys[pygame.K_a] and antimatter):
            nowantimatter = not nowantimatter
            time.sleep(.2)
        if keys[pygame.K_ESCAPE]:
            rerun = True
            pause = False
        pygame.display.flip()
    
    config['wrap'] = wrap
    
    return vals, running, rerun, config


def arrays_list_conv(dict_in,array_to_list=True):
    for key,item in dict_in.items():
        if array_to_list and type(item)==dict:
            dict_in[key] = arrays_list_conv(item)
        elif array_to_list:
            try: dict_in[key] = dict_in[key].tolist()
            except: pass
        elif type(item)==dict:
            dict_in[key] = arrays_list_conv(item, False)
        elif type(item)==list:
            dict_in[key] = np.array(dict_in[key])
            
    return dict_in
                        

if __name__ == '__main__':
    main()