import prompt

def welcome():
    print("\nПервая попытка запустить проект!\n")
    msg = prompt.string("Введите команду: ")

    if msg == "exit":
        raise SystemExit(0)
    if msg == "help":
        help()

def help():
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")

