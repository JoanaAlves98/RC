import socket
import sys
import os
import random

BUFFER_SIZE = 1024

stateBS = ' '
adBS = ' '

#--------------------------------------------------------
#---------------------FUNCTIONS--------------------------
#---------------------CS/USER----------------------------
def receive_TCP():
	return connection.recv(BUFFER_SIZE)

def send_TCP(data):
	connection.send(data.encode())

def receive_login(username, password):
	filename = 'user_' +  username + '_CS.txt'
	try:
		user = open(filename, 'r')
	except IOError:
		user = open(filename, 'w')
		user.write(password)
		user.close()
		print("New User: " + username)
		send_TCP('AUR NEW\n')
	else:
		passw = user.readline()
		if(passw == password):
			print('User: ' + username)
			send_TCP('AUR OK\n')
		else:
			send_TCP('AUR NOK\n')
		user.close()


def safeDir_BS(username, direct, BS_IP, BS_PORT):
	dir_name = 'CS/user_' + username + '/' + direct + '/' 
	t = BS_IP + ' ' + str(BS_PORT)
	if not (os.path.exists(dir_name)):
		os.makedirs(dir_name)
		txt = open(os.path.join(dir_name,'IP_PORT.txt'), 'w')
		txt.write(t)
		txt.close()
	else:
		txt = open(os.path.join(dir_name,'IP_PORT.txt'), 'w')
		txt.write(t)
		txt.close()
	print('BCK ' + username + ' ' + direct + ' ' + BS_IP + ' ' + str(BS_PORT))


def dirlist(username):
	fils = ''
	dir_name = 'CS/user_' + username
	N = 0
	for filename in os.listdir(dir_name):
		N = N + 1
		fils = fils + ' ' + filename
	backup_dirs = 'LDR ' + str(N) + fils + '\n'
	send_TCP(backup_dirs)

def restore(username, dirct):
	print('Restore ' + dirct)
	p = 'CS/user_' + username + '/'+ dirct + '/IP_PORT.txt'
	ip_port = open(p, 'r')
	bs = ip_port.readline()
	ip_port.close()
	send_TCP('RSR ' + bs + '\n')

def deleteuser(username):
	f = 'CS/user_' + username + '/'
	N = 0
	if (os.path.exists(os.path.join(f))):
		for files in os.listdir(os.path.join(f)):
			N = N + 1

		if(N == 0):
			os.rmdir(f)

	user_txt = 'user_' + username + '_CS.txt'
	os.remove(os.path.join(user_txt))

	if not (os.path.exists(os.path.join(f))):
		if not (os.path.exists(user_txt)):
			send_TCP('DLR OK\n')
		else:
			send_TCP('DLR NOK\n')
	else:
		send_TCP('DLR NOK\n')



#---------------------CS/BS------------------------------

def getBS():
	try:
		f_nBS = open('N_BS.txt', 'r')
	except IOError:
		return 'BKR EOF\n'
	else:
		nBS = (f_nBS.readline()).split('\n')
		NBS = int(nBS[0])-1
		f_nBS.close()

		i = random.randint(0, NBS)
		f = open('bs_list.txt','r')
		lines = f.readlines()
		f.close()
		if(lines == []):
			return 'BKR EOF\n'
		bs_aux = (lines[i]).split('\n')
		return bs_aux[0]



def deleteBS(BS_IP, BS_PORT):
	BS = BS_IP + ' ' + BS_PORT + '\n'
	f =	open('bs_list.txt','r')
	lines = f.readlines()
	comp = len(lines)
	for i in range (comp):
		if(lines[i]  == BS):
			lines[i] = '-'
			break

	f.close()
	f =	open('bs_list.txt','w')
	for i in range (comp):
		if (lines[i] != '-'):
			f.write(lines[i])
	f.close()



def backup(username, password, N):
	BS = getBS().split()

	if (BS[1] == 'EOF'):
		return 'BKR EOF\n'
	else:
		B = (BS[0], int(BS[1]))
		request = 'LSU ' + username + ' ' + password + '\n'
		requestBS.sendto(request.encode(), B)
		stateBS_aux, adBS = requestBS.recvfrom(BUFFER_SIZE)
		stateBS = stateBS_aux.decode()
		if(stateBS == 'LUR OK\n'):
			return adBS
		else:
			return None


def deletedir(username, dirt):
	p = 'CS/user_' + username + '/'+ dirt + '/IP_PORT.txt'
	ip_port = open(p, 'r')
	bs_aux = ip_port.readline()
	ip_port.close()
	bs = bs_aux.split()
	B = (bs[0], int(bs[1]))

	request = 'DLB ' + username + ' ' + dirt + '\n'
	requestBS.sendto(request.encode(), B)
	stateBS_aux, adBS = requestBS.recvfrom(BUFFER_SIZE)
	stateBS = stateBS_aux.decode()
	if(stateBS == 'DBR OK\n'):
		p1 = 'CS/user_' + username + '/'+ dirt
		if(os.path.exists(p1)):
			for filename in os.listdir(os.path.join(p1)):
				p1_aux = 'CS/user_' + username + '/'+ dirt + '/' + filename
				os.remove(os.path.join(p1_aux))
		os.rmdir(p1)
		send_TCP('DDR OK\n')
	else:
		send_TCP('DDR NOK\n')

def filelist(username, direct):
	p = 'CS/user_' + username + '/'+ direct + '/IP_PORT.txt'
	ip_port = open(p, 'r')
	bs_aux = ip_port.readline()
	ip_port.close()
	bs = bs_aux.split()
	B = (bs[0], int(bs[1]))

	request = 'LSF ' + username + ' ' + direct + '\n'
	requestBS.sendto(request.encode(), B)
	information_aux, adBS = requestBS.recvfrom(BUFFER_SIZE)
	information = (information_aux.decode()).split()
	if(information[0] == 'LFD'):
		response = 'LFD ' + bs[0] + ' ' + bs[1] + ' ' +' '.join(information[1:]) + '\n'
		send_TCP(response)




#--------------------------------------------------------


args = sys.argv
CS_PORT = int(args[3])		#PORT em que corre o CS

CS_HOST_NAME = socket.gethostname()		#NAME do CS
CS_IP = socket.gethostbyname(CS_HOST_NAME)		#IP do CS
print(CS_IP)


pid = os.fork()
if(pid == 0):

	nBS = 0

	#cria uma ligacao UDP para que os varios BS se possam registar
	socketBS = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	socketBS.bind((CS_IP,CS_PORT))

	while True:

		dataBS_aux, addrBS = socketBS.recvfrom(BUFFER_SIZE)
		dataBS = (dataBS_aux.decode()).split()
		if(dataBS[0] == 'REG'):
			print("+BS: " + dataBS[1] + ' ' + dataBS[2])
			stateBS = ('RGR OK').encode()
			socketBS.sendto(stateBS, addrBS)
			BS_info = dataBS[1] + ' ' + dataBS[2] + '\n'
			BS_FILE = open("bs_list.txt", 'a' )
			BS_FILE.write(BS_info)
			BS_FILE.close()

			nBS = nBS + 1 
			f = open('N_BS.txt', 'w')
			f.write(str(nBS))
			f.close()

		elif(dataBS[0] == 'UNR'):
			nBS = nBS - 1
			f = open('N_BS.txt', 'w')
			f.write(str(nBS))
			f.close()
			deleteBS(dataBS[1], dataBS[2])
			state = ('UAR OK\n').encode()
			socketBS.sendto(state, addrBS)
			print("-BS: " + dataBS[1] + ' ' + dataBS[2])
			if (nBS == 0):
				os.remove('N_BS.txt')
				os.remove('bs_list.txt')

else:
	

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((CS_IP,CS_PORT))
	server.listen(1)

	requestBS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	while True:

		connection, addr = server.accept()
		#print ("Connection address:", addr)

		data = receive_TCP()
		if not data:
			break


		re = (data.decode()).split(' ')

		if (re[0] == 'AUT'):
			receive_login(re[1], re[2])
			current_user = re[1]
			current_password = re[2]
			data1 = receive_TCP()
			re1 = (data1.decode()).split(' ')

		if(re1[0] == 'BCK'):
			files = (connection.recv(1024)).decode()
			BS_to_backup = backup(current_user, current_password, re1[2])
			if(BS_to_backup == 'BKR EOF\n'):
				send_TCP('BKR EOF\n')
			elif( BS_to_backup != None):
				safeDir_BS(current_user, re1[1], BS_to_backup[0], BS_to_backup[1])
				r = 'BKR ' + BS_to_backup[0] + ' ' + str(BS_to_backup[1]) + ' ' + re1[2]
				send_TCP(r)
				send_TCP(files)

		if (re1[0] == 'DLU\n'):
			deleteuser(current_user)
			current_user = ''
			current_password = ''

		if(re1[0] == 'RST'):
			d = re1[1].replace('\n', '')
			restore(current_user, d)

		if(re1[0]== 'LSD\n'):
			dirlist(current_user)

		if(re1[0] == 'LSF'):
			d = re1[1].replace('\n', '')
			filelist(current_user, d)

		if(re1[0] == 'DEL'):
			d = re1[1].replace('\n', '')
			deletedir(current_user, d)

	connection.close()