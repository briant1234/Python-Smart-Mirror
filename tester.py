# sierpinksy-triangle.py

from tkinter import *

def init(data):
    data.level = 1

def drawSierpinskyTriangle(canvas, x, y, size, level):
    # (x,y) is the lower-left corner of the triangle
    # size is the length of a side
    if (level == 0):
        canvas.create_polygon(x, y,
                              x+size, y,
                              x+size/2, y-size*(3**0.5)/2,
                              fill="black")
    else:
        drawSierpinskyTriangle(canvas, x, y, size/2, level-1)
        drawSierpinskyTriangle(canvas, x+size/2, y, size/2, level-1)
        drawSierpinskyTriangle(canvas, x+size/4, y-size*(3**0.5)/4, size/2, level-1)

def keyPressed(event, data):
    if (event.keysym in ["Up", "Right"]):
        data.level += 1
    elif ((event.keysym in ["Down", "Left"]) and (data.level > 0)):
        data.level -= 1

def redrawAll(canvas, data):
    drawSierpinskyTriangle(canvas, 25, 450, 450, data.level)
    canvas.create_text(250, 25,
                       text = "Level %d Sierpinsky Triangle" % (data.level),
                       font = "Arial 26 bold")
    canvas.create_text(250, 50,
                       text = "Use arrows to change level",
                       font = "Arial 10")

def mousePressed(event, data): pass

def timerFired(data): pass

####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(500, 500)