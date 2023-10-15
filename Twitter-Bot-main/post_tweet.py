import os
from twitter_bot_class import Twitter_Bot
import time
import random

with open("Twitter_War_Bot/conquistas.txt", "r") as file:
    tweets = file.readlines()

if __name__ == "__main__":
    i=0
    tbot = Twitter_Bot("TuUsuario", "TuContraseña")
    tbot.login()

    while True:
        image_path = "Twitter_War_Bot/res/mapa_" + str(i) + ".png"
        tweet = tweets[i].replace("\n","")
        tbot.post_tweets(tweet,image_path)
        r=random.randint(1600,1800) #Numero aleatorio entre estos rangos para que parezca mas real y no nos tiren la cuenta
        time.sleep(r)
        i+=1

