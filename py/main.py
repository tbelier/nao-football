#import nao_yolo # python module for tiny YOLO neural network
import nao_driver
#import nao_improc # python module for image processing
#import nao_ctrl # python module for robot control algorithms
import time
import sys
from TargetBall import TargetBall
import numpy as np
import naoLib as nl

robot_ip = "localhost"
robot_port = 11212
if (len(sys.argv) >= 2):
    robot_ip = sys.argv[1]
if (len(sys.argv) >= 3):
    robot_port = int(sys.argv[2])
nao_drv = nao_driver.NaoDriver(nao_ip=robot_ip, nao_port=robot_port)

if nao_drv.vnao:
    nao_drv.set_virtual_camera_path("../../imgs")

#nao_drv.set_nao_at_rest()

#-----------------------Initialisation ----------------------
nao_drv.motion_proxy.setStiffnesses('Body',1.0)
t0 = time.time()
duration = 400.0
sizeImg = nao_drv.get_image()[2:]
nl.initHead(nao_drv)

last_center_found=[0,0]

while (time.time()-t0) < duration:
    bool_img_get, img, w, h = nao_drv.get_image()

    found, center, size_ball = nl.ball_detection(img)

 #TODOOOOOOO si on veut ajouter le placing feet, il faut faire des modifs
    #il y a un main dans vs/py qui est différent, celui ci contient un main pour tester
    if found:

        nl.headPID(nao_drv, center, sizeImg)
        nl.bodyFollowHead(nao_drv)
        last_center_found=center

    else :
        nl.search(nao_drv,last_center_found,sizeImg)

    #nl.displayImg(nao_drv)
        

    time.sleep(0.1)




nao_drv.motion_proxy.stopMove()
#nao_drv.set_nao_at_rest()
