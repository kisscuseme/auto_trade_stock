baseInterval = 'day'

isRunning = True
sendLogEnabled = True

def get_send_log_enabled():
    return sendLogEnabled

def set_send_log_enabled(flag):
    global sendLogEnabled
    sendLogEnabled = flag

def get_running():
    return isRunning

def set_running(flag):
    global isRunning
    isRunning = flag
