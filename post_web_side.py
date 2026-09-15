import os

import toolkit
import time


web_goober = toolkit.api_get_a_preped_goober('COM3')


def main():

    try:
        os.remove("./post_log.txt")
    except:
        pass

    while True:
        print("Main: web recv")
        toolkit.log_post_transaction("web", "recv")
        value = toolkit.api_start_listening(web_goober, 'web')

        #
        print("Main: web send")
        toolkit.log_post_transaction("web", "send")
        toolkit.api_send(web_goober, value + 1)

        # time.sleep(1)


if __name__ == '__main__':
    main()
