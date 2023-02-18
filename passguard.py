#! /usr/bin/python3

import os
import time
import banner
import base64
import random
import sqlite3
import hashlib
import optparse
import maskpass
from termcolor import colored
from cryptography.fernet import Fernet


#CRYPTOGRAPHY
def key_gen():
	global key
	if not os.path.isfile('enc_file.key'):
		key = Fernet.generate_key()
		with open('enc_file.key', 'wb') as f:
			f.write(key)
			f.close()
	with open('enc_file.key', 'rb') as fi:
		key = fi.read()
		fi.close()

def file_enc():
	global key
	fernet = Fernet(key)
	if os.path.isfile('file.db'):
		try:
			en = open('file.db.encrypted', "wb")
			with open('file.db', 'rb') as org:
				original = org.read()
				encrypted = fernet.encrypt(original)
				en.write(encrypted)
			org.close()
			os.remove('file.db')
		except:
			print (colored("[!!] Process failed", 'red'))
	en.close()

def file_dec():
	global key
	global c
	global conn
	fernet = Fernet(key)
	file = 'file.db.encrypted'
	if os.path.isfile(file):
		org_name = file.replace(".encrypted","")
		org_f = open(org_name, 'wb')
		with open (file, 'rb') as enc_file:
			encrypted = enc_file.read()
			decrypted = fernet.decrypt(encrypted)
			org_f.write(decrypted)
		enc_file.close()
		org_f.close()
	conn = sqlite3.connect('file.db')
	c = conn.cursor()

def file_loc():
	if (not os.path.exists("file.db") and not os.path.exists("file.db.encrypted")):
		open("file.db", 'wb')

#GENERATOR
def pass_cyp(passw):
	key = int(input("Enter a key (1-40): "))
	alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
	sym = '!@#$%&'
	passw = passw.upper()
	ran = key
	count = 0
	cip_pass = ''
	for l in passw:
		index = alpha.find(l)
		if ran > 5:
			ran = ran//2
		elif count < 2:
			count +=1
			cip_pass = cip_pass + sym[ran]
			ran = ran//2
		index = (index + key)%len(alpha)
		cip_pass = cip_pass + alpha[index]

	le = int(len(cip_pass)/2)
	ha = hashlib.md5()
	ha.update(cip_pass[le:].encode())
	ha = str(ha.hexdigest())

	cip_pass = cip_pass.replace(cip_pass[le:], ha[:le])
	print ("Secure Password: " + cip_pass)
	return cip_pass

def pin_gen(pri_pin):
	cip_pin = ""
	cip_list = []
	sec_pin = input("Enter a secondary pin: ")
	if len(pri_pin) != len(sec_pin):
		print (colored("Enter pins of same length",'yellow'))
		sec_pin = input("Enter a secondary pin: ")
	for i in pri_pin:
		random.seed(i)
		cip_list.append(str(random.randint(100000000,999999999)))
	j = 0
	for i in cip_list:
		cip_pin += i[int(sec_pin[j])]
		j+=1
	print ("Secure pin: " + cip_pin)
	return cip_pin


def set_data ():
	global pin_pass
	global c
	global conn
	if pin_pass:
		word = input("Enter password: ")
		if (len(word) > 20 or len(word)<8):
			print (colored("Enter password of length in between 8 and 20",'yellow'))
			word = input("Enter password: ")
		word = pass_cyp(word)
	else:
		word = input("Enter pin: ")
		word = pin_gen(word)
	print (colored("Would you like to store the password in a safe database ?", 'magenta'))
	n = input("y/n ")
	if ((n == 'y' or n == 'Y') and pin_pass):
		web = input("Enter site name: ")
		uname = input("Enter username: ")
	elif ((n == 'y' or n == 'Y') and not pin_pass):
		web = input("Enter UPI or card: ")
		uname = input("Enter username: ")
	if (n == 'y' or n == 'Y'):
		file_dec()
		c.execute ("CREATE TABLE IF NOT EXISTS manager('site' VARCHAR(50), 'username' VARCHAR(50), 'password' VARCHAR(20));")
		c.execute ("INSERT INTO manager (site, username, password) VALUES (?,?,?);", (web,uname,word))
		conn.commit()
		print (colored("[+]Password saved", 'green'))
		time.sleep(0.6)
		clo()
	else:
		print (colored("You have not saved the generated password.", 'cyan'))
		time.sleep(0.6)
		print (colored("Please remeber the password and key you entered for future retrieval.", 'cyan'))

def get_data ():
	global pin_pass
	global c
	global conn
	if pin_pass:
		web = input ("Enter site name: ")
	else:
		web = input ("Enter UPI or card: ")
	file_dec()
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
	global pin_pass
	global c
	global conn
	if pin_pass:
		word = input("Enter password: ")
		if (len(word) > 20 or len(word)<8):
			print (colored("Enter password of length in between 8 and 20",''))
			word = input("Enter password: ")
		word = pass_cyp(word)
		web = input ("Enter site name: ")
	else:
		word = input("Enter pin: ")
		word = pin_gen(word)
		web = input ("Enter UPI or card: ")
	file_dec()
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
	global pin_pass
	ch2 = "\n\n1.Password Manager\n2.Pin Manager"
	print (ch2)
	inp = input()
	if (inp == "2"):
		pin_pass = False
	ch1 = "\n\n1.Generate\n2.Retrieve\n3.Update"
	print (ch1)
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

def verify():
	if not os.path.exists("pass.key"):
		pass_file = open("pass.key", 'w')
		password = maskpass.askpass(mask="")
		ha = hashlib.md5()
		ha.update(password.encode())
		ha = ha.hexdigest()
		pass_file.write(ha)
		print (colored("[+]Password created",'cyan'))
		exit()
	else:
		pass_file = open("pass.key", 'r')
		password = maskpass.askpass(mask="")
		ha = hashlib.md5()
		ha.update(password.encode())
		ha = ha.hexdigest()
		org_pass = pass_file.read()
		if (org_pass == ha):
			return True
		else:
			return False

if __name__ == "__main__":
	if (verify()):
		banner.bann()
		global pin_pass
		pin_pass = True
		file_loc()
		key_gen()
		choice()
	else:
		print (colored("[!!]Wrong Password", 'red'))
		exit()
