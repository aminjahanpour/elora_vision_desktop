import datetime
import toolkit
import os
import shutil
from datetime import datetime

class Session():

    def __init__(self):
        self.session_name = self.get_now_string()

        self.gallery_path = toolkit.gallery_path

        self.session_path = os.path.join(self.gallery_path, self.session_name)
        if not os.path.isdir(self.gallery_path):
            os.mkdir(os.path.join(toolkit.root_path, 'sessions'))

        os.mkdir(self.session_path)



    def get_now_string(self):
        now = datetime.now()
        return f"{now.year}_{now.month}_{now.day}___{now.hour}_{now.minute}_{now.second}"


    def save_frame(self, payload_size, gps_data):
        if not os.path.isdir(self.session_path):
            os.mkdir(self.session_path)

        target_file_name = f"{self.get_now_string()}.jpg"

        target_file_path = os.path.join(self.session_path, target_file_name)

        shutil.copyfile(toolkit.received_frame_file_name, target_file_path)

        self.save_frame_into_db(target_file_path, payload_size, gps_data)



    def save_frame_into_db(self, target_file_path, payload_size, gps_data):

        db_path = os.path.join(toolkit.root_path, toolkit.db_file_name)

        if not os.path.isfile(db_path):
            with open(toolkit.db_file_name, "w") as f:
                f.write("datetime,path,size,latitude,longitude,altitude,accuracy,speed\n")

        with open(toolkit.db_file_name, "a") as f:
            instance_datetime = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            f.write(f"{instance_datetime},{target_file_path},{payload_size},{gps_data['latitude_rec']},{gps_data['longitude_rec']},{gps_data['altitude_rec']},{gps_data['accuracy_rec']},{gps_data['speed_rec']}\n")

