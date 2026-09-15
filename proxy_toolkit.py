from __future__ import absolute_import, division, print_function


import re
import traceback
from urllib.parse import urlparse
import os
from datetime import datetime
from builtins import *

import sys
import json
from http.server import BaseHTTPRequestHandler
from io import StringIO
import os
import ColorizePython
import mimetypes
import time


import thesmuggler



shared_bin_file_for_task_1 = 't1_bin'
shared_bin_file_for_task_3 = 't3_bin'

def serialize_binary_data(input):
    return json.dumps(input.decode("latin1"))


def deserialize_binary_data(input):
    return json.loads(input.encode("latin1")).encode()


def log_socket_tx(input, data=None, file_name="socket_logs_localized"):
    try:

        with open(f"./{file_name}.txt", "a") as f:


            f.write(f"{input} ")


            if data is not None:
                f.write(f"({len(data)}) bytes\n")
                f.write("\n")

                f.write(f"{data}")

                f.write("\n")

            f.write("\n")
    except:

        print("ERROR when logging")
        traceback.print_exc()



def process_request(request, blacklist_domains=[], verbose=True):

    try:
        allowed_connection = True
        healthy_proccess = False
        full_url = ''
        first_line = ''
        method = ''
        port = -1
        domain = ''
        headers = ''

        verbose_prefix = 'process_request'


        # get string
        request_string = request.decode()

        if verbose: print(f"\t\t{verbose_prefix}- {request}")

        # get the url
        lines = request_string.split('\n')
        first_line = lines[0]  # parse the first line
        first_line_parts = first_line.split(' ')
        method = first_line_parts[0]
        full_url = first_line_parts[1]
        protocol = first_line_parts[2]



        # BLACK LIST
        for i in range(0, len(blacklist_domains)):
            if blacklist_domains[i] in full_url:
                allowed_connection=False
                break



        """
        parniatech.com:443
        http://parniatech.com/
        206.81.14.87:22
        """

        is_port_mentioned_in_full_url = (':' in full_url) and ('://' not in full_url)

        if is_port_mentioned_in_full_url:
            domain, port = full_url.split(":")
            port = int(port)
        else:
            domain, port = full_url, 80

        if 'http://' in domain:
            domain = domain.replace("http://", '')

        if 'https://' in domain:
            domain = domain.replace("https://", '')

        domain = domain.replace('/', '')


        headers = {}
        # get the headers
        for i in range(1, len(lines)):
            line = lines[i]
            if len(line) > 0:
                parts = line.split(':')
                if len(parts) > 1:
                    left_side = parts[0].strip()
                    right_side = parts[1].strip()
                    if left_side.upper() not in (["CONNECT", "GET", "POST", "HOST"]):
                        headers[left_side] = right_side





    except:
        print("ERROR can not process the request")
        traceback.print_exc()


    else:
        healthy_proccess=True

    finally:

        return {
            "healthy_proccess": healthy_proccess,
            "allowed_connection": allowed_connection,
            # "first_line": first_line,
            "method": method,
            "port": port,
            "domain": domain,
            # "headers": headers
        }

def recvall(sock, chunk_size, timeout):

    # try:
    sock.settimeout(timeout)

    t1 = time.time()
    data = bytearray()
    while True:
        part = sock.recv(chunk_size)
        data.extend(part)
        if len(part) < chunk_size:
            # either 0 or end of data
            break
    # except TimeoutError:
    #     print("TimeoutError")
    # finally:
    return data

def log_request(pr, ret):
    if not os.path.exists('./requests.csv'):
        with open('./requests.csv', 'a') as f:
            f.write("datatime,first_line,method,url,status,reason\n")

    with open("requests.csv", "a") as f:
        dt = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

        status= 'NA'
        reason = 'NA'

        if ret is not None:
            status = ret.status
            reason = ret.reason

        f.write(f"{dt},{pr['first_line'][:-1]}, {pr['method']}, {pr['url']}, {status}, {reason}\n")






def loadConfig(fileName):
    try:
        with open(fileName,'r') as d:
            jsn = json.load(d)
            jsn['PUBLIC_HTML'] = os.path.normpath(jsn['PUBLIC_HTML'])   # Normalize path
            jsn['ERROR_DIR'] = os.path.normpath(jsn['ERROR_DIR'])   # Normalize path
            jsn['OTHER_TEMPLATES'] = os.path.normpath(jsn['OTHER_TEMPLATES'])   # Normalize path
            return jsn
    except IOError:
        print("Error: File does not appear to exist.")
        sys.exit(1)
    except ValueError:
        print("Error: Config file format not correct.")
        sys.exit(1)
    except:
        print("Error: Something went wrong trying to load the settings.")
        sys.exit(1)


def colorizeLog(shouldColorize, log_level, msg):
    ## Higher is the log_level in the log() argument, the lower is its priority.
    colorize_log = {
        "NORMAL": ColorizePython.pycolors.ENDC,
        "WARNING": ColorizePython.pycolors.WARNING,
        "SUCCESS": ColorizePython.pycolors.OKGREEN,
        "FAIL": ColorizePython.pycolors.FAIL,
        "RESET": ColorizePython.pycolors.ENDC
    }

    if shouldColorize.lower() == "true":
        if log_level in colorize_log:
            return colorize_log[str(log_level)] + msg + colorize_log['RESET']
        return colorize_log["NORMAL"] + msg + colorize_log["RESET"]
    return msg






if __name__ == '__main__':
    request=b"""CONNECT branding.norton.com:443 HTTP/1.1
Host: branding.norton.com:443
Proxy-Connection: keep-alive
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203

"""
    print(process_request(request=request, blacklist_domains=[]))