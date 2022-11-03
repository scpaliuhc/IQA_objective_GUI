import sys
from windows import *
from ui import *


if __name__=="__main__":
    app=QtWidgets.QApplication(sys.argv)
    ui=UI()
    window=ObWindow(ui)
    window.show()
    window.resize(1000,700)
    y=QDesktopWidget().availableGeometry().center().y()-350
    window.move(200,y)
    window.load_breakpoints()
    sys.exit(app.exec_())
