import goober_class
import sender_unit

import receiver_unit
import toolkit
import time

client_goober = toolkit.api_get_a_preped_goober('COM6')


def main():
    value = 0


    while True:


        print("Main: client send")
        toolkit.log_post_transaction("client", "send")
        toolkit.api_send(client_goober, value + 1)



        value += 1

        print("Main: client recv")
        toolkit.log_post_transaction("client", "recv")
        value = toolkit.api_start_listening(client_goober, 'client')



if __name__ == '__main__':
    main()


