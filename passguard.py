#! /usr/bin/python3

import sqlite3
import rsa
import banner
import pandas
import os
import rsa
import base64
import time
from termcolor import colored
import optparse
import pandas as pd


def key_gen():
	if not os.path.isfile('prikey.pem'):
		public,private = rsa.newkeys(1024)
		with open('pubkey.pem','wb') as f:
			f.write(public.save_pkcs1('PEM'))
		with open('prikey.pem','wb') as f:
			f.write(private.save_pkcs1('PEM'))
	global Pubkey
	global Prikey
	with open('prikey.pem', 'rb')as f:
		Prikey = rsa.PrivateKey.load_pkcs1(f.read())
	with open('pubkey.pem', 'rb')as f:
		Pubkey = rsa.PublicKey.load_pkcs1(f.read())

def file_enc():
	global Pubkey
	global locate
	if os.path.isfile(locate + 'file.db'):
		try:
			en = open(locate + 'file.db.encrypted', "wb")
			with open(locate + 'file.db', 'rb') as org:
				while True:
					org_data = org.read(117)
					if not org_data: break
					cipher = rsa.encrypt(org_data,Pubkey)
					cipher = base64.b64encode(cipher)
					en.write(cipher)
			org.close()
			os.remove(locate + 'file.db')
		except:
			print (colored("[!!] Process failed", 'red'))
	en.close()

def file_dec():
	global locate
	global Prikey
	global c
	global conn
	file = locate + 'file.db.encrypted'
	if os.path.isfile(file):
		org_name = file.replace(".encrypted","")
		org_f = open(org_name, 'wb')
		with open (file, 'rb') as enc_file:
			while True:
				cip_data = enc_file.read(172)
				if not cip_data: break
				cip_data = base64.b64decode(cip_data)
				org_data = rsa.decrypt(cip_data,Prikey)
				org_f.write(org_data)
		enc_file.close()
		org_f.close()
	conn = sqlite3.connect(locate + 'file.db')
	c = conn.cursor()

def file_loc():
	global locate
	user = os.getlogin()
	locate = "/home/" + user + "/Documents/Pass_Guard/"
	if not os.path.exists(locate):
		os.makedirs(locate)

def pass_cyp(passw):
	key = int(input("Enter a key (1-40): "))
	alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$1234567890'
	passw = passw.upper()
	cip_pass = ''
	for l in passw:
		index = alpha.find(l)
		index = (index + key)%len(alpha)
		cip_pass = cip_pass + alpha[index]
	cip_pass = cip_pass + passw[-5:-2].lower()
	print ("Secure Password: " + cip_pass)
	return cip_pass

def set_data ():
	global c
	global conn
	word = input("Enter password: ")
	if (len(word) > 20 or len(word)<8):
		print (colored("Enter password of length in between 8 and 20",''))
		word = input("Enter password: ")
	word = pass_cyp(word)
	print (colored("Would you like to store the password in a safe database ?", 'magenta'))
	n = input("y/n ")
	if (n == 'y' or n == 'Y'):
		file_dec()
		web = input("Enter site name: ")
		uname = input("Enter username: ")
		c.execute ("CREATE TABLE IF NOT EXISTS manager('site' VARCHAR(50), 'username' VARCHAR(50), 'password' VARCHAR(20));")
		c.execute ("INSERT INTO manager (site, username, password) VALUES (?,?,?);", (web,uname,word))
		conn.commit()
		print (colored("[+]Password saved", 'green'))
		time.sleep(0.6)
		clo()
	else:
		print (colored("You have not saved the generated password.\nPlease remeber the password and key you entered for future retrieval", 'cyan'))

def get_data ():
	global c
	global conn
	file_dec()
	web = input ("Enter site name: ")
	c.execute ("SELECT username FROM manager WHERE site = ?;", (web,))
	user = c.fetchall()
	if (len(user) == 0):
		print (colored("No user for "+ web + " found", 'red'))
		clo()
		return
	if (len(user) > 1):
		print (colored("Multiple users found"))
		uname = input("Enter username: ")
		c.execute ("SELECT username FROM manager WHERE username = ? AND site = ?;", (uname,web))
		user = c.fetchone()[0]
		c.execute ("SELECT password FROM manager WHERE username = ? AND site = ?;", (uname,web))
		paas = c.fetchone()[0]
		print ("Site: " + str(web) + "\nUser: " + str(user) + "\nPassword: " + str(paas))
	else:
		c.execute ("SELECT username FROM manager WHERE site = ?;", (web,))
		user = c.fetchone()[0]
		c.execute ("SELECT password FROM manager WHERE site = ?;", (web,))
		paas = c.fetchone()[0]
		print ("Site: " + str(web) + "\nUser: " + str(user) + "\nPassword: " + str(paas))
	conn.commit()
	time.sleep(0.6)
	clo()

def upd_data():
	global c
	global conn
	file_dec()
	word = input("Enter password: ")
	if (len(word) > 20 or len(word)<8):
		print (colored("Enter password of length in between 8 and 20",''))
		word = input("Enter password: ")
	word = pass_cyp(word)
	web = input ("Enter site name: ")
	c.execute ("SELECT username FROM manager WHERE site = ?;", (web,))
	user = c.fetchall()
	if (len(user) == 0):
		print (colored("No user for "+ web + " found", 'red'))
		clo()
		return
	if (len(user) > 1):
		print (colored("Multiple users found"))
		uname = input("Enter username: ")
		c.execute ("UPDATE manager SET password = ? WHERE site = ? AND username = ?;", (word,web,uname))
		print (colored("Password updated", 'green'))
	else:
		c.execute ("UPDATE manager SET password = ? WHERE site = ?;", (word,web))
		print (colored("Password updated", 'green'))
	conn.commit()
	time.sleep(0.6)
	clo()

def choice ():
	print ("\n\n1.Generate Password\n2.Retrieve Password\n3.Update Password")
	ch = input()
	if (ch == '1'):
		set_data()
	if (ch == '2'):
		get_data()
	if (ch == '3'):
		upd_data()

def clo():
	print (colored("[*]Encrypting the data file before exiting", 'cyan'))
	time.sleep(1)
	file_enc()
	exit()

if __name__ == "__main__":
	if (os.geteuid() != 0):
		print (colored("[!!]Root privileges required", 'red'))
		exit()
	else:
		file_loc()
		key_gen()
		choice()
