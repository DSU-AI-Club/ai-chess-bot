import sys 

if sys.argv[1] == "play":
    ### do stuff

    pass

elif sys.argv[0] == "train":
    ### do stuff

    pass

else:

    raise ValueError("Invalid argument recieved - 'play' or 'train' expected")