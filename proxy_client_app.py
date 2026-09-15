#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import time
import traceback
from builtins import *

import socket
from time import gmtime, strftime
import sys
import threading
import signal  # Signal support (server shutdown on signal receive)
import json
import fnmatch
import os
import errno
from time import gmtime, strftime, localtime
from datetime import datetime
import threading
import logging
import urllib
import ssl
import urllib3

import toolkit

http = urllib3.PoolManager()
import requests
import proxy_toolkit
import os
from datetime import datetime
import proxy_toolkit

import uuid
import proxy_shared

request_session_no_proxy = requests.Session()
request_session_no_proxy.trust_env = False


import goober_class
import sender_unit

import receiver_unit




post_style = proxy_shared.post_style_local
post_style = proxy_shared.post_style_rf


if post_style == proxy_shared.post_style_rf:
    client_goober = goober_class.Goober('COM6')
    client_goober.set_up()

    time.sleep(2)

    assert client_goober.save_settings()

    time.sleep(2)


def rf_send(payload):
    assert client_goober.tell_goober_we_are_senders()
    sender_unit.send(goober=client_goober, text_buffer=payload, jpeg_byte_array=None)


def rf_recv():
    assert client_goober.tell_goober_we_are_receiver()
    return receiver_unit.receiver_task(client_goober)




"""

client  ..  -----------------P-R-O-X-Y-------------------  ..  web-server

client  ..  client_side_socket  :  web_server_side_socket  ..  web-server


first establish the client-socket. it picks up the requests.

the client side of the proxy is done

now we move to the server side of the proxy

we create a new socket and send the request to the web-server

"""

connection_established_text = "HTTP/1.0 200 Connection established\r\n"
connection_established_text += "Proxy-agent: Pyx\r\n"
connection_established_text += "\r\n"


verbose = 1

class Sockets:
    def __init__(self):
        self.sockets = {}
        self.sockets_count = 0
        self.max_sockets_count = 1000000

    def add_new_socket(self, uuid, new_socket_info):
        self.sockets[uuid] = new_socket_info
        self.sockets_count += 1

    def destroy_socket(self, uuid):
        del self.sockets[uuid]
        self.sockets_count -= 1

    def pretty_print_sockets(self):
        if verbose>0: print(f"\tactive client sockets: ({len(self.sockets.items())})")
        for key, value in self.sockets.items():

            if verbose>0: print(f"\t\t{value['id']} - {key}: {value['address']}")


class Server:

    def __init__(self, config):

        self.config = config  # Save config in server

        self.client_side_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket

        self.client_side_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Re-use the socket
        self.client_side_socket.bind(
            (self.config['HOST_NAME'], self.config['BIND_PORT']))  # bind the socket to a public host, and a port
        self.client_side_socket.listen(self.config['MAX_CLIENT_BACKLOG'])  # become a server socket
        self.__clients = {}
        self.__client_no = 1

        self.lora_is_busy = False

        self.sockets = Sockets()

    def client_side_socket_start_listening(self):

        while True:

            (new_client_socket, new_client_address) = self.client_side_socket.accept()  # Establish the connection

            initial_new_client_socket_request_bytes = new_client_socket.recv(
                self.config['MAX_REQUEST_LEN'])  # get the request from browser


            pr = proxy_toolkit.process_request(request=initial_new_client_socket_request_bytes,
                                         blacklist_domains=self.config['BLACKLIST_DOMAINS'], verbose=False)

            if not pr['healthy_proccess']:
                new_client_socket.close()
                continue

            if not pr['allowed_connection']:
                new_client_socket.close()
                continue



            if pr['method'].upper() == "CONNECT":

                """
                if there is space for the new tunnel, go ahead
                """


                if self.sockets.sockets_count < self.sockets.max_sockets_count:

                    tunnel_uuid = str(uuid.uuid4())

                    new_socket_info = {
                        'id': self.sockets.sockets_count,
                        'socket': new_client_socket,
                        'address': new_client_address,
                    }

                    self.sockets.add_new_socket(tunnel_uuid, new_socket_info)
                    if verbose>0: self.sockets.pretty_print_sockets()

                    d = threading.Thread(
                        target=self.proxy_thread,
                        args=(tunnel_uuid, pr)
                    )


                    d.daemon = True

                    d.start()




    def proxy_thread(self, tunnel_uuid, pr):
        """
        *******************************************
        *********** PROXY_THREAD FUNC *************
          A thread to handle request from browser
        *******************************************
        """
        new_client_socket = self.sockets.sockets[tunnel_uuid]['socket']
        tunnel_id = self.sockets.sockets[tunnel_uuid]['id']
        try:

            chunk_size = 100 * 1024

            """
            tell client: assume the server-side socket is connected
            but we only going to create the socket and connect it after we get the first bytes
            from the client.
            this is to save trips count
            """
            new_client_socket.sendall(connection_established_text.encode())


            """
            Now we start to indiscriminately forward bytes
            """

            new_client_socket.setblocking(True)
            new_client_socket.settimeout(self.config['timeout'])

            while True:



                """
                    we always start with task 1
                    
                        we run task 2 only if task 1 was a success
                    
                        regardless of what has happened before, we always try task 3 
                    
                    we run task 4 only if task 3 was a success
                    
                    on the server side we run tasks 2 and 3
                    however we run task 2 only if task 1 was a success
                    task 3 runs regardless
                """


                try:

                    print("""-------------------------------------------------""")

                    self.sockets.pretty_print_sockets()

                    print("""1- RECV FROM BROWSER """)

                    """
                    we assume task 1 is going to be a sucess so on the server
                    on which case server side is going to start with task 2
                    """
                    try_step_2 = True


                    progress = '(1 ERROR) recv from browser'


                    # new_client_socket_request_bytes = new_client_socket.recv(chunk_size)
                    new_client_socket_request_bytes = proxy_toolkit.recvall(new_client_socket, chunk_size, self.config['timeout'])


                    if ((not new_client_socket_request_bytes) or (len(new_client_socket_request_bytes) == 0)):
                        if verbose>0: print(f"--- void recv: breaking tunnel_id:{tunnel_id}")
                        # proxy_toolkit.log_socket_tx("(1) BLANK from browser", file_name="socket_logs_api")

                        break



                    # proxy_toolkit.log_socket_tx("(1) rec from browser", data=new_client_socket_request_bytes, file_name="socket_logs_api")



                    if verbose>1: print(f"--new_client_socket_request_bytes: {len(new_client_socket_request_bytes)}  tunnel_id:{tunnel_id}")

                except Exception as err:
                    if err.args[0] == 'timed out':
                        print(f"--- recv time out in tunnel_id:{tunnel_id}")
                        pass
                    elif ("connection was aborted" in err.args[1]) or ("connection was forcibly closed" in err.args[1]):
                        print(f"--- connection is closed/aborted: breaking tunnel_id:{tunnel_id}")
                        break

                    else:
                        print(f"(1) ERROR  tunnel_id:{tunnel_id}")
                        traceback.print_exc()
                        break


                    # proxy_toolkit.log_socket_tx("(1 ERROR)", data=str(err), file_name="socket_logs_api")

                    try_step_2 = False
                    new_client_socket_request_bytes = b''


                try:
                    print("""(2, 3)- SEND TO WEB""")
                    progress = '(2,3 ERROR) web sendall and web recv'

                    if verbose>0: print(f"POSTING deal_with_internet tunnel_id:{tunnel_id}")
                    if verbose>1: print(f"----data to go on internet:\n{new_client_socket_request_bytes}\n tunnel_id:{tunnel_id}")



                    """

                    AIR

                    """
                    request_payload_dict = {
                        'req': 'deal_with_internet',
                        'pr': pr,
                        'try_step_2': try_step_2,
                        'tunnel_uuid': tunnel_uuid,
                        'chunk_size': chunk_size,
                        'tunnel_id': tunnel_id,
                        'timeout': self.config['timeout']
                    }

                    if post_style == proxy_shared.post_style_rf:

                        payload = toolkit.bundle_dict_and_data(request_payload_dict, new_client_socket_request_bytes)

                        rf_send(payload)

                        recv_payload = rf_recv()

                        resp_content, web_server_side_socket_reply = toolkit.unbundle_dict_and_data(recv_payload)

                        resp_content = {'ret': resp_content}


                    elif post_style == proxy_shared.post_style_local:

                        with open(f"./tmp/{proxy_toolkit.shared_bin_file_for_task_1}_{tunnel_uuid}", 'bw') as f:
                            f.write(new_client_socket_request_bytes)


                        resp = request_session_no_proxy.post(url=proxy_shared.server_app_address,
                                                             json=request_payload_dict,
                                                             timeout=proxy_shared.post_request_timeout)

                        assert resp.status_code == 200



                        resp_content = json.loads(resp.content.decode())

                        if verbose>0: print(f"status_code: {resp.status_code}    tunnel_id:{tunnel_id}")





                    """
                    
                    POST IS FINISHED
                    
                    """



                    if ('empty_recv' in resp_content['ret']):
                    # if (3) returned void, we need to abort
                        if (resp_content['ret']['empty_recv']):
                            if verbose>0: print(f"empty_recv from web---------------------------------------------------------------------- tunnel_id:{tunnel_id}")
                            break



                    """
                    we will not execute 4 if there was an error in 3
                    """
                    if resp_content['ret']['error']:
                        print("4 is skipped because 3 failed.")
                    else:

                        try:
                            print("""4- SEND TO BROWSER\n""")


                            if post_style == proxy_shared.post_style_local:

                                with open(f"./tmp/{proxy_toolkit.shared_bin_file_for_task_3}_{tunnel_uuid}", 'br') as f:
                                    web_server_side_socket_reply = f.read()

                            if(len(web_server_side_socket_reply) == 0):
                                break

                            if verbose>1: print(f"----data I was told came from the internet:\n{web_server_side_socket_reply}\n tunnel_id:{tunnel_id}")




                            new_client_socket.sendall(web_server_side_socket_reply)

                            # proxy_toolkit.log_socket_tx("(4) new_client_socket.sendall good", data=web_server_side_socket_reply, file_name='socket_logs_api')


                        except:
                            # proxy_toolkit.log_socket_tx(f"{progress}", file_name='socket_logs_api')
                            print("Error when sending btyes to client socket.")
                            pass
                except Exception as e:
                    print(f"\t!!! Error in task 2-3\n\t{str(e)} \n\ttunnel_id:{tunnel_id}")

                    traceback.print_exc()


            self.sockets.destroy_socket(tunnel_uuid)


        except Exception as e:
            print(f"!!!ERROR!!!")
            print(str(e))
            traceback.print_exc()

        finally:
            new_client_socket.close()

            # self.log("ERROR", new_client_addr, target_url)
            return


if __name__ == "__main__":

    dir = './tmp/'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))


    config = proxy_toolkit.loadConfig('proxy_settings.conf')
    server = Server(config)
    server.client_side_socket_start_listening()
