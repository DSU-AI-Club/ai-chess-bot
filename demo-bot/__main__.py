import sys 

if sys.argv[1] == "play":
    ### do stuff
    play()

elif sys.argv[1] == "train":
    ### do stuff

    pass

elif sys.argv[1] == "test":

    pass

else:

    raise ValueError("Invalid argument recieved - 'play' or 'train' expected")