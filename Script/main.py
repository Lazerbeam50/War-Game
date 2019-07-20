'''
Created on 13 Aug 2018

@author: Femi
'''
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

import game  # @UnresolvedImport

g = game.Game() #create a game object
lc = LoopingCall(g.main_loop) #add the main loop to our looping call
lc.start(1/g.values.settings.FPS) #run the main loop at FPS speed        
if not g.errorRaised: #If errors have not occurred during initialisation
    g.reactorStarted = True
    reactor.run() #run the game through twisted's loop