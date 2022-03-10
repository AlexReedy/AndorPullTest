import os
import logging
import json
from logging.handlers import TimedRotatingFileHandler
import time
import socket
import threading
import andor
# import paramiko

SITE_ROOT = os.path.abspath(os.path.dirname(__file__)+'/../..')
print(SITE_ROOT)
with open(os.path.join(SITE_ROOT, 'config', 'logging.json')) as data_file:
    params = json.load(data_file)

logger = logging.getLogger("ifu_cameraLogger")
logger.setLevel(logging.DEBUG)
logging.Formatter.converter = time.gmtime
formatter = logging.Formatter("%(asctime)s--%(name)s--%(levelname)s--"
                              "%(module)s--%(funcName)s--%(message)s")

logHandler = TimedRotatingFileHandler(os.path.join(params['abspath'],
                                                   'ifu_camera_server.log'),
                                      when='midnight', utc=True, interval=1,
                                      backupCount=360)
logHandler.setFormatter(formatter)
logHandler.setLevel(logging.DEBUG)
logger.addHandler(logHandler)
logger.info("Starting Logger: Logger file is %s", 'ifu_camera_server.log')


class CamServer:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.socket = ""
        self.cam = None
        print("Starting up cam server on %s port %s" % (self.hostname,
                                                        self.port))

    def handle(self, connection, address):

        if address is not None:
            pass

        while True:
            response = {'test': 'test'}
            try:
                start = time.time()
                data = connection.recv(2048)

                data = data.decode("utf8")
                logger.info("Received: %s", data)
                print(data)

                if not data:
                    break

                try:
                    data = json.loads(data)
                except Exception as e:
                    logger.error("Load error", exc_info=True)
                    error_dict = json.dumps(
                        {'elaptime': time.time()-start,
                         "error": "error message %s" % str(e)})
                    connection.sendall(error_dict)
                    break

                if 'command' in data:

                    if data['command'].upper() == 'INITIALIZE':
                        if not self.cam:
                            if self.port == 53:
                                cam_prefix = "rc"
                                send_to_remote = True
                                output_dir = 'C:/images'
                            else:
                                cam_prefix = "ifu"
                                send_to_remote = True
                                output_dir = 'C:/images'
                            self.cam = andor.Controller(
                                serial_number="", cam_prefix=cam_prefix,
                                send_to_remote=send_to_remote,
                                output_dir=output_dir)

                            ret = self.cam.initialize()
                            if self.port == 6942:
                                # Spare camera SN
                                # self.cam.serialNumber = "2803120001"
                                self.cam.serialNumber = "04001312"
                            else:
                                self.cam.serialNumber = "05313416"
                            if ret:
                                response = {'elaptime': time.time()-start,
                                            'data': "Camera started"}
                            else:
                                response = {'elaptime': time.time()-start,
                                            'error': self.cam.lastError}
                        else:
                            print(self.cam)
                            print(type(self.cam))
                            response = {'elaptime': time.time()-start,
                                        'data': "Camera already intiailzed"}

                    elif data['command'].upper() == 'TAKE_IMAGE':
                        with open("ifu_exposure_start.txt", 'w') as file:
                            file.write(time.strftime('%Y-%m-%d %H:%M:%S.%d',
                                                     time.gmtime()))
                        response = self.cam.take_image(**data['parameters'])
                        print(response)
                    elif data['command'].upper() == 'LOGROLLOVER':
                        logger.removeHandler(logHandler)
                        logHandler.doRollover()
                        logger.addHandler(logHandler)
                        logger.info("New IFU log")
                        print("Log rollover")
                    elif data['command'].upper() == 'STATUS':
                        response = self.cam.get_status()
                    elif data['command'].upper() == 'GETTEMPSTATUS':
                        response = self.cam.get_temp_status()
                        print(response)
                    elif data['command'].upper() == 'PING':
                        response = {'data': 'PONG'}
                    elif data['command'].upper() == 'GETPRESSURE':
                        last_line = open("C:/Users/SEDM-User/Desktop/"
                                         "SEDMv3Robot-master/utilities/"
                                         "chiller.txt").readlines()[-1]
                        response = {'elaptime': time.time() - start,
                                    'data': str(last_line)}
                    elif data['command'].upper() == "LASTERROR":
                        response = self.cam.lastError
                        print(response)
                    elif data['command'].upper() == "LASTEXPOSED":
                        obs_time = open("ifu_exposure_start.txt").readlines()[0]
                        response = {'elaptime': time.time()-start,
                                    'data': str(obs_time)}
                    elif data['command'].upper() == "PREFIX":
                        response = {'elaptime': time.time()-start,
                                    'data': self.cam.camPrefix}
                    elif data['command'].upper() == "REINIT":
                        response = self.cam.opt.disconnect()
                        print(response)
                    elif data['command'].upper() == "SHUTDOWN":
                        _ = self.cam.opt.disconnect()
                        _ = self.cam.opt.unloadLibrary()
                        self.cam = None
                        response = {'elaptime': time.time()-start,
                                    'data': "Camera shutdown"}
                        print(response)
                else:
                    response = {'elaptime': time.time()-start,
                                'error': "Command not found"}

                jsonstr = json.dumps(response)
                connection.sendall(jsonstr.encode('utf-8'))
            except Exception as e:
                print("Camera error:", time.gmtime())
                print(str(e))
                logger.error("Big error", exc_info=True)
                time.sleep(60)

    def start(self):
        logger.debug("IFU server now listening for connections on port:%s" %
                     self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(None)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(5)

        while True:
            conn, address = self.socket.accept()
            logger.debug("Got connection from %s:%s" % (conn, address))
            new_thread = threading.Thread(target=self.handle, args=(conn,
                                                                    address))
            new_thread.start()
            logger.debug("Started process")


if __name__ == "__main__":
    server = CamServer("127.0.0.1", 6942)
    # try:
    logger.info("Starting IFU Server")
    # server.cam = pixis.Controller(serial_number="", cam_prefix="ifu",
    #                               send_to_remote=True, output_dir="C:/images")
    # server.cam.initialize()
    # server.cam.serialNumber = "05313416"
    server.start()
    # except Exception as e:
    #    print(str(e))
    #    logging.exception("Unexpected exception %s", str(e))
    # finally:
    #    logging.info("Shutting down IFU server")
    logger.info("All done")
