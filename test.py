import win32gui
import win32con
import win32api

kor_notepad = "제목 없음 - Windows 메모장"
eng_notepad = "Untitled - Notepad"

hwnd = win32gui.FindWindow(None, kor_notepad)

if hwnd == 0:
    hwnd = win32gui.FindWindow(None, "*"+kor_notepad)

if hwnd != 0:
    edit = win32gui.GetDlgItem(hwnd, 0xF)

    win32api.SendMessage(edit, win32con.WM_CHAR, ord('H'), 0)
    win32api.Sleep(100)
    win32api.SendMessage(edit, win32con.WM_CHAR, ord('e'), 0)
    win32api.Sleep(100)
    win32api.SendMessage(edit, win32con.WM_CHAR, ord('l'), 0)
    win32api.Sleep(100)
    win32api.SendMessage(edit, win32con.WM_CHAR, ord('l'), 0)
    win32api.Sleep(100)
    win32api.SendMessage(edit, win32con.WM_CHAR, ord('o'), 0)
    win32api.Sleep(100)
else:
    print("메모장을 찾지 못했습니다.")