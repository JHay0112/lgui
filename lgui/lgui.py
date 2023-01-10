"""
    Runs the lgui application
"""

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

NAME = "lgui"
GEOM = (100, 100, 800, 800)

if __name__ == '__main__':
   
   app = QApplication(sys.argv)
   w = QWidget()
   w.setGeometry(*GEOM)
   w.setWindowTitle(NAME)

   # TODO, literally everything

   w.show()
   sys.exit(app.exec_())