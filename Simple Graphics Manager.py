import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit
from PyQt5.QtWidgets import QLabel, QLCDNumber, QCheckBox, QMainWindow
from PyQt5.QtWidgets import QSizePolicy, QSlider, QDialog, QComboBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

MWX, MWY = 300, 300
MWWIDTH, MWHIGHT = 600, 150
CREATE_BUTT_WIDTH, CREATE_BUTT_HIGHT = 100, 40
ADD_BUTT_XDIST, ADD_BUTT_YDIST = 100, 25
NEW_FUNC_HEIGHT = 41
FUNC_NUMBER = 15
CWX, CWY = 800, 500
CWWIDTH, CWHIGHT = 200, 200
COLOR_SQUARE_SIZE = 80


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setGeometry(MWX, MWY, MWWIDTH, MWHIGHT)
        self.setFixedSize(MWWIDTH, MWHIGHT)
        self.setWindowTitle('Главная панель')
        self.noPlot = True

        self.CreateButton = QPushButton('Создать', self)
        self.CreateButton.resize(CREATE_BUTT_WIDTH, CREATE_BUTT_HIGHT)
        self.CreateButton.move(MWWIDTH - 10 - CREATE_BUTT_WIDTH, 10)
        self.CreateButton.clicked.connect(self.create)

        self.AddButton = QPushButton('Добавить', self)
        self.AddButton.resize(ADD_BUTT_XDIST, ADD_BUTT_YDIST)
        self.AddButton.move(MWWIDTH - 50 - ADD_BUTT_XDIST, MWHIGHT - 10 - ADD_BUTT_YDIST)
        self.AddButton.clicked.connect(self.addNewFunction)

        self.Graphic = MplCanvas(self, width=5, height=5)
        self.Graphic.move(MWWIDTH + 60, 10)

        self.saveButton = QPushButton('Save', self)
        self.saveButton.move(2 * MWWIDTH - 140, 5 * MWHIGHT - 85)
        self.saveButton.clicked.connect(self.saveMe)

        self.Title = QLineEdit(self)
        self.Title.resize(500, 20)
        self.Title.move(MWWIDTH + 60, 515)
        self.xTitle = QLineEdit(self)
        self.xTitle.resize(220, 20)
        self.xTitle.move(MWWIDTH + 90, 540)
        self.yTitle = QLineEdit(self)
        self.yTitle.resize(220, 20)
        self.yTitle.move(MWWIDTH + 340, 540)
        self.xtit, self.ytit = QLabel(self), QLabel(self)
        self.xtit.move(MWWIDTH + 65, 540)
        self.xtit.resize(30, 20)
        self.ytit.move(MWWIDTH + 315, 540)
        self.ytit.resize(30, 20)
        self.xtit.setText('Ox:')
        self.ytit.setText('Oy:')

        self.Title.textChanged.connect(self.titling)
        self.xTitle.textChanged.connect(self.titling)
        self.yTitle.textChanged.connect(self.titling)

        self.setGrid = QCheckBox('', self)
        self.setGrid.move(MWWIDTH + 547, 590)
        self.setGrid.stateChanged.connect(self.titling)
        self.setGrid.setCheckState(2)
        self.grider = QLabel(self)
        self.grider.move(MWWIDTH + 525, 594)
        self.grider.resize(20, 20)
        self.grider.setText('Grid')

        self.setCompr = QCheckBox(self)
        self.setCompr.move(MWWIDTH + 497, 594)
        self.setCompr.resize(15, 20)
        self.setCompr.stateChanged.connect(self.titling)
        self.setCompr.setCheckState(2)
        self.compress = QLabel(self)
        self.compress.move(MWWIDTH + 425, 594)
        self.compress.resize(70, 20)
        self.compress.setText('Autocompress')

        self.GraphExistList = [self.Graphic, self.saveButton, self.Title,
                               self.xTitle, self.yTitle, self.setGrid,
                               self.grider, self.compress, self.setCompr,
                               self.xtit, self.ytit]
        for i in self.GraphExistList:
            i.hide()

        self.functions = []
        
        for i in range(FUNC_NUMBER):
            self.NulFunction = NewFunction(self, len(self.functions))
            self.functions.append(self.NulFunction)
            if i:
                self.NulFunction.hide()

        self.CustomizeW = CustomizeWindow(self)
        

    def create(self):
        global MWWIDTH, MWHIGHT
        for i in self.functions.copy():
            if i.alive:
                if not(i.newfunc.text().strip()):
                    i.delete()
        self.noPlot = False
        MWWIDTH, MWHIGHT = 1200, 130 + NEW_FUNC_HEIGHT * (FUNC_NUMBER - 1)
        self.resize(MWWIDTH, MWHIGHT)
        self.setFixedSize(MWWIDTH, MWHIGHT)
        self.AddButton.move(450, MWHIGHT - 10 - ADD_BUTT_YDIST)
        self.Graphic.ax.clear()
        for i in self.GraphExistList:
            i.show()
        self.Graphic.plt.grid(True)
        if not(len(list(filter(lambda x: x.alive, self.functions)))):
            self.addNewFunction()
        else:
            for i in list(filter(lambda x: x.alive, self.functions)):
                i.drawFuncGraph()
        self.titling()
        self.CustomizeW.hide()
        
                
        
    def addNewFunction(self):
        global MWHIGHT
        nf = len(list(filter(lambda x: x.alive, self.functions)))
        if nf < FUNC_NUMBER:
            if nf < FUNC_NUMBER - 1:
                if self.noPlot:
                    MWHIGHT +=  NEW_FUNC_HEIGHT
                    self.resize(MWWIDTH, MWHIGHT)
                    self.setFixedSize(MWWIDTH, MWHIGHT)
                self.AddButton.move(450, MWHIGHT - 10 - ADD_BUTT_YDIST)
            else:
                self.AddButton.hide()
                
            nf = self.functions[nf]
            for i in nf.widgets:
                i.show()
            nf.alive = True
            nf.remove(self.functions.index(nf))

    def titling(self):
        self.Graphic.ax.set_title(self.Title.text())
        self.Graphic.ax.set_xlabel(self.xTitle.text())
        self.Graphic.ax.set_ylabel(self.yTitle.text())
        self.Graphic.plt.grid(self.setGrid.checkState())
        self.Graphic.draw()

    def saveMe(self):
        filen = QFileDialog.getSaveFileName(self, "Сохранить файл", '', 'PNG изображение(*.png);;JPEG изображение(*.jpg;*.jpeg)')[0]
        
        self.Graphic.plt.savefig(filen)


class CustomizeWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.qp = QPainter()
        self.initUI()

    def initUI(self):
        self.F = None
        self.setGeometry(CWX, CWY, CWWIDTH, CWHIGHT)
        
        self.OkButton = QPushButton('Ok', self)
        self.OkButton.move(CWWIDTH - 35, CWHIGHT - 25)
        self.OkButton.resize(30, 20)
        self.OkButton.clicked.connect(self.apply)

        self.rSlider = QSlider(True, self)
        self.rSlider.setGeometry(CWWIDTH - COLOR_SQUARE_SIZE - 10 + 8,
                                 COLOR_SQUARE_SIZE + 20,
                                 COLOR_SQUARE_SIZE - 4, 5)
        self.rlabel = QLabel(self)
        self.rlabel.setText('Red')
        self.rlabel.move(CWWIDTH - COLOR_SQUARE_SIZE - 10 - 14,
                         COLOR_SQUARE_SIZE + 15)
        self.gSlider = QSlider(True, self)
        self.gSlider.setGeometry(CWWIDTH - COLOR_SQUARE_SIZE - 10 + 8,
                                 COLOR_SQUARE_SIZE + 37,
                                 COLOR_SQUARE_SIZE - 4, 5)
        self.glabel = QLabel(self)
        self.glabel.setText('Green')
        self.glabel.move(CWWIDTH - COLOR_SQUARE_SIZE - 10 - 24,
                         COLOR_SQUARE_SIZE + 32)
        self.bSlider = QSlider(True, self)
        self.bSlider.setGeometry(CWWIDTH - COLOR_SQUARE_SIZE - 10 + 8,
                                 COLOR_SQUARE_SIZE + 54,
                                 COLOR_SQUARE_SIZE - 4, 5)
        self.blabel = QLabel(self)
        self.blabel.setText('Blue')
        self.blabel.move(CWWIDTH - COLOR_SQUARE_SIZE - 10 - 15,
                         COLOR_SQUARE_SIZE + 48)

        self.aSlider = QSlider(True, self)
        self.aSlider.setValue(100)
        self.aSlider.setGeometry(CWWIDTH - COLOR_SQUARE_SIZE - 10 + 8,
                                 COLOR_SQUARE_SIZE + 71,
                                 COLOR_SQUARE_SIZE - 4, 5)
        self.alabel = QLabel(self)
        self.alabel.setText('Opacity')
        self.alabel.move(CWWIDTH - COLOR_SQUARE_SIZE - 10 - 32,
                         COLOR_SQUARE_SIZE + 65)
        
        self.rSlider.valueChanged.connect(self.changeColor)
        self.gSlider.valueChanged.connect(self.changeColor)
        self.bSlider.valueChanged.connect(self.changeColor)
        self.aSlider.valueChanged.connect(self.changeColor)

        self.setTyper = QComboBox(self)
        self.setTyper.move(10, 10)
        self.setTyper.addItems(TYPES.keys())
        self.setTyper.currentIndexChanged.connect(self.typesetting)

        self.XfromY = QCheckBox('x(y)', self)
        self.XfromY.move(10, 40)
        self.XfromY.stateChanged.connect(self.xfy)

        self.x1Setter = QLineEdit(self)
        self.x1Setter.move(25, 65)
        self.x1Setter.resize(30, 15)

        self.x2Setter = QLineEdit(self)
        self.x2Setter.move(60, 65)
        self.x2Setter.resize(30, 15)

        self.xSetter = QLabel(self)
        self.xSetter.move(10, 65)
        self.xSetter.resize(15, 15)
        self.xSetter.setText('x∈')
        self.x12Setter = QLabel(self)
        self.x12Setter.move(56, 65)
        self.x12Setter.resize(5, 15)
        self.x12Setter.setText(';')

        self.levButton = QPushButton('1000', self)
        self.levButton.move(45, 85)
        self.levButton.resize(45, 20)
        self.levButton.clicked.connect(self.accuracity)
        self.levLabel = QLabel(self)
        self.levLabel.move(10, 85)
        self.levLabel.resize(40, 16)
        self.levLabel.setText('Точно:')

    def serve(self, Function):
        self.F = Function
        self.rSlider.setValue(round(self.F.color[0] * 100 / 256))
        self.gSlider.setValue(round(self.F.color[1] * 100 / 256))
        self.bSlider.setValue(round(self.F.color[2] * 100 / 256))
        self.aSlider.setValue(round(self.F.color[3] * 100))
        self.XfromY.setCheckState(self.F.XfromY)
        self.x1Setter.setText(str(self.F.x1).rstrip('0'*('.' in
                                                         str(self.F.x1))).rstrip('.'))
        self.setTyper.setCurrentIndex(self.setTyper.findText(self.F.type))
        self.x2Setter.setText(str(self.F.x2).rstrip('0'*('.' in
                                                         str(self.F.x2))).rstrip('.'))
        self.setTyper.setCurrentIndex(self.setTyper.findText(self.F.type))
        if self.F.type == 'линия':
            self.levButton.setText(str(self.F.lev))
        elif self.F.type == 'точки' or self.F.type == 'диаграмма':
            self.levButton.setText(str(self.F.dot_lev))
        self.setWindowTitle(Function.newfuncName.text().rstrip(' = '))

    def typesetting(self, s):
        if list(TYPES.keys())[s] == 'линия':
            self.levButton.setText(str(self.F.lev))
        elif (list(TYPES.keys())[s] == 'точки' or
              list(TYPES.keys())[s] == 'диаграмма'):
            self.levButton.setText(str(self.F.dot_lev))
        
    def apply(self):
        self.F.color = (round(self.rSlider.value() * 256 / 100),
                        round(self.gSlider.value() * 256 / 100),
                        round(self.bSlider.value() * 256 / 100),
                        self.aSlider.value() / 100)
        self.F.newfuncCustom.setStyleSheet("""QPushButton { background-color:
                                           rgba(%d, %d, %d, %g)}""" % (self.F.color))
        self.F.type = self.setTyper.currentText()
        self.F.XfromY = self.XfromY.checkState()
        x1 = x2 = 0
        f = True
        try:
            try:
                x2 = float(eval(Evalable(self.x2Setter.text().strip())))
                self.x2Setter.setStyleSheet("QLineEdit { background: white;}")
            except Exception:
                f = False
                self.x2Setter.setStyleSheet("QLineEdit { background: salmon;}")
            x1 = float(eval(Evalable(self.x1Setter.text().strip())))
            self.x1Setter.setStyleSheet("QLineEdit { background: white;}")
        except Exception:
            f = False
            self.x1Setter.setStyleSheet("QLineEdit { background: salmon;}")
        if (x1 > x2 or x1 - x2 > 200000) and f:
            f = False
            self.x1Setter.setStyleSheet("QLineEdit { background: salmon;}")
            self.x2Setter.setStyleSheet("QLineEdit { background: salmon;}")
        if f:
            self.F.x1 = x1
            self.F.x2 = x2
            
        if self.F.type == 'линия':
            self.F.lev = int(self.levButton.text())
        elif self.F.type == 'точки' or self.F.type == 'диаграмма':
            self.F.dot_lev = float(self.levButton.text())
        
        self.hide()

    def changeColor(self):
        self.update()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.showColor(qp)
        qp.end()

    def showColor(self, qp):
        qcol = QColor(round(self.rSlider.value() * 256 / 100),
                      round(self.gSlider.value() * 256 / 100),
                      round(self.bSlider.value() * 256 / 100))
        qcol.setAlpha(round(self.aSlider.value() * 256 / 100))
        qp.setBrush(qcol)
        qp.drawRect(CWWIDTH - COLOR_SQUARE_SIZE - 10, 10, COLOR_SQUARE_SIZE,
                    COLOR_SQUARE_SIZE)

    def xfy(self, state):
        if state:
            self.F.newfuncName.setText(self.F.newfuncName.text().replace('x', 'y'))
            self.xSetter.setText('y∈')
        else:
            self.F.newfuncName.setText(self.F.newfuncName.text().replace('y', 'x'))
            self.xSetter.setText('x∈')
        self.setWindowTitle(self.F.newfuncName.text().rstrip(' = '))

    def accuracity(self):
        if self.setTyper.currentText() == 'линия':
            levels = self.F.plot_levels
            lev = self.F.lev
        elif (self.setTyper.currentText() == 'точки'or
              self.setTyper.currentText() == 'диаграмма'):
            levels = self.F.dot_levels
            lev = self.F.dot_lev
        b = list(filter(lambda x: (self.F.x2 - self.F.x1) * x <= 2000000,
                        levels))
        a = levels.index(lev)
        if a >= len(b):
            a = len(b) - 1
        else:
            a = (a + 1) % len(b)
        self.levButton.setText(str(levels[a]))
        if self.setTyper.currentText() == 'линия':
            self.F.lev = int(self.levButton.text())
        elif (self.setTyper.currentText() == 'точки'or
              self.setTyper.currentText() == 'диаграмма'):
            self.F.dot_lev = float(self.levButton.text())
            


class NewFunction():
    def __init__(self, selfWindow, num):
        self.num = num
        self.sW = selfWindow
        self.alive = True
        self.visible = True
        
        self.newfuncName = QLabel(self.sW)
        self.newfuncName.setText(str(f"f{self.num}(x) = "))
        
        self.newfunc = QLineEdit(self.sW)
        self.newfunc.resize(MWWIDTH - 70 - CREATE_BUTT_WIDTH - 40, 22)

        self.newfuncDeleter = QPushButton('🞪', self.sW)
        self.newfuncDeleter.resize(14, 15)
        self.newfuncDeleter.clicked.connect(self.delete)

        self.newfuncCustom = QPushButton('', self.sW)
        self.newfuncCustom.resize(22, 22)
        self.newfuncCustom.setStyleSheet("QPushButton { background-color: rgb(0, 0, 0)}")
        self.newfuncCustom.clicked.connect(self.customize)

        self.newfuncVisible = QCheckBox(self.sW)
        self.newfuncVisible.resize(15, 32)
        self.newfuncVisible.setChecked(True)
        self.newfuncVisible.stateChanged.connect(self.view)

        self.widgets = (self.newfuncDeleter,
                        self.newfuncName,
                        self.newfunc,
                        self.newfuncCustom,
                        self.newfuncVisible)
        
        self.plot_levels = [10, 100, 1000, 5000, 10000]
        self.dot_levels = [0.01, 0.1, 1, 10, 100]
        
        self.default()

        self.remove(self.num)


    def hide(self):
        for i in range(len(self.widgets)):
            if self.sW.functions.index(self) or i:
                self.widgets[i].hide()
        self.newfunc.clear()

        lastIndex = self.sW.functions.index(self)
        self.alive = False
        self.sW.functions.sort(key=lambda x: not(x.alive))
        for i in range(lastIndex, FUNC_NUMBER):
            if self.sW.functions[i].alive:
                self.sW.functions[i].remove(i)
            else:
                self.sW.functions[i:] = sorted(self.sW.functions[i:], key=lambda x: x.num)
                break

    def delete(self):
        global MWHIGHT
        self.hide()
        if len(list(filter(lambda x: x.alive == False, self.sW.functions))) == 1:
            self.sW.AddButton.show()
        else:
            if self.sW.noPlot:
                MWHIGHT -= NEW_FUNC_HEIGHT
                self.sW.AddButton.move(MWWIDTH - 50 - ADD_BUTT_XDIST,
                                       MWHIGHT - 10 - ADD_BUTT_YDIST)
        self.sW.resize(MWWIDTH, MWHIGHT)
        self.sW.setFixedSize(MWWIDTH, MWHIGHT)
        self.default()
        
    def remove(self, num):
        self.localX = 10
        self.localY = ADD_BUTT_YDIST + 24 + NEW_FUNC_HEIGHT * num
        self.newfuncName.move(self.localX + 19, self.localY - 9)
        self.newfunc.move(self.localX + 59, self.localY - 4)
        self.newfuncCustom.move(self.localX + 453, self.localY - 4)
        self.newfuncDeleter.move(self.localX + 476, self.localY - 13)
        self.newfuncVisible.move(self.localX, self.localY - 8)
        if num == 0:
            self.newfuncDeleter.hide()
        elif self.alive:
            self.newfuncDeleter.show()

    def view(self):
        self.visible = not(self.visible)

    def customize(self):
        self.sW.CustomizeW.show()
        self.sW.CustomizeW.serve(self)

    def drawFuncGraph(self):
        if self.visible:
            try:
                function_body = Evalable(self.newfunc.text().strip(), [self.num],
                                         self.sW)
                if self.type == 'линия':
                    curlev = self.lev
                elif self.type == 'точки' or self.type == 'диаграмма':
                    curlev = self.dot_lev
                x = np.arange(self.x1, self.x2, 1 / curlev)
                y = eval(function_body)
                if function_body.count('x') == function_body.count('exp'):
                    y = np.array([y for i in range(x.size)])
                if self.XfromY:
                    x, y = y, x
                if self.type == 'линия':
                    self.sW.Graphic.plt.plot(x, y,
                                             color=tuple(map(lambda x: x / 255,
                                                             self.color[:3])),
                                         alpha=self.color[3],
                                         linewidth=self.plot_width,
                                         linestyle=self.plot_style)
                elif self.type == 'точки':
                    self.sW.Graphic.plt.scatter(x, y,
                                             color=tuple(map(lambda x: x / 255,
                                                             self.color[:3])),
                                                         alpha=self.color[3])
                elif self.type == 'диаграмма':
                    self.sW.Graphic.plt.bar(x, y,
                                             color=tuple(map(lambda x: x / 255,
                                                             self.color[:3])),
                                                         alpha=self.color[3],
                                                                width=self.barwidth)
                                     
                self.newfunc.setStyleSheet("QLineEdit"
                                "{"
                                "background : white;"
                                "}")
            except Exception:
                self.newfunc.setStyleSheet("QLineEdit"
                                "{"
                                "background : salmon;"
                                "}")
        if not(self.sW.setCompr.checkState()):
            self.sW.Graphic.ax.set_xlim(self.sW.Graphic.x1_lim,
                                     self.sW.Graphic.x2_lim)
            self.sW.Graphic.ax.set_ylim(self.sW.Graphic.y1_lim,
                                     self.sW.Graphic.y2_lim)
            self.sW.Graphic.plt.plot(self.sW.Graphic.x1_lim,
                                             self.sW.Graphic.y2_lim)
            self.sW.Graphic.plt.plot(self.sW.Graphic.x1_lim,
                                     self.sW.Graphic.y1_lim)
            self.sW.Graphic.plt.plot(self.sW.Graphic.x2_lim,
                                     self.sW.Graphic.y1_lim)
        self.sW.Graphic.plt.draw()

    def default(self):
        self.x1, self.x2, self.lev = -15, 15, 1000
        self.dot_lev = 1
        self.color = (0, 0, 0, 1)
        self.newfuncVisible.setChecked(True)
        self.visible = self.newfuncVisible.checkState()
        self.plot_width = 1
        self.plot_style = 'solid'
        self.type = 'линия'
        self.dot_width = 2
        self.dot_style = 'o'
        self.barwidth = 1
        self.newfuncCustom.setStyleSheet("""QPushButton { background-color:
                                         rgba(%d, %d,
                                         %d, %g)}""" % (self.color))
        self.newfunc.setStyleSheet("QLineEdit"
                                "{"
                                "background : white;"
                                "}")
        self.XfromY = False


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, polar=False):
        self.plt = plt
        self.fig = self.plt.figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.ax = self.figure.add_axes([0.16, 0.1, 0.8, 0.8])
        self.x1_lim, self.x2_lim, self.y1_lim, self.y2_lim = (-15, 15,
                                                              -15, 15)
        self.plt.grid(True)
        

def Evalable(s, funcs=[], outW=None, prime=True):
    if outW:
        outfuncSort = sorted(outW.functions,
                             key=lambda x: int(x.newfuncName.text().lstrip('f').rstrip('(x) = ').rstrip('(y) = ')))
    for i in range(FUNC_NUMBER - 1):
        if ('f' + str(i)) in s and i != funcs[-1]:
            if len(s) - s.index('f' + str(i)) - len(str(i)) - 1:
                if s[s.index(('f' + str(i))) + len(str(i)) + 1].isdigit():
                    continue
            if i in funcs:
                return '(0/0)'
            if outfuncSort[i].alive:
                for fs in range(s.count('f' + str(i))):
                    fcs = funcs.copy()
                    fcs.append(i)
                    s = s.replace('f' + str(i), f"({Evalable(outfuncSort[i].newfunc.text().strip(), fcs, outW, False)})")
            else:
                return '(0/0)'
    if prime:
        for i in HOH.keys():
            s = s.replace(i, HOH[i])
    return s


HOH = dict()
HOH['arcsin'], HOH['arccos'], HOH['arctan'], HOH['exp'] = 'si_in', 'co_os', 'ta_an', 'aksp'
for i in ['sin', 'cos', 'tan', 'pi', 'e', 'log', 'sqrt']:
    HOH[i] = 'np.' + i
HOH['si_in'], HOH['co_os'], HOH['ta_an'], HOH['aksp'] = 'np.arcsin', 'np.arccos', 'np.arctan', 'np.exp'
HOH['lg'] = 'np.log10'
HOH['^'] = '**'
HOH[','] = '.'

TYPES = {}
TYPES['линия'] = ['толщина', 'стиль']
TYPES['точки'] = ['толщина', 'стиль', 'лин/точ']
TYPES['диаграмма'] = ['толщина', 'стиль']


if __name__ == '__main__':
    app = QApplication(sys.argv)
    Mw = MainWindow()
    Mw.show()
    sys.exit(app.exec())
