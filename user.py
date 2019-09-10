import socket
import sys
import os
import os.path
import time
import shutil

BUFFER_SIZE = 1024

#--------------------------------------------------------
#---------------------FUNCTIONS--------------------------
#--------------------USER/CS-----------------------------
def client_connect():
	s.connect((TCP_IP, TCP_PORT))

def client_disconnect():
	s.close()

def send(message):
	s.send(message.encode())

def receive():
	return (s.recv(BUFFER_SIZE)).decode()

def login(username, password):
	send('AUT ' + username + ' ' + password + '\n')
	return receive()
	

def convert_file_info(filename, data_time, file_size):
	data_time_aux = data_time.split()
	m = str(time.strptime (data_time_aux[1], '%b').tm_mon)
	d = '%02d' % int(data_time_aux[2])
	return filename + ' ' + d + '.' + m + '.' + data_time_aux[4] + ' ' + data_time_aux[3] + ' ' + str(file_size)


def backup_BS(BS_IP, BS_PORT, direct, N):
	message = b''
	s_BS.connect((BS_IP, BS_PORT))
	s_BS.send(('AUT ' + current_user + ' ' + user_password + '\n').encode())
	r_aux = s_BS.recv(BUFFER_SIZE)
	r = r_aux.decode()
	if (r == 'AUR OK\n'):
		s_BS.send(('UPL ' + direct + ' ' + str(N)).encode())
		fils = ''
		for filename2 in os.listdir(direct):
			fils = fils + filename2 + ' '
			file2 = os.stat(os.path.join(direct, filename2))
			file_date2 = time.ctime(file2.st_mtime)
			file_size2 = os.path.getsize(os.path.join(direct, filename2))

			k = (' ' + convert_file_info(filename2,file_date2, file_size2)).encode()
			s_BS.send(k)

			fl = open(os.path.join(direct,filename2), 'rb')

			x = True
			s = file_size2
			while (s > BUFFER_SIZE):
				if (x):
					x = False
					data = b' ' + fl.read(BUFFER_SIZE)
					s_BS.send(data)
					s = s - BUFFER_SIZE
				else:
					data = fl.read(BUFFER_SIZE)
					s_BS.send(data)
					s = s - BUFFER_SIZE

			if (s <= BUFFER_SIZE):
				if (x):
					x = False
					data = b' ' + fl.read(BUFFER_SIZE)
					s_BS.send(data)
				else:
					data = fl.read(BUFFER_SIZE)
					s_BS.send(data)
			fl.close()

		s_BS.send(('\n').encode())

		rbs = (s_BS.recv(BUFFER_SIZE)).decode()
		if(rbs == 'UPR OK\n'):
			print('completed - ' + direct + ': ' + fils + '\n')
		s_BS.close()


def backup(dir):
	N = 0
	files_aux = ''
	for filename in os.listdir(dir):
		N = N + 1
		file = os.stat(os.path.join(dir, filename))
		file_date = time.ctime(file.st_atime)
		file_size = os.path.getsize(os.path.join(dir, filename))
		files_aux = files_aux +  ' ' + convert_file_info(filename,file_date, file_size)

	send('BCK ' + dir + ' ' + str(N))
	files = files_aux + '\n'
	send(files)

	r = receive().split()
	if(r[0] == 'BKR'):
		if(r[1] == 'EOF'):
			print("Nenhum BS disponivel")
		else:
			print('backup to: ' + r[1] + ' ' + r[2])
			backup_BS(r[1], int(r[2]), dir, N)
	client_disconnect()


def dirlist():
	send('LSD\n')
	received_aux = ''
	while True:
		r_aux = receive()
		sizereceived = len(r_aux.encode())
		received_aux+= r_aux
		if (sizereceived <= BUFFER_SIZE):
			break
		if not (r_aux):
			break

	r = received_aux.split()
	comp = len(r)
	for i in range (2, comp):
		print(r[i])


def restore(username, drct):
	send('RST ' + drct + '\n')
	bs_aux = receive()
	bs = bs_aux.split()
	BS_IP_2 = bs[1]
	BS_PORT_2 = int(bs[2])
	mensa = 'from: ' + BS_IP_2 + ' ' + str(BS_PORT_2)
	print(mensa)

	success = 'success - ' + drct + ':'
	s_BS.connect((BS_IP_2, BS_PORT_2))
	s_BS.send(('AUT ' + current_user + ' ' + user_password + '\n').encode())
	resp = (s_BS.recv(BUFFER_SIZE)).decode()
	if (resp == 'AUR OK\n'):

		s_BS.send(('RSB ' + drct + '\n').encode())

		respo = ((s_BS.recv(4)).decode()).split()

		if(respo[0] == 'RBR'):
			m = ''
			inf_list = [] 
			while True:
				t = (s_BS.recv(1)).decode()
				if not(t == ' '):
					m = m + t
				else:
					NFiles = int(m)
					break

			for i in range (NFiles):
				z = 0
				m = ''
				info_list = []
				while True:
					info = (s_BS.recv(1)).decode()
					if not (info == ' '):
						m = m + info

					else:
						info_list.append(m)
						z = z + 1
						m = ''
						if( z == 4):
							break


				file_name = info_list[0]
				success = success + ' ' + file_name

				size = int(info_list[3])
				bytesLidos = 0
				dados = b''
				while (size > 0):
					if(size < BUFFER_SIZE):
						data = s_BS.recv(size)
						dados = dados + data
						bytesLidos = len(data)
						size = size - bytesLidos
					else:
						data = s_BS.recv(BUFFER_SIZE)
						dados = dados + data
						bytesLidos = len(data)
						size = size - bytesLidos


				dirname = 'user_' +  current_user + '/' + drct + '/'
				if not (os.path.exists(dirname)):
					os.makedirs(dirname)
					file = open(os.path.join(dirname, file_name), 'wb')
					file.write(dados)
					file.close()
				else:
					d = dirname + file_name
					if not (os.path.exists(d)):
						file = open(os.path.join(dirname, file_name), 'wb')
						file.write(dados)
						file.close()
					else:
						print('JÁ GUARDOU')

				fim = s_BS.recv(1)
	s_BS.close()
	print(success)



def deluser(username):
	send('DLU\n')
	r = receive()


def deletedir(direct):
	send('DEL ' + direct + '\n')
	r = receive()


def filelist(dir):
	send('LSF '+ dir + '\n')
	listfiles = ''
	while True:
		listreceived = receive()
		sizereceived = len(listfiles.encode())
		listfiles = listfiles + listreceived

		if (sizereceived <= BUFFER_SIZE):
			break
		if not (listreceived):
			break

	fileslist = listfiles.split()
	
	print(fileslist[1] + ' ' + fileslist[2] + ' ' + fileslist[3])
	for j in range(int(fileslist[3])):
		indice = j * 4 + 4
		print(fileslist[indice] + ' ' + fileslist[indice+1] + ' ' + fileslist[indice+2] + ' ' +fileslist[indice+3])

def exit():
	s.close()

#--------------------------------------------------------
#--------------------------------------------------------

args = sys.argv

TCP_IP = args[3]
TCP_PORT = int(args[5])

#TCP_IP = socket.gethostbyname(TCP_NAME)

while True:

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s_BS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	t = input().split()

	if (t[0] == 'login'):
		client_connect()
		if (login(t[1], t[2]) == 'AUR NEW\n'):
			print ('User '+'"'+ t[1] + '"' + ' created')

		current_user = t[1]
		user_password = t[2]
		client_disconnect()

	elif (t[0] == 'backup'):
		client_connect()
		if (login(current_user, user_password) == 'AUR OK\n'):
			backup(t[1])

	elif (t[0] == 'deluser'):
		client_connect()
		if (login(current_user, user_password) == 'AUR OK\n'):
			deluser(current_user)
		client_disconnect()

	elif (t[0] == 'restore'):
		client_connect()
		if (login(current_user, user_password) == 'AUR OK\n'):
			restore(current_user, t[1])
		client_disconnect()

	elif(t[0] == 'dirlist'):
		client_connect()
		if (login(current_user, user_password) == 'AUR OK\n'):
			dirlist()
		client_disconnect()	

	elif (t[0] == 'filelist'):
		client_connect()
		if (login(current_user, user_password) == 'AUR OK\n'):
			filelist(t[1])
		client_disconnect()
	#CONTACTA COM O BS

	elif (t[0] == 'delete'):
		client_connect()
		if (login(current_user, user_password) == 'AUR OK\n'):
			deletedir(t[1])
		client_disconnect()

	elif (t[0] == 'logout'):
		print('Logout user: ', current_user)
		current_user = ''
		user_password = ''

	elif (t[0] == 'exit'):
		exit()
		break
