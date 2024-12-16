# Implements the long run wind model for Hercules


class WindSimLongTerm:
    def __init__(self, input_dict, dt):

        print('trying to read in verbose flag')
        if "verbose" in input_dict:
            self.verbose = input_dict["verbose"]
            print('read in verbose flag = ',self.verbose)
        else:
            self.verbose = True # default value


        