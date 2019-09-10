# RC Cloud Backup - Programming using the Sockets interface

O projeto "RC Cloud Backup" foi desenvolvido em python, sendo constituido por tres ficheiros: user.py (User Application), cs.py (Central Server) e bs.py (Backup Server).
Os ficheiros devem ser executados da seguinte forma:
User Application: python3 user.py ./user [-n CSname] [-p CSport]
Central Server: python3 cs.py ./CS [-p CSport]
Backup Server: python3 bs.py ./BS [-b BSport] [-n CSname] [-p CSport]