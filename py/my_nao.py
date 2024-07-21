import cv2
import numpy as np
import nao_driver
import math
import sys
import numpy as np
import time
import naoLib as nl

class MyNao():

    def __init__(self,state):

        # init driver

        if state == "simu":
            robot_ip = "localhost"
            robot_port = 11212
        elif state == "leonardo":
            robot_ip = "172.19.147.99"
            robot_port = 9559
        elif state == "raphael":
            robot_ip = "172.19.147.117"
            robot_port = 9559

        self.nao_drv = nao_driver.NaoDriver(nao_ip=robot_ip, nao_port=robot_port)
        self.nao_drv.motion_proxy.setStiffnesses('Body',1.0)

        if self.nao_drv.vnao:
            self.nao_drv.set_virtual_camera_path("../../imgs")

        # init parameters

        self.dist_close = 1.3
        self.delta_dist = 1
        self.last_center_found = [0, 0]
        self.sizeImg = self.nao_drv.get_image()[2:]

        self.delta_top_center = 10

        self.time_start=time.time()

        self.dt=0.05


    def initHead(self):
        names = ["HeadYaw", "HeadPitch"]
        angles = [0, 0]
        fractionMaxSpeed = 0.5
        self.nao_drv.motion_proxy.setAngles(names, angles, fractionMaxSpeed)


    def search(self):
        print("Searching ...")
        w,h=self.sizeImg
        fractionMaxSpeed = 1
        print(time.time()-self.time_start)
        self.nao_drv.motion_proxy.setAngles(["HeadPitch"], [18*np.pi/180], fractionMaxSpeed)
        if self.last_center_found[0]>=w/2:
            self.nao_drv.motion_proxy.move(0,0, -np.pi/8)
        else:
            self.nao_drv.motion_proxy.move(0,0, np.pi/8)
        time.sleep(self.dt)

    def displayImg():
        img_ok, img, nx, ny = self.nao_drv.get_image()
        self.nao_drv.show_image(key=1)

    def headPID(self,center):
        print("intialising headPID()")
        names = ["HeadYaw", "HeadPitch"]
        w,h = self.sizeImg
        ux,uy = center
        errx, erry = w/2-ux, h//2-uy
        yaw0, pitch0 = self.nao_drv.motion_proxy.getAngles(names,True)
        print("--------------yaw0 :"+str(yaw0)+"--------------yaw1 :"+str(pitch0))

        yaw0_deg, pitch0_deg = yaw0*180/np.pi, pitch0*180/np.pi
        kp = 0.02

        yaw1_deg = yaw0_deg + kp * errx
        pitch1_deg = pitch0_deg - kp * erry
        print("pitch0: "+str(pitch0_deg))
        print(pitch1_deg)

        angles = [yaw1_deg*np.pi/180, pitch1_deg*np.pi/180]
        fractionMaxSpeed = 1
        self.nao_drv.motion_proxy.setAngles(names, angles, fractionMaxSpeed)
        time.sleep(self.dt)


    def bodyFollowHead(self):
        kp = 0.01
        yaw0,pitch0 = self.nao_drv.motion_proxy.getAngles(["HeadYaw", "HeadPitch"], True)
        yaw0_deg = yaw0*180/np.pi

        u = kp*yaw0_deg
        self.nao_drv.motion_proxy.move(0,0, u)
        time.sleep(self.dt)

    def placingFoot(self, center, w_bot, h_bot):
        kp = 0.005
        ux, uy = center
        print(center)
        errx, erry = w_bot / 2 - ux, h_bot / 2 - uy
        vx = kp*errx
        vy = kp*erry

        self.nao_drv.motion_proxy.move(vx,vy, 0)
        time.sleep(self.dt)

    def go_straight(self):

        kp = 0.01
        yaw0,pitch0 = self.nao_drv.motion_proxy.getAngles(["HeadYaw", "HeadPitch"], True)
        yaw0_deg = yaw0*180/np.pi
        u = kp*yaw0_deg

        self.nao_drv.motion_proxy.move(1,0,u)
        time.sleep(self.dt)


    def change_camera(self,cam_name):
        if cam_name == "top":
            self.nao_drv.change_camera(0)
        if cam_name == "bottom":
            self.nao_drv.change_camera(1)
        else :
            print("ATTENTION LE NOM DE LA CAMERA AJOUTE EST FAUX")

    def keep_distance(self,side):
        kp = 0.005
        bool_img_get, img, w, h = self.nao_drv.get_image()
        found, center, size_ball = nl.ball_detection(img)
        err = nl.get_ball_dist(size_ball)
        vx = kp * err

        kp = 0.01
        yaw0,pitch0 = self.nao_drv.motion_proxy.getAngles(["HeadYaw", "HeadPitch"], True)
        yaw0_deg = yaw0*180/np.pi
        u = kp*yaw0_deg

        if side=="gauche":
            self.nao_drv.motion_proxy.move(vx, 4, u)
        elif side=="droite":
            self.nao_drv.motion_proxy.move(vx, -4, u)
        time.sleep(self.dt)

    def shoot_far(self):
        self.nao_drv.motion_proxy.move(30, 0, -0.04)

    def shoot_close(self):
        self.nao_drv.motion_proxy.move(30, 0, 0)


