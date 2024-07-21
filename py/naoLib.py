import cv2
import numpy as np
import math
import sys
import numpy as np

def detect_yellow_real(imgBGR):
    imgHSV = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2HSV)

    #Hmin = 5
    #Hmax = 45
    #Smin = 112
    #Smax = 255
    #Vmin = 112
    #Vmax = 178
    Hmin = 10
    Hmax = 50
    Smin = 150
    Smax = 255
    Vmin = 0
    Vmax = 255

    # Seuillage HSV pour detection du jaune

    imgbin = cv2.inRange(imgHSV, (Hmin, Smin, Vmin), (Hmax, Smax, Vmax))
    
    # cv2.namedWindow("Nao Image")
    # cv2.imshow("Nao Image", imgbin)
    # cv2.waitKey(500)
    return imgbin

def detect_yellow_simu(imgBGR):
    imgHSV = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2HSV)

    Hmin = 20
    Hmax = 35
    Smin = 100
    Smax = 255
    Vmin = 0
    Vmax = 255

    imgbin = cv2.inRange(imgHSV, (Hmin, Smin, Vmin), (Hmax, Smax, Vmax))
    
    return imgbin

def visualize_detection(imgBGR):
    # get dimensions
    imageHeight, imageWidth, imageChannels = imgBGR.shape

    # --------------------------------------------------------------------------------------------

    # create a window
    cv2.namedWindow("self.nao_drv Image")
    # resize the window to match image dimensions
    cv2.resizeWindow("self.nao_drv Image", imageWidth, imageHeight)
    # move image to upper - left corner
    cv2.moveWindow("self.nao_drv Image", 0, 0)
    # show the image
    cv2.imshow("self.nao_drv Image", imgBGR)

    # --------------------------------------------------------------------------------------------

    imgbin = detect_yellow_real(imgBGR)

    cv2.namedWindow("detect yellow")
    cv2.resizeWindow("detect yellow", imageWidth, imageHeight)
    cv2.imshow("detect yellow", imgbin)

    #--------------------------------------------------------------------------------------------

    # Ouverture: Erosion puis Dilatation

    kernel_open=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    imgopen= cv2.morphologyEx(imgbin, cv2.MORPH_OPEN, kernel_open)

    cv2.namedWindow("open")
    cv2.resizeWindow("open", imageWidth , imageHeight )
    cv2.imshow("open", imgopen)

    #--------------------------------------------------------------------------------------------

    # Fermeture: Dilatation puis Erosion

    kernel_close=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(40,40))
    imgclose= cv2.morphologyEx(imgopen, cv2.MORPH_CLOSE, kernel_close)

    cv2.namedWindow("close")
    cv2.resizeWindow("close", imageWidth , imageHeight )
    cv2.imshow("close", imgclose)

    #--------------------------------------------------------------------------------------------

    # Balle jaune mise en evidence

    imgball=cv2.bitwise_and(imgBGR,imgBGR,mask=imgclose)

    cv2.namedWindow("Ball")
    cv2.resizeWindow("Ball", imageWidth , imageHeight )
    cv2.imshow("Ball", imgball )

    #--------------------------------------------------------------------------------------------

    # Identification du barycentre


    contours,hierarchy=cv2.findContours(imgclose,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    img_contours = imgBGR.copy()
    color = (0, 255, 0)  # Vert
    thickness = 2

    cv2.drawContours(img_contours, contours, -1, color, thickness)

    cv2.namedWindow("Image avec Contours")
    cv2.resizeWindow("Image avec Contours", imageWidth, imageHeight)
    cv2.imshow("Image avec Contours", img_contours)

    # --------------------------------------------------------------------------------------------

    best_contour = contours[0]
    max_area = cv2.contourArea(best_contour)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_area:
            best_contour = contour
            max_area = area


    img_contour = imgBGR.copy()

    cv2.drawContours(img_contour, [best_contour], -1, color, thickness)

    cv2.namedWindow("Image avec Meilleur Contour")
    cv2.resizeWindow("Image avec Meilleur Contour", imageWidth, imageHeight)
    cv2.imshow("Image avec Meilleur Contour", img_contour)

    # --------------------------------------------------------------------------------------------

    # Calcul de la taille de la balle

    min_x=np.min(best_contour[:,0,0])
    max_x=np.max(best_contour[:,0,0])
    min_y=np.min(best_contour[:,0,1])
    max_y=np.max(best_contour[:,0,1])
    size_ball=np.max([max_x-min_x,max_y-min_y])

    print("Taille de la balle : "+str(size_ball))

    # --------------------------------------------------------------------------------------------

    # Identification du barycentre

    if len(contours) > 0:
        # Selectionnez le premier contour (l'objet) dans la liste des contours
        M = cv2.moments(best_contour)
        # Calculez les coordonnees du barycentre
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            print("Coordonnees du barycentre : ({}, {})".format(cx, cy))

            center = (int(cx), int(cy))
            cv2.circle(imgBGR, center, 2, (0, 0, 255), -1)  # Dessine un cercle rouge sur le barycentre
            cv2.namedWindow("Image avec barycentre")
            cv2.imshow("Image avec barycentre", imgBGR)
        else:
            print("L'objet a une aire nulle, impossible de calculer le barycentre.")
    else:
        print("Aucun contour trouve dans l'image.")

    # wait until a key is pressed
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def ball_detection(imgBGR):
    # get dimensions
    imageHeight, imageWidth, imageChannels = imgBGR.shape

    imgbin = detect_yellow_real(imgBGR)
    #imgbin = detect_yellow_simu(imgBGR)

    # Ouverture: Erosion puis Dilatation

    kernel_open=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    imgopen= cv2.morphologyEx(imgbin, cv2.MORPH_OPEN, kernel_open)

    # Fermeture: Dilatation puis Erosion

    kernel_close=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(40,40))
    imgclose= cv2.morphologyEx(imgopen, cv2.MORPH_CLOSE, kernel_close)

    # Identification du barycentre

    contours,hierarchy=cv2.findContours(imgclose,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:

        best_contour = contours[0]
        max_area = cv2.contourArea(best_contour)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > max_area:
                best_contour = contour
                max_area = area

        # calcule la taille de la balle
        min_x=np.min(best_contour[:,0,0])
        max_x=np.max(best_contour[:,0,0])
        min_y=np.min(best_contour[:,0,1])
        max_y=np.max(best_contour[:,0,1])
        size_ball=np.max([max_x-min_x,max_y-min_y])
        print(size_ball)

        M = cv2.moments(best_contour)

        # si l'aire est non nulle
        # calcule les coordonnees du barycentre
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            found = True
            barycentre = [cx, cy]

        else:
            found = False
            barycentre = [0, 0]
    else:
        found = False
        barycentre = [0, 0]
        size_ball = 0

    return found, barycentre, size_ball


def compute_alpha_i(imgBGR,dsol):
    found,barycentre,size_ball=ball_detection(imgBGR)
    hcam=0.4
    db=np.sqrt((dsol/100)**2+hcam**2)
    return db*size_ball/0.09

def compute_alpha():
    list_dsol=[60,80,100,120]
    alpha=0
    for dsol in list_dsol:
        for k in range(10):
            img=cv2.imread("../images_test/img"+str(dsol)+"/self.nao_drvreal"+str(k+1)+".png")
            visualize_detection(img)
            alpha+=compute_alpha_i(img,dsol)
        
    alpha=alpha/(len(list_dsol)*10)
    print("alpha = ",alpha)

def get_ball_dist(size_ball):
    alpha=280
    hcam=0.4
    if size_ball == 0:
        print("aucune balle n'est trouvee")
        db=0
    else :
        db=0.09/size_ball*alpha
    dsol=np.sqrt(max(0,db**2-hcam**2))
    return dsol

def test_alpha():
    list_dsol=[60,80,100,120]
    for dsol in list_dsol:
        for k in range(10):
            img=cv2.imread("../images_test/img"+str(dsol)+"/self.nao_drvreal"+str(k+1)+".png")
            found,barycentre,size_ball=ball_detection(img)
            computed_dsol=get_ball_dist(size_ball)
            print(str(dsol)+" : "+str(computed_dsol))


def detect_red(imgBGR):
    imgHSV = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2HSV)

    # Definir les plages HSV pour la couleur rouge
    Hmin = 0        # La teinte minimale pour le rouge
    Hmax = 10
    Smin = 100
    Smax = 255
    Vmin = 100
    Vmax = 255



    imgbin = cv2.inRange(imgHSV, (Hmin, Smin, Vmin), (Hmax, Smax, Vmax))
    cv2.namedWindow("Nao Image")
    cv2.imshow("Nao Image", imgbin)
    cv2.waitKey(100)
    return imgbin
    
def detection_goal(img):

    imgbin = detect_red(img)
    print(imgbin.shape)
    contours, hierarchy = cv2.findContours(imgbin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img_bord = img.copy()
    L_barys = []
    if len(contours) > 0:
        found = True
        nb_barys = len(contours)
        print("Le nombre de poteaux rouges que je vois est : " +str(len(contours)))
        for k in range(len(contours)):
            cv2.drawContours(img_bord, contours, -1, (255, 255, 0), -1)
        for k in range(len(contours)):
            M = cv2.moments(contours[k])
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                center = (int(cx), int(cy))
                L_barys.append([cx, cy])
                cv2.circle(img_bord, center, 4, (0, 0, 255), -1)
            else :
                found = False
                cx_goal = imgbin.shape[1]/2
                cy_goal = 0
                nb_barys = 0
        if found:
            L_array_barys = np.array(L_barys)
            print(L_array_barys)
            cx_goal = int(np.mean(L_array_barys[:, 0]))
            cy_goal = int(np.mean(L_array_barys[:, 1]))
        cv2.circle(img_bord, (cx_goal, cy_goal), 4, (255, 0, 0), -1)
        #print("Je vois : " + str(len(contours)) + " contours")
    else :
        found = False
        cx_goal = imgbin.shape[1]/2
        cy_goal = 0
        nb_barys = 0
    return found, [cx_goal, cy_goal], nb_barys