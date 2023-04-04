from random import randint

class Star(object):

    def __init__(self):
        self.x = randint(0,239)
        self.y = randint(0,431)
        self.speed = randint(2,12)
        self.last_x = 0
        self.last_y = 0

    def Afficher(self):
        print("x:{0} y:{1} speed:{2}".format(self.x,self.y,self.speed))

class Stars(object):

    def __init__(self):
        self.ListOfStar = []

    def Add(self, Star):
        self.ListOfStar.append(Star)

    def Afficher(self):
        for value in self.ListOfStar:
            value.Afficher()

class init():

    def Star():
        NumberOfStar = 25
        for x in range(0,NumberOfStar):
            star = Star()
            Stars.Add(star)


Stars = Stars() # create object