import requests
import json
import parameters

# Récupère la liste des jeux d'un joueur depuis l'API Steam
# Liste des API steam : https://developer.valvesoftware.com/wiki/Steam_Web_API
def apiSteam(id):
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=" + parameters.keyAPI + \
        "&steamid=" + id + "&include_appinfo=true&include_played_free_games=true&format=json"

    response = requests.request("GET", url)
    return response.text.encode('utf8')

# Récupère les infos d'un jeu depuis l'API steam
def infoJeux(id):
    url = "https://store.steampowered.com/api/appdetails?appids=" + id

    response = requests.request("GET", url)

    return response.text.encode('utf8')

# Parse le JSON retourner par steam et défini si le jeu est multi ou non
# Category ID :
# 1 : Multi
# 2 : Solo
def isMulti(sourceJSON, id):
    fileParse = json.loads(sourceJSON)
    rep = False

    print("Check online for : " + id)

    try:
        for element in fileParse[id]["data"]["categories"]:
            if element["id"] == 1:
                rep = True
                break
    except:
        return rep

    return rep
    
# Parse le JSON retourné par steam pour extraire la liste des jeux
def extractJeux(sourceJSON):
    fileParse = json.loads(sourceJSON)
    liste = []

    for element in fileParse["response"]["games"]:
        liste.append({"name": element["name"], "appid": element["appid"]})
    return liste

# Extrait la liste des jeux par joueurs
def listJeuxParJoueur(listeJoueurs):
    listeJeux = []
    listeJSON = []
    i = 0

    for joueur in listeJoueurs:
        listeJSON.append(apiSteam(joueur["id"]))
        listeJeux.append({"name": joueur["name"], "jeux": extractJeux(listeJSON[i])})
        i += 1

    return listeJeux

# Liste des jeux de l'ensemble des joueurs 
def allGames(jeuxParJoueurs):
    Games = []
    for joueur in jeuxParJoueurs:

        Games = Games + joueur["jeux"]

    listsansdoublon = []
    for jeuUnique in Games:
        if jeuUnique not in listsansdoublon:
            listsansdoublon.append(jeuUnique)

    return sorted(listsansdoublon, key=lambda i: i['name'])

# Défini la liste des jeux en commun
# Pour chaque jeux, regarde si c'est dans la liste de chaque joueur
def commun(parJoueur, tousJeux):
    listCommun = []
    for jeu in tousJeux:
        i = "\t"
        cpt = 0

        if isMulti(infoJeux(str(jeu["appid"])), str(jeu["appid"])) == True:
            for player in parJoueur:
                if jeu in player["jeux"]:
                    i = i + player["name"] + "\n\t"
                    cpt += 1
            if cpt > 1:
                listCommun.append({"jeu": jeu["name"], "joueurs": i})
    return listCommun

jeux = listJeuxParJoueur(parameters.steamID)
tousLesJeux = allGames(jeux)
jeuxCommun = commun(jeux, tousLesJeux)

multi = open('multi.txt', 'w')
for jeu in jeuxCommun:
    multi.write(jeu["jeu"]+"\n"+jeu["joueurs"]+"\n")
multi.close()
