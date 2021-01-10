import os, sys

class _Accessor(dict):
    def __getattr__(self, item):
        return self[item]

class _Properties:
    def __init__(self):
        self.name = ""
        self.required=False
        self.help=''
        self.default="None"
        self.type=str
        self.dim=None
        self.terminator=None

class InputFile:
    def __init__(self, comment_char=""):
        self._accessors = _Accessor()
        self._properties = _Accessor()
        self.comment_char=comment_char

    def add_argument(self, name,
                    required=False,
                    help='',
                    default="None",
                    type=str):
        prop = _Properties()
        prop.name = name
        prop.required = required
        prop.help = help
        prop.type = type

        self._accessors[name] = default
        self._properties[name] = prop

    def add_list(self, name, terminator,
                required=False,
                help='',
                default=[],
                dim=1):
        prop = _Properties()
        prop.name = name
        prop.required = required
        prop.help = help
        prop.type = list
        prop.terminator = terminator
        prop.dim = dim

        self._accessors[name] = default
        self._properties[name] = prop

    def add_sub_parser(self, name, parser):
        prop = _Properties()
        prop.type = 'parser'
        self._accessors[name] = parser
        self._properties[name] = prop

    def parse_args(self):
        for a in self._accessors:
            if self._properties[a].type == 'parser':
                g = self._accessors[a].parse_args()
                self._accessors[a] = g
        return self._accessors

    def parse_args_file(self, fileLoc):
        #   not sure if this is needed yet
        #for a in self._accessors:
        #    if self._properties[a].type == 'parser':
        #        print(a)
        #        g = self._accessors[a].parse_args()
        #        self._accessors[a] = g


        add_to_list = False
        list_key = None

        args = self._accessors # self access, easier syntax
        props = self._properties
        with open(fileLoc, 'r') as file:
            for line in file.readlines():
                split = line.split()
                if len(split) != 0:
                    option = split[0]
                    if option[0] != self.comment_char:
                        if len(split) > 1:
                            value = split[1]
                        else:
                            value = None

                        #   if currently adding elements to a list
                        if add_to_list:
                            #   terminate at the end of the list
                            if option == props[list_key].terminator:
                                add_to_list = False
                                if props[list_key].dim == 1:
                                    args[list_key] = [item for sublist in args[list_key] for item in sublist]
                            else:
                                dim = len(split)
                                if dim < props[list_key].dim:
                                    print("ERROR: missing values in " + list_key)
                                args[list_key].append(split)

                        #   print error if option is not present
                        elif option not in args.keys():
                            print("ERROR: keyword {:s} is not valid".format(option))
                            exit()
                        else:
                            #   loop through all possible options
                            for a in args:
                                if a == option:
                                    typ = props.get(a).type

                                    #   parse subparsers
                                    if typ == 'parser':
                                        pass
                                    #   parse lists
                                    elif typ == list:
                                        add_to_list = True
                                        list_key = a
                                        args[a] = []
                                        pass
                                    #   parse all others as single values
                                    else:
                                        if value == None:
                                            print("ERROR: no value assigned to " + a)
                                            exit()
                                        if typ == int:
                                            args[a] = int(value)
                                        elif typ == float:
                                            args[a] = float(value)
                                        elif typ == bool:
                                            args[a] = value.lower() in ['true', '1', 't', 'y', 'yes']
                                        else:
                                            args[a] = value

        return self._accessors
        

if __name__ == "__main__":
    #   for debugging only
    parser = InputFile()
    parser.add_argument('vcube', required=False, help="electrostatic potential cube file")
    parser.add_argument('n_elms', required=True, type=int)
    parser.add_list('$esp_files', '$end_esp_files', required=True)

    parser2 = InputFile()
    parser2.add_argument('test', default=1)
    parser2.add_argument('test2')
    parser.add_sub_parser('sub', parser2)

    args2 = parser.parse_args_file('test_file.txt')
