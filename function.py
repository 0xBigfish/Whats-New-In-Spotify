x = "yee"

def aFunction():
    x = "what up"
    print("From function: " + x)

def anotherFunction():
    global x
    x = "sheesh"
    print("From anotherFunction: " + x)
    
def aThirdFunction():
    x = "three"
    print("From third function: " + x)

aFunction()
anotherFunction()
aThirdFunction()


print("Out of function: " + x )

y = range(5)
for i in y:
    print(i)