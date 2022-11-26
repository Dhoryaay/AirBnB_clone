#!/usr/bin/python3

"""console module
"""
import cmd
import models
import re
import shlex
from models.amenity import Amenity
from models.base_model import BaseModel
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User

# A global constant since both functions within and outside use it
CLASSES = [
    "BaseModel",
    "User",
    "City",
    "Place",
    "State",
    "Amenity",
    "Review"
]


def parse(arg):
    curly_braces = re.search(r"\{(.*?)\}", arg)
    brackets = re.search(r"\[(.*?)\]", arg)
    if curly_braces is None:
        if brackets is None:
            return [i.strip(",") for i in split(arg)]
        else:
            lexer = split(arg[:brackets.span()[0]])
            retl = [i.strip(",") for i in lexer]
            retl.append(brackets.group())
            return retl
    else:
        lexer = split(arg[:curly_braces.span()[0]])
        retl = [i.strip(",") for i in lexer]
        retl.append(curly_braces.group())
        return retl


def check_args(args):
    """checks if args is valid
    Args:
        args (str): the string containing the arguments passed to a command
    Returns:
        Error message if args is None or not a valid class, else the arguments
    """
    arg_list = parse(args)

    if len(arg_list) == 0:
        print("** class name missing **")
    elif arg_list[0] not in CLASSES:
        print("** class doesn't exist **")
    else:
        return arg_list
    
    

class HBNBCommand(cmd.Cmd):
    """class HBNBCommand
    """
    prompt = '(hbnb) '
    class_list = ['BaseModel', 'User', 'State',
                  'City', 'Amenity', 'Place', 'Review']

    def do_EOF(self, args):
        """EOF command to exit the program"""
        return True

    def do_quit(self, args):
        """Quit command to exit the program"""
        return True

    def do_create(self, line):
        """Create command to create and store objects"""
        args = line.split()
        if not self.verify_class(args):
            return
        inst = eval(str(args[0]) + '()')
        if not isinstance(inst, BaseModel):
            return
        inst.save()
        print(inst.id)

    def do_show(self, line):
        """Show command to print string representation of an instance"""
        args = line.split()
        if not self.verify_class(args):
            return
        if not self.verify_id(args):
            return
        string_key = str(args[0]) + '.' + str(args[1])
        objects = models.storage.all()
        print(objects[string_key])

    def do_destroy(self, line):
        """Destroy command to delete an instance"""
        args = line.split()
        if not self.verify_class(args):
            return
        if not self.verify_id(args):
            return
        string_key = str(args[0]) + '.' + str(args[1])
        objects = models.storage.all()
        models.storage.delete(objects[string_key])
        models.storage.save()

    def do_all(self, line):
        """Prints list of strings of all instances, regardless of class"""
        args = line.split()
        objects = models.storage.all()
        print_list = []
        if len(args) == 0:
            # print all classes
            for value in objects.values():
                print_list.append(str(value))
        elif args[0] in self.class_list:
            # print just arg[0] class instances
            for (key, value) in objects.items():
                if args[0] in key:
                    print_list.append(str(value))
        else:
            print("** class doesn't exist **")
            return False
        print(print_list)
        
        
    def do_update(self, argv):
        """Updates an instance based on the class name and id by adding or
        updating attribute and save it to the JSON file."""
        arg_list = check_args(argv)
        if arg_list:
            if len(arg_list) == 1:
                print("** instance id missing **")
            else:
                instance_id = "{}.{}".format(arg_list[0], arg_list[1])
                if instance_id in self.storage.all():
                    if len(arg_list) == 2:
                        print("** attribute name missing **")
                    elif len(arg_list) == 3:
                        print("** value missing **")
                    else:
                        obj = self.storage.all()[instance_id]
                        if arg_list[2] in type(obj).__dict__:
                            v_type = type(obj.__class__.__dict__[arg_list[2]])
                            setattr(obj, arg_list[2], v_type(arg_list[3]))
                        else:
                            setattr(obj, arg_list[2], arg_list[3])
                else:
                    print("** no instance found **")

            self.storage.save()


    def default(self, line):
        """method called on input line when command prefix is not recognized
        """
        full_list = []
        args = line.split(".")
        if len(args) < 2:
            print('provide more than one argument please')
            return
        cl_name = args[0]
        action = args[1].rstrip('()').lower()
        all_objs = models.storage.all()
        for (key, value) in all_objs.items():
            two_keys = key.split(".")
            if cl_name == two_keys[0]:
                full_list.append(value)
        if 'all' in action:
            print([str(val) for val in full_list])
        elif 'count' in action:
            print(len(full_list))
        elif 'show' in action:
            try:
                c_id = args[1][6:-2]
                print(all_objs[cl_name + '.' + c_id])
            except Exception as e:
                print('** no instance found **')
        elif 'destroy' in action:
            try:
                c_id = args[1][9:-2]
                models.storage.delete(all_objs[cl_name + '.' + c_id])
            except Exception as e:
                print('** no instance found **')
        elif 'update' in action:
            pass
        else:
            print(action)
            print('** default method not found **')

    @classmethod
    def verify_class(cls, args):
        """verify class
        """
        if len(args) == 0:
            print("** class name missing **")
            return False
        if args[0] not in cls.class_list:
            print("** class doesn't exist **")
            return False
        return True

    @staticmethod
    def verify_id(args):
        """verify id
        """
        if len(args) < 2:
            print("** instance id missing **")
            return False
        objects = models.storage.all()
        string_key = str(args[0]) + '.' + str(args[1])
        if string_key not in objects.keys():
            print("** no instance found **")
            return False
        return True

    @staticmethod
    def verify_attribute(args):
        """verify attribute
        """
        if len(args) < 3:
            print("** attribute name missing **")
            return False
        if len(args) < 4:
            print("** value missing **")
            return False
        return True

    def emptyline(self):
        """when empty line is entered, do not execute anything
        """
        pass

    def postloop(self):
        """do nothing after each loop
        """
        pass

if __name__ == '__main__':
    HBNBCommand().cmdloop()
