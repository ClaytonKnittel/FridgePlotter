import random
import sys
import os

print("Hello World")

# comment

''' multi-line
    comment

'''

name = "clayton"
print(name)

# Numbers Strings Lists Tuples Dictionaries
# 5 main data types

'''

+ - * / % ** //

floor division is last one

'''

quote = "\"Always to\""

print(quote)

multiline = ''' this is
a multiline quote'''

print(multiline)

print("%s %s %s" % ('I like the quote', quote, multiline))

print("I don't like this", end="")

print(" new lines")

grocerylist = ['juice', 'orange', 'glow']
otherlist = ['one', 'two', 'three']

totallist = [grocerylist, otherlist]
print(totallist)

grocerylist.sort()
print(grocerylist)
grocerylist.reverse()
print(grocerylist)

print(len(grocerylist))
print(max(grocerylist))

# tuples cannot be changed after being made

pi_tuple = (3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3)
li = list(pi_tuple)
newtuple = tuple(li)

print(len(pi_tuple))
print(min(pi_tuple))


# dictionaries have values with a unique key for each value stored
# can't join dictionaries with '+'

supervillains = {'Evil': 'Batman',
                 'Good': 'Batwoman',
                 'Green': 'Goblin'}
print(supervillains['Evil'])
del supervillains['Evil']

supervillains['Good'] = 'Boogi'

print(supervillains['Good'])

print(len(supervillains))
print(supervillains.get('Green'))
print(supervillains.keys())

print(supervillains.values())

# and or not logic operators

a = random.random()
b = random.random()
print(a, b)

if a > .5 and b > .5:
    print('bu')
elif a > .5:
    print('up')
else:
    print('no')

if not(a > .5):
    print('howdy')


for x in range(0, 10):
    print(x, ' ', end='')

print('\n')

for y in grocerylist:
    print(y, end='')
print()

numlist = [[1, 2, 3], [10, 20, 30], [100, 200, 300]]

for x in numlist:
    for y in x:
        print(y, ' ', end='')
    print()

random_num = random.randrange(0, 100)

while random_num != 15:
    # print(random_num)
    random_num = random.randrange(0, 100)


i = 0

while i <= 20:
    if i % 2 == 0:
        print(i)
    elif i == 9:
        break
    else:
        i += 1
        continue
    i += 1


print("\n" * 3)


def addnumber(f, l):
    su = f + l
    return su


print(addnumber(1, 4))

# name = sys.stdin.readline()

print("hello", name)

stri = "yfewffeewlle"

# %c = character, %s = string, %d = integer,
# %.5f = floating pt with at least 5 decimal places

print("%c is my %s letter and my number %d number is %.5f" % ('X', 'favorite', 1, .133))

print(stri.capitalize())
print(stri.find("fewf"))
print(stri.find("fwf"))

# return true if all characters in string are letters
print(stri.isalpha())
print(stri.isalnum())
print(len(stri))
print(stri.replace("fewf", "foof"))
# strips white space
print(stri.strip())
slist = stri.split('f')
print(slist)

# use "ab+ " to read & append to file (it also opens/creates the file)
test_file = open("test.txt", 'wb')

print(test_file)

print(test_file.name)

test_file.write(bytes("write me to the fle\n", "UTF-8"))

test_file.close()

# r+ means reading and writing to a file
test_file = open('test.txt', 'r+')

text = test_file.read()
print(text)

os.remove("test.txt")


class Animal:

    # preceding with __ means private

    __name = None  # or ""
    __height = 0
    __weight = 0
    __sound = 0

    # constructor
    def __init__(self, n, h, w, s):
        self.__name = n
        self.__height = h
        self.__weight = w
        self.__sound = s

    # self = this, allows an object to refer to itself
    def set_name(self, n):
        self.__name = n

    def get_name(self):
        return self.__name

    def set_height(self, height):
        self.__height = height

    def get_height(self):
        return self.__height

    def set_weight(self, weight):
        self.__weight = weight

    def get_weight(self):
        return self.__weight

    def set_sound(self, sound):
        self.__sound = sound

    def get_sound(self):
        return self.__sound

    def get_type(self):
        print("Animal")

    def tostring(self):
        return "{} is {} cm tall and {} kilograms and says {}".\
            format(self.__name, self.__height, self.__weight, self.__sound)


cat = Animal('whiskers', 33, 10, 'meow')

print(cat.tostring())


class Dog(Animal):

    __owner = ''

    def __init__(self, n, height, weight, sound, owner):
        self.__owner = owner
        super(Dog, self).__init__(n, height, weight, sound)

    def set_owner(self, owner):
        self.__owner = owner

    def get_owner(self):
        return self.__owner

    def get_type(self):
        print("Dog")

    def tostring(self):
        return super(Dog, self).tostring() + ". His owner is {}".format(self.__owner)

    # =None means its ok to omit this parameter
    def multiple_sounds(self, how_many=None):

        if how_many is None:
            print(self.get_sound())
        else:
            print(self.get_sound() * how_many)


dog = Dog('bo', 10, 10, 'bark', 'me')
print(dog.tostring())

dog.multiple_sounds()
dog.multiple_sounds(3)


class AnimalTesting:

    def get_type(self, animal):
        animal.get_type()


test_animals = AnimalTesting()
test_animals.get_type(cat)
test_animals.get_type(dog)

# fie = open("CH1 P 17-11-13[2].txt", 'wb')