import os
import json

class Log():
    def __init__(self,file_location:str):
        self.file_location = file_location
        
        if not os.path.exists(file_location):
            with open(file_location,'w') as read_file:
                print("[*] log file created")


    def info(self,message:str):
        with open(self.file_location,'a') as read_file:
            read_file.write("[*] "+message+"\n")
        return True

    def warning(self,message:str):
        with open(self.file_location,'a') as read_file:
            read_file.write("[!] "+message+"\n")
        return True
    
    def critical(self,message:str):
        with open(self.file_location,'a') as read_file:
            read_file.write("\n****************************\n[!] "+message+"\n****************************\n\n")
        return True

class Config():
    def __init__(self,file_location:str):
        self.file_location = file_location
        
        if not os.path.exists(file_location):
            with open(file_location,'w') as read_file:
                print("[*] config file created")


    def read(self):
        with open("config.json", "r") as read_file:
            config_file = json.load(read_file)
        return config_file

    def write(self,json_data):
        with open(self.file_location,'w') as read_file:
            json.dump(json_data,read_file,indent=4)
        return True
    
    