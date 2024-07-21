# BELIER Titouan - LE FLOCH Tristan - ROB 2024


<div align="center">
<img src="/images_test/fsm2.png" alt="Nao tente de marquer un but !">
</div>

## Nao marque un but en simulation !
Regardez la démo du projet [ici](https://youtu.be/dyFPzrKtFaU) !


## Nao marque (presque) un but en réél !
Regardez la démo de son essai [ici](https://youtu.be/ARl1SwZ4mc0) !


## comment exécuter la simulation
Si vous êtes élèves de 3ème année en robotique autonome à l'ENSTA Brtegne, vous avez récupéré un fichier avec VREP ainsi que toutes les scènes de Nao et le but. Placez vous dans ce fichier et installez ce répertoire git :

cd VREP/UE52-VS-IK/
git clone https://gitlab.ensta-bretagne.fr/lefloctr/ue52vsik_belier_le_floch.git

Vous allez maintenant ouvrir deux fenêtres sur votre terminal. Sur la première, vous lancerez VREP, sur la deuxième, vous lancerez le programme :

Fenêtre 1 :
```
cd external-software/V-REP_PRO_EDU_V3_6_2_Ubuntu18_04/
./vrep.sh
```
Et voilà VREP est lancé dans la première fenêtre, vous n'avez plus qu'à choisir la scène qui vous intéresse et lancer la simulation.

Fenêtre 2 :
Si vous avez un environnement virtuel, c'est le moment de le lancer. En effet, notre programme se lance sur python2 donc il est préférable de le lancer pour éviter tout problème ! Vous allez également devoir source la librairie naoqi comme suit. Si vous avez suivi les étapes vous êtes toujours dans le dossier VREP/UE52-VS-IK/.
```
setup_pynaoqi.bash
source ./prj/venv/bin/activate (à modifier selon l'emplacement de votre environnement)
cd ue52vsik_belier_le_floch/py
python2 my_own_fsm.py
```
C'est tout bon ! Grâce à ce programme, vous êtes capables de marquer un but avec votre Nao !

## Structure

Les fichiers nécessaires à l'exécution de la mission sont:
- nao_driver.py le driver donnant accès aux fonctions de base du nao
- my_nao.py définit la classe MyNao qui permet d'instancier l'objet MyNao représentant le robot, et dont les fonctions de classe sont celles permettant au Nao de réaliser différentes tâches.
- fsm.py définit l'objet fsm pour lequel on peut définir les états, transitions, évènements, ...
- my_own_fsm.py le fichier à exécuter pour lancer la machine à états finis permettant de mener à bien la mission du Nao


## Détection de balle

La fonction de détection de balle se trouve dans le fichier naoLib.py, il s'agit de ball_detection qui prend en entrée l'image sur laquelle détectée la balle, et qui retourne: un booléen indiquant si la balle est trouvée ou non, la position du barycentre de la balle sur l'image en pixels et la taille de la balle sur l'image en pixels.

La détection de balle en suit le procédé suivant:
- Seuillage de l'image HSV pour conserver les pixels de couleur jaune, on obtient une image binaire avec les objets jaunes
- Ouverture de l'image binaire pour éliminer les petits objets jaunes parasites
- Fermeture de l'image binaire pour compléter les pixels manquant de la balle
- Détection des contours dans l'image
- Identification de l'objet qui a la plus grande aire (on suppose que c'est la balle)
- Calcul de la taille de la balle en conservant la longueur la plus longue entre celle selon x et celle selon y
- Finalement, on calcule le barycentre de la balle en calculant les moments du contour à l'aide de la fonction cv2.moments d'opencv. On vérifie que le moment n'est pas nul, si il ne l'est pas on peut considérer la balle trouvée et on calcule les coordonnées du braycentre.

Pour information, on détecte les objets qui sont jaunes en sélectionnant seulement sont qui sont dans l'intervalle autour du jaune. Pour la simulation, les couleurs sont : 
- Hmin = 20
- Hmax = 35
- Smin = 100
- Smax = 255
- Vmin = 0
- Vmax = 255

Pour le robot réel, les couleurs sont :
- Hmin = 10
- Hmax = 50
- Smin = 150
- Smax = 255
- Vmin = 0
- Vmax = 255

ball_detection élimine de nombreux objets avec l'ouverture et réduit donc la durée de la boucle for lors de la recherche de la plus grande aire parmis tous les contours.

De plus, nous avons envisagé d'ajouter un critère de rondeur, mais ça ne s'est pas montré nécessaire car la détection fonctionne déjà bien à la fois en simulation et en réel notamment grâce aux étapes d'ouverture et de fermeture.


## méthode de détection du but

Pour la détection du but (fonction detection_goal dans naoLib.py) on procède de la même manière que pour la balle à quelques différences près. La gamme de couleur en HSV est : 
- Hmin = 0
- Hmax = 10
- Smin = 100
- Smax = 255
- Vmin = 100
- Vmax = 255

Pour trouver le centre du but, on détecte les 4 coins rouges du but de foot. et on prend comme coordonnées x,y le barycentre des côtés détectés.

Comme vous pouvez l'imaginer, il est possible que Nao ne voit pas les 4 coins. Par exemple lorsqu'il est proche de la balle, il baisse la tête pour voir la balle et ne détecte alors par la totalité du but. Ce n'est pas grave, Nao n'a besoin que de 2 coins. Lorsqu'il en voit 2, il prend le barycentre. Si l'on revient au cas ou Nao baisse la tête il verra alors les deux coins du bas, ce qui est suffisant pour marquer puisque notre centrage par rapport au but est uniquement en x.


## Séquencement des opérations réalisées par NAO pour marquer un but

Voici le diagramme de la machine à états finis de Nao !

![Diagramme](/images_test/fsm.png)

