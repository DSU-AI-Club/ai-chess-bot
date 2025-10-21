import sys 

from .play import play

if sys.argv[1] == "play":
    ### do stuff
    play()

elif sys.argv[0] == "train":
    ### do stuff

    pass

else:

    raise ValueError("Invalid argument recieved - 'play' or 'train' expected")