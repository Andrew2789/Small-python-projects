from time import sleep
from os import startfile

def main():
    with open("sysinfo.ini","r") as f:
        wait = int(f.readlines()[-1].split("|")[1])

    while True:
        startfile("bg36.pyw")
        sleep(wait * 60)

main()
