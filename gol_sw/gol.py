import numpy as np
from PyQt5.QtCore import QDir, Qt, QThread
from PyQt5.QtGui import QImage, QPainter, QPalette, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
        QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
import sys

from PIL import Image

from gol_menu import *


class GoLGame(object):
    history_len = 16

    def __init__(self, initial_state):
        self.state = initial_state.astype(np.uint8)
        self.shape = initial_state.shape

        self.history = [np.zeros_like(self.state) for _ in range(self.history_len)]
        self.color = palette['re']

    @staticmethod
    def GAME_RANDOM(shape, fill):
        Z = np.random.randint(0,100,shape)
        Z[Z > 100 * fill] = 0
        Z[Z >= 1] = 1
        return GoLGame(Z)

    @staticmethod
    def GAME_EMPTY(shape, fill):
        Z = np.zeros(shape, dtype=np.uint8)
        return GoLGame(Z)

    def iterate(self):
        X = np.pad(self.state, ((1,1),(1,1)), mode='constant')
        X1 = np.array(
             (X[0:-2,0:-2] + X[0:-2,1:-1] + X[0:-2,2:] +
              X[1:-1,0:-2]                + X[1:-1,2:] +
              X[2:  ,0:-2] + X[2:  ,1:-1] + X[2:  ,2:]), dtype=np.uint8)

        birth = (X1==3) & (X[1:-1,1:-1]==0)
        survive = ((X1==2) | (X1==3)) & (X[1:-1,1:-1]==1)
        X[...] = 0
        X[1:-1,1:-1][birth | survive] = 1

        self.history.append(self.state)
        if len(self.history) >= self.history_len:
            self.history = self.history[1:]
        self.state = X[1:-1,1:-1].copy()

        return self.state

    def set_color(self, rgba):
        self.color = rgba

    def render(self, target, color=None):
        if color == None:
            color = self.color
        target[:,:,:3][self.state == 1] = color[:3]
        target[:,:,3] = 255


class GoLThread(QThread):
    def __init__(self, gol):
        QThread.__init__(self)
        self.gol = gol
        self.delayms = 1000

    def __del__(self):
        self.wait()

    def run(self):
        while(not self.isInterruptionRequested()):
            self.msleep(self.delayms)
            print("Thread updating image")
            #x = self.game.state
            #print(float(np.sum(x)) / np.product(x.shape))
            #im = self.game.mk_image_simple([0,0,255])
            self.gol.iterate()
            self.gol.display()

palette = {
    're': [255, 0, 0],
    'gr': [0, 255, 0],
    'ye': [255,255,0],
    'wh': [255,255,255],
    'bk': [0, 0, 0],
    'bl': [0, 0, 255],
    'lb':[128, 128, 255]
}
for c in palette.iterkeys():
    palette[c] = np.array(palette[c] + [255], dtype=np.uint8)


class GoLViewer(QMainWindow):
    def __init__(self, gol):
        super(GoLViewer, self).__init__()
        self.imageLabel = QLabel()

        #self.scrollArea = QScrollArea()
        #self.scrollArea.setBackgroundRole(QPalette.Dark)
        #self.scrollArea.setWidget(self.imageLabel)
        #self.setCentralWidget(self.scrollArea)
        self.setCentralWidget(self.imageLabel)
        self.resize(500, 500)

        self.gol = gol

        self.golthread = GoLThread(self.gol)
        self.golthread.start()

    def _np_array_to_qimage(self, arr):
        shape = arr.shape
        im = QImage(arr, shape[1], shape[0], QImage.Format_ARGB32).rgbSwapped()
        im = im.scaledToWidth(600)
        return im

    def update(self, arr):
        shape = arr.shape
        self.imageLabel.setPixmap(QPixmap.fromImage(self._np_array_to_qimage(arr)))
        self.imageLabel.adjustSize()
        img = Image.fromarray(arr[:,:,:3], 'RGB')
        img.save('out.png')

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        elif e.key() == Qt.Key_Up:
            self.gol.menu.go_up()
            self.gol.display()
            print "going up"
        elif e.key() == Qt.Key_Down:
            self.gol.menu.go_down()
            self.gol.display()
            print "going down"
        elif e.key() == Qt.Key_Left:
            pass
        elif e.key() == Qt.Key_Right:
            self.gol.menu.go_right()
        elif e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
            print "enter"
        else:
            print e.key()


class GoL(object):
    def __init__(self):
        self.width = 72 + GoLItem.WIDTH
        self.height = 72

        self.gol_width = self.width - GoLItem.WIDTH
        self.gol_height = self.height

        self.game = GoLGame.GAME_RANDOM((self.gol_height, self.gol_width), 0.5)
        self.ui = GoLViewer(self)
        self.items = [
            GoLColorItem(self, GoLColorItem.COLORSCHEME_BORING),
            GoLStartStopItem(self)
        ]
        self.menu = GoLMenu(self.items)

        self.display()

    def start(self):
        self.ui.show()

    def iterate(self):
        return self.game.iterate()

    def render(self):
        screen = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        screen[:,:,3] = 255
        self.game.render(screen[:,GoLItem.WIDTH:,:])
        self.menu.render(screen[:,:GoLItem.WIDTH,:])
        return screen

    def display(self):
        self.ui.update(self.render())




if __name__ == '__main__':
    app = QApplication(sys.argv)
    g = GoL()
    g.start()

    sys.exit(app.exec_())
