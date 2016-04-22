import numpy as np
import scipy as sp
import scipy.ndimage

from gol import palette

class GoLItem(object):
    HEIGHT = 10
    WIDTH = 10

    def __init__(self, game):
        self.is_selected = False
        self.game = game
        self.icon = np.zeros((self.HEIGHT, self.WIDTH, 4), dtype=np.uint8)
        self.icon[:,:,3] = 255

    def render(self, ptr):
        icon = self.icon
        if icon.shape == (self.HEIGHT, self.WIDTH):
            for i in range(self.HEIGHT):
                for j in range(self.WIDTH):
                    #print ptr[i,j,:]
                    ptr[i,j,:] = palette[icon[i,j]]
                    #print ptr[i,j,:]
        else:
            ptr[:,:,:] = icon

        #f = lambda x: palette[x]
        #v = np.vectorize(f, otypes=[np.dtype("4u1")])
        #v = np.vectorize(f, otypes=[np.ndarray])
        #h = v(self.icon)
        #print(h)
        #ptr[:,:,:] = v(self.icon)

        #print ptr.shape

        #for color in palette.iterkeys():
        #    ptr[self.icon == color] = palette[color]

    def select(self):
        self.is_selected = True
        self._select()

    def _select(self):
        color = palette['wh']
        self.icon[0, :, :] = color
        self.icon[self.HEIGHT - 1:, :, :] = color
        self.icon[:,0,:] = color
        self.icon[:,self.WIDTH - 1,:] = color

    def deselect(self):
        self.is_selected = False
        self._deselect()

    def _deselect(self):
        self.icon[0, :, :3] = 0
        self.icon[self.HEIGHT - 1:, :, :3] = 0
        self.icon[:,0,:3] = 0
        self.icon[:,self.WIDTH - 1,:3] = 0

    def go_right(self):
        pass

    def go_left(self):
        pass

    def input(self, key):
        pass

    @staticmethod
    def _binary_array_color(arr, color):
        icon = np.array([['bl']*self.WIDTH]*self.HEIGHT)



class GoLColorItem(GoLItem):
    COLORSCHEME_BORING = 0

    def __init__(self, game, color):
        super(GoLColorItem, self).__init__(game)
        self.icon = scipy.ndimage.imread('c.png', mode='RGBA')
        self.color_index = 0

    def _select(self):
        super(GoLColorItem, self)._select()


    def _deselect(self):
        super(GoLColorItem, self)._deselect()

    def go_right(self):
        while True:
            self.color_index = (self.color_index + 1) % len(palette)
            if palette.keys()[self.color_index] != 'bk':
                break
        color = palette[palette.keys()[self.color_index]]
        print palette.keys()[self.color_index]
        print color
        self.game.game.set_color(color)
        self.game.display()


class GoLStartStopItem(GoLItem):
    def __init__(self, game):
        super(GoLStartStopItem, self).__init__(game)
        self.on = False
        self.icon = scipy.ndimage.imread('onoff.png', mode='RGBA')


class GoLMenu(object):
    HEIGHT = 6

    def __init__(self, items):
        self.pos = -1
        self.items = items

    def go_up(self):
        new_pos = max(self.pos - 1, 0)
        if new_pos != self.pos:
            self.items[self.pos].deselect()
            self.pos = new_pos
            self.items[new_pos].select()

    def go_down(self):
        new_pos = min(self.pos + 1, len(self.items) - 1)
        if new_pos != self.pos:
            self.items[self.pos].deselect()
            self.pos = new_pos
            self.items[new_pos].select()

    def go_right(self):
        if self.pos >= 0:
            self.items[self.pos].go_right()

    def render(self, ptr):
        for (i, item) in zip(range(len(self.items)), self.items):
            item.render(ptr[i * GoLItem.HEIGHT : (i + 1) * GoLItem.HEIGHT, :])
        #for i in range(self.HEIGHT - i - 1):
        #    ptr[i * 36 : (i + 1) * 36, :, :] = 0
        pass
