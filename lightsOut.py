#This is the version of the program that can use gradients on the
#buttons. 


#Adam Sinck
#Lights Out
#This program will implement a lights out game.
#I programmed this for fun.

#The goal of the game is to turn the lights (white squares) off
#(black).  This is accomplished by clicking on the squares, which
#toggles that square and the vertically and horizontally adjacent
#squares. If a square is on the edge or in a corner, it only toggles
#squares that are available to be toggled; it doesn't wrap around the
#board.

#For more information, visit
#http://en.wikipedia.org/wiki/Lights_Out_%28game%29


#this is a list of import commands. If the user doesn't have Tkinter
#or other libraries installed, it will fail gracefully instead of
#crashing.
imports = [
    "from Tkinter import *",
    "import tkMessageBox",
    "import io",
    "import string",
    "import random",
    "import time",
    "import Image, ImageDraw",
    "import math"
]
#failedPackages will keep a record of the names of the packages that
#failed to import, so that the program can go through the entire list
#of packages that it wants to import. This will allow the program to
#give the user a complete list of packages that they need to install,
#instead of only telling the user one at a time.
failedPackages = ''
for i in imports:
    try:
        exec(i)
    except ImportError as error:
        failedPackages += str(error) + '\n'
#if there were any errors in the imports, tell the users what packages
#didn't import, and exit.
if len(failedPackages) > 0:
    print "Some packages could not be imported:"
    print failedPackages
    exit()


#some global variables
lights = {}
scores = {}
#a move count for high scores and to let the user know how many moves
#they've made
moves = 0
#this is so that the program knows when it's scrambling the board, for
#the move count. The program scrambles by "clicking" on random
#buttons, and if it didn't know when it was scrambling, it would set
#high scores when it accidentally solved the board during the
#scrambling
scrambling = False

#these are for the settings
#the board can be resized to arbitrary widths/heights
row = 5
col = 5
size = row * col

#this holds whether or not the user has gradients on the buttons or not
gradient = True

#this will start a new game
def newGame():
    win.pack_forget()
    puzzleFrame.pack_forget()
    puzzle[0].pack_forget()
    del puzzle[0]
    puzzleFrame.pack()
    puzzle[0] = Frame(puzzleFrame)
    puzzle[0].pack()
    init()

#This will automate the "chase" algorithm for solving all but the
#bottom row. This is helpful for users that use the algorithm, and
#want to speed up the process by having the program do it for them,
#because it's tedious and a lot of clicking.

#This is also helpful for users that don't know the algorithm or how
#to solve the puzzle at all, and want to cheat. :)

#Spoiler for the solution:
#The chase algorithm works as follows:
#    It starts in the second row, and "clicks" on any square that has
#    a light on above it. This has the effect of turning off all the
#    lights from the first row. It repeats this in the third row to
#    turn off all the lights in the second row, and so on until it has
#    turned off all lights except those in the bottom row. At that
#    point, the chase algorithm is finished (for the moment), and the
#    user must know the lights to turn on in the first row so that the
#    next time the chase algorithm runs, it works out such that the
#    bottom row is solved at the same time as the second row up.

#One of my later goals is to make an AI that can actually solve
#puzzles of arbitrary sizes, but this isn't so much of a feature for
#the user as a programming puzzle for me to try. If I wanted to just
#solve it for the user, I could make the program turn all of the
#squares black.

#On the other hand, if I do write an algorithm that solves the puzzle,
#I could put a delay in the solving, so that it looks animated and the
#solution can be followed. This could lead to insight about how to
#solve the puzzle, and help new users.

def chase():
    for i in range(col, size):
        if lights[i-col][0]["image"] == str(fg):
            change(i)

#this will update the high scores.
def updateHighScores():
    text = open('highscores.txt', 'r')
    table = {}
    currentSize = str(col) + "x" + str(row)
    #make the table of scores
    for i in text:
        s = ''
        if i.strip():
            line = i.strip()
            s = line.split(' ')
            if s[0] in table:
                table[s[0]].append(int(s[1]))
            else:
                table[s[0]] = []
                table[s[0]].append(int(s[1]))

    text.close()
    if table == {} or currentSize not in table:
        table[currentSize] = []
    #update the scores
    initScores = [i for i in table[currentSize]]
    temp = 0
    count = 0
    table[currentSize].append(moves)
    a = sorted(table[currentSize])
    table[currentSize] = sorted(table[currentSize])
    table[currentSize] = table[currentSize][0:10]
    
    s = ''
    text = open('highscores.txt', 'w')
    for key in table:
        for arrayEntry in table[key]:
            s += str(key) + " " + str(arrayEntry) + '\n'
    text.write(s)
    text.close()
    newHighScore = False
    #do some checking to see if the user set a high score, and let
    #them know if they did
    if len(initScores) == 0 or len(initScores) < len(table[currentSize]):
        newHighScore = True
    else:
        for i in range(len(table[currentSize])):
            num1 = table[currentSize][i]
            num2 = initScores[i]
            if num1 != num2:
                newHighScore = True
    
    if newHighScore:
        tkMessageBox.showinfo("High Score!", "You set a new high score!")
        
#this will show the user the high scores for the current puzzle size
def showHighScores():
    numbers = ['first', 'second', 'third', 'fourth', 'fifth',
               'sixth', 'seventh', 'eighth', 'ninth', 'tenth'
              ]
    text = open('highscores.txt')
    s = "scores for a %dx%d puzzle:\n" %(row, col)
    count = 0
    for i in text:
        if i.strip():
            line = i.strip()
            hs = line.split(' ')
            if hs[0] == str(col) + "x" + str(row):
                count += 1
                s += numbers[count - 1] + ":  " + str(hs[1]) + '\n'
    text.close
    tkMessageBox.showinfo("Highscores", s)

#this will show the settings frame
def showSettings():
    settingsFrame.pack(side=RIGHT)

#this will hide the settings frame
def hideSettings():
    settingsFrame.pack_forget()

#this will apply the settings
def updateSettings(var=None):
    global row, col, size
    newRow = rowInput.get()
    newCol = colInput.get()
#    newbgColor = bgColorInput.get()
#    newfgColor = fgColorInput.get()
    resized = False
    if newRow != '' and int(newRow) != row:
        row = int(newRow)
        size = row*col
        resized = True
    if newCol != '' and int(newCol) != col:
        col = int(newCol)
        size = row*col
        resized = True

    if resized:
        resize(row, col)
    changeColors()


def processColor(color):
    if color == '':
        return ''
    color = color.replace("#",'')
    if len(color) != 6:
        r, g, b = color[0], color[1], color[2]
        return "#" + r+r+g+g+b+b
    return "#" + color
    
def toggleGradient(var=None):
    global gradient
    if gradient:
        gradient = False
        gradientButton.config(text = "Turn Gradient On", bg = "#CCC")
    else:
        gradient = True
        gradientButton.config(text = "Turn Gradient Off", bg = "#999")

#this applies a color settings change to the board
def changeColors(var=None):
    global bg,fg,gradient

    #background
    bgInput = processColor(bgColorInput.get())
    newBG = bg
    if bgInput != '':
        if gradient:
            generateColor(bgInput)
        else:
            img = Image.new("RGB", (30,30), bgInput)
            img.save("out.png", "PNG")
        newBG = PhotoImage(file="out.png")
    
    #foreground
    fgInput = processColor(fgColorInput.get())
    newFG = fg
    if fgInput != '':
        if gradient:
            generateColor(fgInput)
        else:
            img = Image.new("RGB", (30,30), fgInput)
            img.save("out.png", "PNG")
        newFG = PhotoImage(file="out.png")
    
    for i in range(size):
        if str(lights[i][0]["image"]) == str(fg):
            lights[i][0]["image"] = newFG
        else:
            lights[i][0]["image"] = newBG
    bg = newBG
    fg = newFG

def generateColor(color):
    size=30
    center = size/2
    img = Image.new("RGB", (size, size), "#FFFFFF")
    output = ImageDraw.Draw(img)
    color = color.replace("#",'')
    if len(color) == 6:
        r, g, b = color[0:2], color[2:4], color[4:6]
    else:
        r, g, b = color[0], color[1], color[2]
    dr = int(r, 16)
    dg = int(g, 16)
    db = int(b, 16)
    r, g, b = 255,255,255
    def distance(a,b,x,y):
        return math.sqrt( pow(x-a,2) + pow(y-b,2) )
    #use the distance formula for a multiplier
    for x in range(size):
        for y in range(size):
            r, g, b = 255,255,255
            ratio = 1.0/distance(0,0,center,center)
            d = distance(center, center, x, y)*ratio
            d = .00001 if d == 0 else d
            r,g,b = int((dr*d) * 2), int((dg*d) * 2), int((db*d) * 2)
            output.line( (x, y, x+10, y+10), fill=(r,g,b) )
    img.save("out.png", "PNG")
#this gives a cool square radial gradient            
#    for radius in range(141, 0, -1):
#        r,g,b = r-dr, g-dg, b-db
#        print r,g,b
#        for x in range(radius):
#            for y in range(radius):
#                #color by quarter
#                output.line((100,100,100-x,100-y),fill=(r,g,b) )
#                output.line((100,100,100-x,100+y),fill=(r,g,b) )
#                output.line((100,100,100+x,100-y),fill=(r,g,b) )
#                output.line((100,100,100+x,100+y),fill=(r,g,b) )
#
    
#this will change the board size and initialize it
def resize(row, col):
    givenSize.config(text = "Current size:  " + str(col) + "x" + str(row))
    win.pack_forget()
    puzzleFrame.pack_forget()
    puzzle[0].pack_forget()
    del puzzle[0]
    puzzleFrame.pack()
    puzzle[0] = Frame(puzzleFrame)
    puzzle[0].pack()
    init()

#this will make a game board, shuffle it, and set moves to 0
def init():
    count = 0
    global row, size, scrambling
    #put the buttons on the board
    for Row in range(row):
        f = Frame(puzzle[0])
        f.pack(side=TOP)
        for Cell in range(col):
            lights[count] = []
            lights[count].append(Button(f, image=bg))
            lights[count].append(count)
            c = lights[count][1]
            lights[count][0].pack(side = LEFT)
#            lights[count][0]["image"] = bg
#            lights[count][0]["width"] = 1
#            lights[count][0]["height"] = 1
            
            count += 1
    #set the action of the buttons
    for n in range(size):
        lights[n][0].configure(command = lambda n=n: change(n))
    #scramble the board
    scrambling = True
    scramble()
    scrambling = False
    #set the active background of the buttons to the color of the
    #button so that they don't change color when the user hovers the
    #mouse over them
#    for i in range(size):
#        lights[i][0].config(activebackground=lights[i][0]["bg"])

    puzzle[0].pack()
    global moves
    moves = 0
    moveCount.config(text = "Moves:  " + str(moves))

#this will toggle a single cell at the given location
def toggle(cell):
    if lights[cell][0]["image"] == str(bg):
        lights[cell][0]["image"] = fg
    else:
        lights[cell][0]["image"] = bg
    
#this is the function that turns "lights" on or off
#it makes sure that it can toggle the adjacent cells before trying to
def change(cell):
    global row
    toggle(cell)
    #toggle the cell to the left of the current one
    if cell > 0 and cell%col != 0:
        toggle(cell - 1)
    #toggle the cell to the right of the current one
    if cell < size and cell%col != col-1:
        toggle(cell + 1)
    #toggle the cell above the current one
    if cell >= col:
        toggle(cell - col)
    #toggle the cell below the current one
    if cell < (size - col):
        toggle(cell + col)
    
    #reset the mouseover color of the buttons
#    for i in range(size):
#        lights[i][0].config(activebackground=lights[i][0]["bg"])
    
    #increment the move count and display the number of moves
    global moves
    moves += 1
    moveCount.config(text = "Moves:  " + str(moves))

    #set won to True, and if there any lights on, set it to false
    won = True
    if scrambling:
        won = False
    for i in range(size):
        if lights[i][0]["image"] == str(fg):
            won = False
    #if no lights are on, display a message to the user that they won
    if won:
        win.pack(side=BOTTOM)
        updateHighScores()

#scramble the board
def scramble():
    global size
    if size > 0:
        for i in range(random.randint(10,(row*row) + 10)):
            r = random.randint(0,size-1)
            change(r)
    win.pack_forget()

    
#set up the main frame
root = Tk()
root.title("Lights Out")

bg = PhotoImage(file="dark.png")
fg = PhotoImage(file="blue.png")

#menu
menuFrame = Frame(root, relief = RAISED, bd = 2)
menuFrame.pack(side=TOP, fill=X)
fileMenu = Menubutton(menuFrame, text = "File", underline = 0)
fileMenu.pack(side=LEFT, fill = X)
menu = Menu(fileMenu)
menu.add_command(label = 'New game', command = newGame, underline = 0)
menu.add_command(label = 'High scores', command = showHighScores, underline=0)
menu.add_command(label = 'Settings', command = showSettings, underline=0)
menu.add_command(label = 'Quit', command = quit, underline = 0)
fileMenu['menu'] = menu

#initialize the rest of the top level frames
mainFrame = Frame(root)
mainFrame.pack(side=LEFT)
headerFrame = Frame(mainFrame)
messagesFrame = Frame(mainFrame)
newGameFrame = Frame(mainFrame)
puzzleFrame = Frame(mainFrame)

#header
headerFrame.pack(side=TOP)
head = Label(headerFrame, text="Lights Out")
head.pack(side=TOP)

#messages
messagesFrame.pack(side=TOP)
win = Label(messagesFrame, text = "You Won!")
moveCount = Label(messagesFrame, text = "Moves:  ")
givenSize = Label(messagesFrame, text = "Current size: 5x5")
moveCount.pack()
givenSize.pack()

#the actual puzzle
puzzleFrame.pack(side=TOP)
puzzle = {}
puzzle[0] = Frame(mainFrame)

#a frame to hold the options
settingsFrame = Frame(root)
showSettings()

#frames for the settings
colorFrame = Frame(settingsFrame)
bgColorFrame = Frame(settingsFrame)
fgColorFrame = Frame(settingsFrame)
rowFrame = Frame(settingsFrame)
colFrame = Frame(settingsFrame)
gradientFrame = Frame(settingsFrame)
submitFrame = Frame(settingsFrame)

#settings
bgColorLabel = Label(bgColorFrame, text = "Enter a background gradient color")
bgColorInput = Entry(bgColorFrame, bd=5, width = 7)
bgColorInput.bind("<Return>", updateSettings)

fgColorLabel = Label(fgColorFrame, text = "Enter a foreground gradient color")
fgColorInput = Entry(fgColorFrame, bd=5, width = 7)
fgColorInput.bind("<Return>", updateSettings)

rowLabel = Label(rowFrame, text = "Enter a new row size")
rowInput = Entry(rowFrame, bd=5, width = 5)
rowInput.bind("<Return>", updateSettings)

colLabel = Label(colFrame, text = "Enter a new column size")
colInput = Entry(colFrame, bd=5, width = 5)
colInput.bind("<Return>", updateSettings)

gradientButton=Button(gradientFrame,text="Turn Gradient Off",bg="#999",command=lambda:toggleGradient())


colorFrame.pack(side = TOP)
bgColorFrame.pack(side = TOP)
fgColorFrame.pack(side = TOP)
rowFrame.pack(side = TOP)
colFrame.pack(side = TOP)
gradientFrame.pack(side = TOP)
submitFrame.pack(side = TOP)

bgColorLabel.pack(side=LEFT)
bgColorInput.pack(side=LEFT)
fgColorLabel.pack(side=LEFT)
fgColorInput.pack(side=LEFT)

rowLabel.pack(side = LEFT)
rowInput.pack(side = LEFT)
colLabel.pack(side = LEFT)
colInput.pack(side = LEFT)
gradientButton.pack(side=TOP)

chase = Button(submitFrame, text ="Chase", command = chase)
submit = Button(submitFrame, text ="Apply", command = updateSettings)
cancel = Button(submitFrame, text ="Cancel", command = hideSettings)

#the following line is for a button that will automate the
#"chase" strategy. It will solve everything down to the
#bottom row. To disable this feature, comment out the
#following line.
chase.pack(side=LEFT)
submit.pack(side=LEFT)
cancel.pack(side=RIGHT)
settingsFrame.pack_forget()

#so it begins
def main():
    try:
        text = open('highscores.txt', 'r')
        text.close()
    except:
        text = open('highscores.txt', 'w+')
        text.close()
    init()
    root.mainloop()


if __name__ == '__main__': main()
