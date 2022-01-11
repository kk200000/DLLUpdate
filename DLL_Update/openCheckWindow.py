# coding:gbk
import DLL_Update.app as app



def click():
    print('test deal')


check_win = app.check_win
check_win.webview.bind_function("clickMe", click())


