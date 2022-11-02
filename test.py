from threading import Thread
import time

def getInput():
    while True:

        print(input("your name: "))

def sameTime():
    time.sleep(10)
    while True:
        print("Hello there")

t1 = Thread(target=getInput)
t2 = Thread(target=sameTime)

t1.start()
t2.start()

t1.join()
t2.join()

print("This always happens last")