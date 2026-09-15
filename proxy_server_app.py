import socket
import time

from flask import Flask, request, jsonify
import traceback

import goober_class
import proxy_shared
import proxy_toolkit
import receiver_unit
import sender_unit
import toolkit

app = Flask(__name__)

post_style = proxy_shared.post_style_rf
# post_style = proxy_shared.post_style_local

verbose = 1





def rf_send(payload):
    assert web_goober.tell_goober_we_are_senders()
    sender_unit.send(goober=web_goober, text_buffer=payload, jpeg_byte_array=None)


def rf_recv():
    assert web_goober.tell_goober_we_are_receiver()
    return receiver_unit.receiver_task(web_goober)



@app.route('/', methods=["POST"])
def api_serve():
    try:
        req_json = request.get_json()

        req_type = str(req_json['req'])

        if verbose>0: print(f'\n\n\nserving a {req_type} --------------------------------------------------------------------------------- tunnel_id:',end='')


        if req_type == 'deal_with_internet':
            ret, ret_data = deal_with_internet(req_json)
            return jsonify(ret=ret)

    except:
        traceback.print_exc()
        # return traceback.format_exc()



def deal_with_internet(req_json, data=None):
    tunnel_uuid = req_json['tunnel_uuid']
    tunnel_id = req_json['tunnel_id']
    timeout = req_json['timeout']
    try_step_2 = req_json['try_step_2']

    if verbose > 0: print(tunnel_id)

    """
    is this the first? create and connect the socket
    """
    if (tunnel_uuid not in proxy_shared.server_sockets.keys()):

        web_server_side_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        web_server_side_socket.settimeout(10)

        pr = req_json['pr']

        web_server_side_socket.connect((pr['domain'], pr['port']))

        web_server_side_socket.setblocking(True)

        proxy_shared.server_sockets[tunnel_uuid] = web_server_side_socket

        if verbose > 0: print(f"Socket created and connected for tunnel id: {tunnel_id}")

    if (try_step_2):
        try:
            if verbose > 0: print("""2- SEND TO WEB""")

            if post_style == proxy_shared.post_style_local:
                with open(f"./tmp/{proxy_toolkit.shared_bin_file_for_task_1}_{tunnel_uuid}", 'br') as f:
                    new_client_socket_request_bytes = f.read()
            else:
                new_client_socket_request_bytes = data

            if verbose > 1: print(f"---- (2) data I'm going to send to internet is:\n{new_client_socket_request_bytes}")

            proxy_shared.server_sockets[tunnel_uuid].sendall(new_client_socket_request_bytes)

            proxy_toolkit.log_socket_tx("(2) web_server_side_socket.sendall good", file_name='socket_logs_api')

        except:
            print("(2) ERROR")
            traceback.print_exc()
    else:
        if verbose > 0: print("""2 is skiped because 1 failed""")

    ret = {}

    try:
        ret_data=None

        if verbose > 0: print("""3- RECV FROM WEB""")

        sock = proxy_shared.server_sockets[tunnel_uuid]

        # sock.settimeout(timeout)
        # web_server_side_socket_reply = sock.recv(req_json['chunk_size'])

        web_server_side_socket_reply = proxy_toolkit.recvall(sock, req_json['chunk_size'], timeout)

        if verbose > 1: print(f"---- (3) data I got from the internet is:\n{web_server_side_socket_reply}")


        if post_style == proxy_shared.post_style_local:

            with open(f"./tmp/{proxy_toolkit.shared_bin_file_for_task_3}_{tunnel_uuid}", 'bw') as f:
                f.write(web_server_side_socket_reply)

        else:
            ret_data = web_server_side_socket_reply

        proxy_toolkit.log_socket_tx('(3) rec from web', data=web_server_side_socket_reply, file_name='socket_logs_api')

        empty_recv = not web_server_side_socket_reply

        if (empty_recv):
            sock.close()

            del proxy_shared.server_sockets[tunnel_uuid]

            print('end of recv')

        ret = {
            'empty_recv': empty_recv,
            'error': False
        }

    except Exception as err:
        if err.args[0] == 'timed out':
            print("--- time out")
        else:
            print("(3) ERROR")
            traceback.print_exc()

        ret = {"error": True}

    finally:
        return ret, ret_data




if __name__ == '__main__':

    if post_style == proxy_shared.post_style_local:

        app.run(host='0.0.0.0', port=proxy_shared.server_app_port, threaded=True)

    elif post_style == proxy_shared.post_style_rf:

        if post_style == proxy_shared.post_style_rf:
            web_goober = goober_class.Goober('COM3')
            web_goober.set_up()

            time.sleep(2)

            assert web_goober.save_settings()

            time.sleep(2)


        while True:

            payload = rf_recv()

            request_dict, data= toolkit.unbundle_dict_and_data(payload)

            response_dict, ret_data = deal_with_internet(request_dict, data)

            payload = toolkit.bundle_dict_and_data(response_dict, ret_data)

            rf_send(payload)




        asd=3
        pass