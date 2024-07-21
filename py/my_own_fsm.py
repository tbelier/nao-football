import fsm
import time
import sys
#import nao_yolo # python module for tiny YOLO neural network
import nao_driver
#import nao_improc # python module for image processing
#import nao_ctrl # python module for robot control algorithms
import time
import sys
import numpy as np
import naoLib as nl
from my_nao import MyNao


#---------------------------------------------------------------------------------------
#					CREATE ROBOT
#---------------------------------------------------------------------------------------
nao=MyNao("raphael")

#---------------------------------------------------------------------------------------
#					CREATE FSM AND initialize TIME
#---------------------------------------------------------------------------------------
# global variables
f = fsm.fsm();  # finite state machine


time_start = time.time()

#---------------------------------------------------------------------------------------
#					USEFULL FUNCTIONS
#---------------------------------------------------------------------------------------
# functions (actions of the fsm)
def doSearchBall():
	bool_img_get, img, w, h = nao.nao_drv.get_image()
	found, center, size_ball = nl.ball_detection(img)
	if found:
		event = "searchBall_orientRobot"
		nao.last_center_found=center
	else:
		nao.search()
		event = "searchBall_searchBall"
	return event

def doOrientRobot():
	bool_img_get, img, w, h = nao.nao_drv.get_image()
	found, center, size_ball = nl.ball_detection(img)

	yaw0= nao.nao_drv.motion_proxy.getAngles(["HeadYaw"], True)[0]
	if yaw0*180/np.pi<10 and np.abs(center[0] - w/2)< nao.delta_top_center:
		nao.nao_drv.motion_proxy.move(0, 0, 0)
		event = "orientRobot_goClose"
	elif not(found):
		nao.nao_drv.motion_proxy.move(0, 0, 0)
		event = "orientRobot_searchBall"
	else:
		nao.headPID(center)
		nao.bodyFollowHead()
		event = "orientRobot_orientRobot"
	return event

def doGoClose():
	bool_img_get, img, w, h = nao.nao_drv.get_image()
	found, center, size_ball = nl.ball_detection(img)
	dist = nl.get_ball_dist(size_ball)
	print("Distance: "+str(dist))
	if dist < nao.dist_close:
		event = "goClose_turnKeepDistance"
	elif not (found):
		nao.nao_drv.motion_proxy.move(0, 0, 0)
		event = "goClose_searchBall"
	else:
		nao.headPID(center)
		nao.go_straight()
		event = "goClose_goClose"
	return event


def doTurnKeepDistance():
	bool_img_get, img, w, h = nao.nao_drv.get_image()
	found, center, size_ball = nl.ball_detection(img)
	found_goal, center_goal, nb_barys = nl.detection_goal(img)
	x,y = center_goal
	# print("mon center goal en x est a :" + str(x))
	# print("affichage x-w/2 pour le goal : " + str(x - w / 2))

	if not (found):
		nao.nao_drv.motion_proxy.move(0, 0, 0)
		event = "turnKeepDistance_searchBall"

	elif np.abs(x - w/2) < nao.delta_top_center and nb_barys >=2:
		print("Distance de la balle : " + str(nl.get_ball_dist(size_ball)))
		event="turnKeepDistance_prepareToShoot"
		print("distance : "+str(nl.get_ball_dist(size_ball)))
		if nl.get_ball_dist(size_ball) < 0.3:
			nao.headPID(center)
			nao.shoot_close()
			time.sleep(25)
		else :
			nao.shoot_far()
			time.sleep(25)
		event = "turnKeepDistance_turnKeepDistance"

	else:

		nao.headPID(center)
		if x - w / 2 >= 0:
			print("Je tourne a gauche !")
			side="gauche"
		else:
			print("Je tourne a droite !")
			side="droite"
		nao.keep_distance(side)
		event = "turnKeepDistance_turnKeepDistance"
	return event


def doPrepareToShoot():
	nao.change_camera("top")
	bool_img_get, img, w, h = nao.nao_drv.get_image()
	found, center, size_ball = nl.ball_detection(img)

	nao.change_camera("bottom")
	bool_img_get_bot, img_bot, w_bot, h_bot = nao.nao_drv.get_image()
	found_bot, center_bot, size_ball_bot = nl.ball_detection(img_bot)

	found_goal, center_goal, nb_barys = nl.detection_goal(img)
	if w_bot - nao.delta_bot_center <= center_bot < w_bot + nao.delta_bot_center:
		nao.shoot()
	elif not (found):
		nao.change_camera("top")
		nao.nao_drv.motion_proxy.move(0, 0, 0)
		event = "prepareToShoot_searchBall"
	else:
		nao.change_camera("bottom")
		nao.placingFoot(center_bot,w_bot,h_bot)
		event = "prepareToShoot_prepareToShoot"
	return event



if __name__== "__main__":


	# ---------------------------------------------------------------------------------------
	#					DEFINE STATES
	# ---------------------------------------------------------------------------------------
	f.add_state ("searchBall") #1
	f.add_state ("orientRobot") #2
	f.add_state ("goClose") #3
	f.add_state ("turnKeepDistance")  #4
	f.add_state ("prepareToShoot") #5
	f.add_state ("shoot") #6
	f.add_state ("celebrate")  # 7

	# ---------------------------------------------------------------------------------------
	#					DEFINE TRANSITIONS (current state, next state, event, action in next state)
	# ---------------------------------------------------------------------------------------
	f.add_transition ("searchBall","orientRobot","searchBall_orientRobot",doOrientRobot);
	f.add_transition ("orientRobot","goClose","orientRobot_goClose",doGoClose);
	f.add_transition ("goClose","turnKeepDistance","goClose_turnKeepDistance",doTurnKeepDistance);
	f.add_transition ("turnKeepDistance","prepareToShoot","turnKeepDistance_prepareToShoot",doPrepareToShoot);


	f.add_transition("prepareToShoot", "searchBall", "prepareToShoot_searchBall", doSearchBall);
	f.add_transition("goClose", "searchBall", "goClose_searchBall", doSearchBall);
	f.add_transition("turnKeepDistance", "searchBall", "turnKeepDistance_searchBall", doSearchBall);
	f.add_transition("orientRobot", "searchBall", "orientRobot_searchBall", doSearchBall);

	f.add_transition("searchBall", "searchBall", "searchBall_searchBall", doSearchBall);
	f.add_transition("orientRobot", "orientRobot", "orientRobot_orientRobot", doOrientRobot);
	f.add_transition("turnKeepDistance", "turnKeepDistance", "turnKeepDistance_turnKeepDistance", doTurnKeepDistance);
	f.add_transition("goClose", "goClose", "goClose_goClose", doGoClose);
	f.add_transition("prepareToShoot", "prepareToShoot", "prepareToShoot_prepareToShoot", doPrepareToShoot);

	# ---------------------------------------------------------------------------------------
	#					DEFINE EVENTS
	# ---------------------------------------------------------------------------------------

	f.add_event ("searchBall_orientRobot")
	f.add_event ("orientRobot_goClose")
	f.add_event ("goClose_turnKeepDistance")
	f.add_event ("turnKeepDistance_prepareToShoot")
	f.add_event ("prepareToShoot_shoot")

	f.add_event("shoot_searchBall")
	f.add_event("prepareToShoot_searchBall")
	f.add_event("goClose_searchBall")
	f.add_event("turnKeepDistance_searchBall")
	f.add_event("orientRobot_searchBall")


	# ---------------------------------------------------------------------------------------
	#					DEFINE INITIAL, WAIT and END STATE
	# ---------------------------------------------------------------------------------------
	f.set_state ("searchBall")
	f.set_event("searchBall_searchBall")
	f.set_end_state ("celebrate")

	nao.initHead()
	# fsm loop
	run = True   
	while (run):

		funct = f.run () # function to be executed in the new state
		print("-------------------- Current state : " + str(f.curState))
		if f.curState != f.endState:
			newEvent = funct() # new event when state action is finished
			print ("New Event : ",newEvent)
			f.set_event(newEvent) # set new event for next transition
		else:
			funct()
			run = False
			
	print ("End of the programm")

