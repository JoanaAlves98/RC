import socket
import sys
import os
import time
import signal

BUFFER_SIZE = 1024

#--------------------------------------------------------
#---------------------FUNCTIONS--------------------------

def convert_file_info(filename, data_time, file_size):
	data_time_aux = data_time.split()
	m = str(time.strptime (data_time_aux[1], '%b').tm_mon)
	d = '%02d' % int(data_time_aux[2])
	return filename + ' ' + d + '.' + m + '.' + data_time_aux[4] + ' ' + data_time_aux[3] + ' ' + str(file_size)

#---------------------BS/CS------------------------------
def regist_user_CS(username, password):
	filename = 'user_' + username + '_BS.txt'
	try:
		user = open(filename, 'r')
	except IOError:
		user = open(filename, 'w')
		user.write(password)
		user.close()
		print('New User: ' + username + '\n')
		return 'LUR OK\n'
	else:
		passw = user.readline()
		if(passw == password):
			print('User: ' + username + '\n')
			return 'LUR OK\n'
		else:
			return 'LUR NOK\n'

def deletedir(username, dirt):
	d = 'BS_' + str(BS_PORT) + '/user_' + username + '/' + dirt + '/'
	if(os.path.exists(d)):
		for filename in os.listdir(os.path.join(d)):
			d_aux = d + filename
			os.remove(os.path.join(d_aux))
		os.rmdir(d)

	d_user = 'BS_' + str(BS_PORT) + '/user_' + username + '/'
	N = 0
	for files in os.listdir(os.path.join(d_user)):
		N = N + 1

	if(N == 0):
		os.rmdir(d_user)
		user_txt = 'user_' + username + '_BS.txt'
		os.remove(os.path.join(user_txt))

	if not (os.path.exists(d)):
		return 'DBR OK\n'
	else:
		return 'DBR NOK\n'

def filelist(username, direct, CS):
	p = 'BS_' + str(BS_PORT) + '/user_' + username + '/' + direct + '/'
	files = ''
	N = 0
	for filename in os.listdir(p):
		N = N + 1
		file = os.stat(os.path.join(p, filename))
		file_date = time.ctime(file.st_mtime)
		file_size = os.path.getsize(os.path.join(p, filename))

		files = files +  ' ' + convert_file_info(filename,file_date, file_size)

	serverBS.sendto(('LFD ' + str(N) + ' ' + files + '\n').encode(), CS)

#--------------------------------------------------------
#---------------------BS/USER----------------------------
def send_TCP(data):
	connection_USER.send(data.encode())

def regist_user(username, password):
	filename = 'user_' + username + '_BS.txt'
	try:
		user = open(filename, 'r')
	except IOError:
		user = open(filename, 'w')
		user.write(password)
		user.close()
		print('New User: ' + username + '\n')
		return 'AUR OK\n'
	else:
		passw = user.readline()
		if(passw == password):
			print('User: ' + username + '\n')
			send_TCP('AUR OK\n')
		else:
			send_TCP('AUR NOK\n')

def restore(username, direct):
	d = 'BS_' + str(BS_PORT) + '/user_' + username + '/' + direct + '/'
	N = 0
	for filename3 in os.listdir(d):
		N = N + 1

	connection_USER.send(('RBR ' + str(N)).encode())
	p = ''
	info_files = 'Sending ' + direct
	for filename in os.listdir(d):
		info_files = info_files + ' ' + filename
		file = os.stat(os.path.join(d, filename))
		file_date = time.ctime(file.st_mtime)
		file_size = os.path.getsize(os.path.join(d, filename))

		p = ' ' + convert_file_info(filename,file_date, file_size)

		connection_USER.send(p.encode())

		fl = open(os.path.join(d,filename), 'rb')

		s = file_size
		x = True
		while (s > BUFFER_SIZE):
			if(x):
				x = False
				data = b' ' + fl.read(BUFFER_SIZE)
				connection_USER.send(data)
				s = s - BUFFER_SIZE
			else:
				data = fl.read(BUFFER_SIZE)
				connection_USER.send(data)
				s = s - BUFFER_SIZE

		if (s <= BUFFER_SIZE):
			if (x):
				x = False
				data = b' ' + fl.read(s)
				connection_USER.send(data)
			else:
				data = fl.read(s)
				connection_USER.send(data)

	connection_USER.send(('\n').encode())
	print(info_files)
#--------------------------------------------------------
def ctrl_c_filho(sig, frame):
	sys.exit()


def ctrl_c_pai(sig, frame):
	CS = (UDP_IP, UDP_PORT)
	info = ('UNR ' + BS_IP + ' ' + str(BS_PORT) + '\n').encode()
	socketCS.sendto(info, CS)
	r_aux , addr = socketCS.recvfrom(BUFFER_SIZE)
	r = r_aux.decode()
	if(r == 'UAR OK\n'):
		sys.exit()


#--------------------------------------------------------

args = sys.argv

BS_PORT = int(args[3])

UDP_IP = args[5] #IP do CS
UDP_PORT = int(args[7]) #PORT Ddo CS

socketCS = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

BS_NAME = socket.gethostname()
BS_IP = socket.gethostbyname(BS_NAME)	#IP do BS

#registar BS no Cs
connectCS_information_aux = 'REG ' + BS_IP + ' ' + str(BS_PORT)
connectCS_information = connectCS_information_aux.encode()
socketCS.sendto((connectCS_information), (UDP_IP, UDP_PORT))
state_aux, addrCS = socketCS.recvfrom(BUFFER_SIZE)
state = state_aux.decode()


pid = os.fork()
if(pid == 0):

	signal.signal(signal.SIGINT, ctrl_c_filho)

	#TCP CONNECTION WITH USER
	s_USER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s_USER.bind((BS_IP, BS_PORT))
	s_USER.listen(1)

	while True:

		connection_USER, addr_USER = s_USER.accept()
		r_USER = ((connection_USER.recv(BUFFER_SIZE)).decode()).split()

		if(r_USER[0] == 'AUT'):
			regist_user(r_USER[1], r_USER[2])

			current_user = r_USER[1]
			user_password = r_USER[2]

		r_USER1 = ((connection_USER.recv(4)).decode()).split()	#"come" o código e o espaço a seguir

#--------------------------------------------------------------------------------BACKUP
		if (r_USER1[0] == 'UPL'):
			r_u = []
			o = 0
			m = ''
			while True:
				req = (connection_USER.recv(1)).decode()
				if not (req == ' '):
					m = m + req
				else:
					r_u.append(m) 
					o = o + 1
					m = ''
					if(o == 2):
						break

			directory = r_u[0]
			N = int(r_u[1])

			info = directory + ': '

			for i in range(N):
				k = b''
				y = 0
				f_list = []
				while True:
					information_x = connection_USER.recv(1)
					if not (information_x == b' '):
						k = k + information_x
					else:
						n = k.decode()
						f_list.append(n)
						y = y + 1
						k = b''
						if (y == 4):
							break

				bytesLidos = 0
				dados = b''
				size = int(f_list[3])

				while (size > 0):
					if (size < BUFFER_SIZE):
						file = connection_USER.recv(size)
						dados = dados + file
						bytesLidos = len(file)
						size = size - bytesLidos
					else:
						file = connection_USER.recv(BUFFER_SIZE)
						dados = dados + file
						bytesLidos = len(file)
						size = size - bytesLidos


				dirname = 'BS_' + str(BS_PORT) + '/user_' + current_user + '/' + directory + '/' 
				file_name = f_list[0]

				if not (os.path.exists(dirname)):
					os.makedirs(dirname)
					f = open(os.path.join(dirname,file_name), 'wb')
					f.write(dados)
					f.close()
				else:
					d = dirname + file_name

					if not (os.path.exists(d)):
						f = open(os.path.join(dirname,file_name), 'wb')
						f.write(dados)
						f.close()
					else:
						print("Ja guardou o ficheiro")
						

				fim = connection_USER.recv(1)
				info = info + file_name + ' ' + f_list[3] + ' BYTES received' + '\n'
			print(info)

			connection_USER.send(('UPR OK\n').encode())

#--------------------------------------------------------------------------------

		if(r_USER1[0] == 'RSB'):
			m = ''
			r_u = []
			while True:
				req = (connection_USER.recv(1)).decode()
				if not (req == '\n'):
					m = m + req
				else:
					r_u.append(m) 
					break

			directory = r_u[0]
			restore(current_user, directory)











elif(pid == -1):
	print("ERR fork")

else:

	signal.signal(signal.SIGINT, ctrl_c_pai)

	#receber do CS
	serverBS = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	serverBS.bind((BS_IP, BS_PORT))

	while True:
		request_aux, addr = serverBS.recvfrom(BUFFER_SIZE)
		CS_request = (request_aux.decode()).split()
		if(CS_request[0] == 'LSU'):
			s_aux = regist_user_CS(CS_request[1], CS_request[2])
			s = s_aux.encode()
			serverBS.sendto(s, addr)

		if(CS_request[0] == 'DLB'):
			s_aux = deletedir(CS_request[1], CS_request[2])
			s = s_aux.encode()
			serverBS.sendto(s, addr)

		if(CS_request[0] == 'LSF'):
			filelist(CS_request[1], CS_request[2], addr)

