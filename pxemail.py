from email.parser import HeaderParser
import email
import imaplib
import smtplib

from emailentity import IMAPEntity, SMTPEntity, EntityFlag
from emailfilter import EmailFilter
from messagebuilder import MessageBuilder

class PxEmail(object):
    '''
        python helper for email manipulation
        - retrieve email using imap connection
        - sending email using smtp
        - support for ssl connection
    '''
    
    def __init__(self):
        '''
            create imap object constructor
            with no parameter
            imap_user is ImapUser object
        '''
        
        self.__imap_entity = IMAPEntity()
        self.__smtp_entity = SMTPEntity()
        
        # this will be override when call imap_set_active(host, username)
        self.__active_imap_user = {'host':'', 'username':''}
        self.__active_smtp_user = {'host':'', 'username':''}
        
    def imap_add(self, host, username, password, port=imaplib.IMAP4_PORT,
        connection_type=EntityFlag.CONNECTION_PLAIN, keyfile=None, certfile=None, ssl_context=None, force=False):
        '''
            add imap user to __imap_user
            host = 'ex@mail.com'
            username = 'jhondoe@mail.com'
            password = 'secret'
            port = 143 (default is imap port or custom port depend on connection preference)
            force = False (default is false, to not override existing user), if exist will return false
                True will force existing user with new configuration
                    
            connection_type = EntityFlag.CONNECTION_PLAIN (if connection using ssl, may need keyfile, certfile, ssl_context parameter)
                value should be one of EntityFlag.CONNECTION_PLAIN|CONNECTION_SSL
        '''
        
        return self.__imap_entity.add(host, username, password, port,
            connection_type, keyfile, certfile, ssl_context, force)
            
    def imap_get_user(self, host, username=None):
        '''
            get user imap configuration
            depend on host and username selector
            if configuration not exist will return None
            if username nost set will return list of imap user
        '''
        
        return self.__imap_entity.get(host, username)
        
    def imap_set_active(self, host, username):
        '''
            set current active user
            all imap operation and modification will depend on current active user
        '''
        
        self.__active_imap_user['host'] = host
        self.__active_imap_user['username'] = username
        
    def imap_get(self):
        '''
            get user imap object
            depend on host and username selector
        '''
        
        host = self.imap_get_active().get('host')
        username = self.imap_get_active().get('username')
        return self.__imap_entity.get_imap(host, username)
        
    def imap_is_connected(self):
        '''
            check if conneected to server or not
            online or not
        '''
        
        try:
            imap_get().noop()
            return True
        except Exception:
            return False
            
    def imap_reconnect(self):
        '''
            reconnect imap
            this is force to re login
            and init imap object with new one
            
            but check with imap_is_connected before do force connect
        '''
        
        self.imap_logout()
        
        host = self.imap_get_active().get('host')
        username = self.imap_get_active().get('username')
        imap_user = self.imap_get_user(host, username)
        
        self.imap_add(
            host,
            username,
            imap_user.get('password'),
            imap_user.get('port'),
            imap_user.get('connection_type'),
            imap_user.get('keyfile'),
            imap_user.get('certfile'),
            imap_user.get('ssl_context'),
            force=True)
            
        return self.imap_login()
        
    def imap_get_active(self):
        '''
            get active user
            will return host and user name as dictionary
        '''
        
        return self.__active_imap_user
            
    def imap_is_login(self):
        '''
            check if current active user already execure login command
            if already login return true
        '''
        
        host = self.imap_get_active().get('host')
        username = self.imap_get_active().get('username')
        return self.imap_get_user(host, username).get('is_login')
        
    def imap_login(self):
        '''
            login to imap using host and username
            will search in imap user list
            if not exist will return imap user not exist error code
            if success will return SUCCESS_USER_LOGIN flag
        '''
        
        imap = self.imap_get()
        
        host = self.imap_get_active().get('host')
        username = self.imap_get_active().get('username')
        password = self.__imap_entity.get(host, username).get('password')
        
        # do login if imap user exist
        if imap:
            try:
                imap.login(username, password)
                self.imap_get_user(host, username)['is_login'] = True
                return EntityFlag.SUCCESS_USER_LOGIN
                
            except imaplib.IMAP4.error as e:
                print(e)
                return EntityFlag.ERROR_USER_LOGIN
            
        return EntityFlag.ERROR_USER_NOT_EXIST
        
    def imap_logout(self):
        '''
            logout from specific imap object
            return
            EntityFlag.SUCCESS_USER_LOGOUT|EntityFlag.SUCCESS_USER_LOGOUT
        '''
        
        try:
            host = self.imap_get_active().get('host')
            username = self.imap_get_active().get('username')
            self.imap_get_user(host, username)['is_login'] = False
            self.imap_get().close()
            self.imap_get().logout()
            self.imap_get().shutdown()
            return EntityFlag.SUCCESS_USER_LOGOUT
        except Exception:
            return EntityFlag.ERROR_USER_LOGOUT
        
        
    def imap_get_list(self):
        '''
            return list of mailbox list
            directory default to top level
            pattern default match to any
        '''
        
        return self.imap_get().list()
            
    def imap_mailbox_select(self, mailbox='INBOX', readonly=False):
        '''
            select mailbox from imap object
            default is INBOX
        '''
            
        self.imap_get().select(mailbox, readonly)
    
    def imap_get_search(self, *criterion):
        '''
            do search in imap
            get email from imap object
            *criterion is for search criterion ex: 'FROM', '"LDJ"' or '(FROM "LDJ")'
        '''
        
        return self.imap_get().uid('search', None, *criterion)
        
    def imap_get_fetch(self, email_id, *criterion):
        '''
            do fetch email information
            for specific email_id
        '''
        
        return self.imap_get().uid('fetch', email_id, *criterion)
        
    def imap_get_fetch_header(self, email_id):
        '''
            get header of messages
            return parsed header messages
            parameter is email_id returned from serach result
        '''
        
        status, header = self.imap_get_fetch(email_id, '(BODY[HEADER])')
        if status.lower() != 'ok':
            return None
        
        header = header[0][1].decode('UTF-8') #get header string then decode
        parser = HeaderParser()
        return parser.parsestr(header)
        
    def imap_get_fetch_content(self, email_id):
        '''
            get email content
            return email content with attachment filename
            format
            {
                'content':'',
                attachment:[
                    {'name':attachment01, 'mime':''},
                    {'name':attachment01, 'mime':''}
                ],
                inline_attachment:[
                    {'name':attachment01, 'mime':''},
                    {'name':attachment01, 'mime':''}
                ]
            }
        '''
        
        status, data = pyemail.imap_get_fetch(email_id, '(BODY[])')
        
        email_msg = email.message_from_bytes(data[0][1])
        if status.lower() != 'ok':
            return None
        
        email_content = {'content':[], 'attachment':[], 'inline_attachment':[]}
        
        for part in email_msg.walk():
            if part.get('Content-Disposition'):
                # save attachment
                filename = part.get_filename()
                fp = open(filename, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
                # add attachment filename
                email_content.get('attachment').append({'name':filename, 'mime':part.get_content_type()})
                
            # if plain text or html and not disposition
            elif part.get_content_type() == 'text/plain' or part.get_content_type() == 'text/html':
                body = part.get_payload(decode=True)
                body = body.decode()
                email_content.get('content').append(body)
                    
            # else save as inline attachment
            # elif part.get_content_type().find('image/') != -1 or part.get_content_type().find('video/') != -1 or part.get_content_type().find('application/') != -1 or part.get('Content-Disposition'):
            else:
                # save attachment
                filename = part.get_filename()
                fp = open(filename, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
                # add attachment filename
                email_content.get('inline_attachment').append({'name':filename, 'mime':part.get_content_type()})
                # append inline attachment value to content
                email_content.get('content').append('[pxemail:inline' + filename + ']')
                
        # make sure content is in text
        email_content['content'] = ''.join(email_content.get('content'))
        return email_content
        
    def smtp_add(self, host, username, password, port=smtplib.SMTP_PORT, local_hostname=None, source_address=None,
        connection_type=EntityFlag.CONNECTION_PLAIN, keyfile=None, certfile=None, context=None, force=False):
        '''
            add smtp user to __smtp_user
            host = 'ex@mail.com'
            username = 'jhondoe@mail.com'
            password = 'secret'
            port = 25 (default is imap port or custom port depend on connection preference)
            local_hostname = If specified, local_hostname is used as the FQDN of the local host in the HELO/EHLO command.
                Otherwise, the local hostname is found using socket.getfqdn().
            source_address = If the connect() call returns anything other than a success code, an SMTPConnectError is raised
                The optional source_address parameter allows to bind to some specific source address in a machine with multiple network interfaces, and/or to some specific source TCP port.
                It takes a 2-tuple (host, port), for the socket to bind to as its source address before connecting.
                If omitted (or if host or port are '' and/or 0 respectively) the OS default behavior will be used.    
            force = False (default is false, to not override existing user), if exist will return false
                    True will force existing user with new configuration
                    
            connection_type = EntityFlag.CONNECTION_PLAIN (if connection using ssl, may need keyfile, certfile, ssl_context parameter)
                value should be one of connection_type=EntityFlag.CONNECTION_PLAIN|connection_type=EntityFlag.CONNECTION_SSL|connection_type=EntityFlag.CONNECTION_LMTP
        '''
        
        return self.__smtp_entity.add(host, username, password, port, local_hostname, source_address,
            connection_type, keyfile, certfile, context, force)
        
    def smtp_get_user(self, host, username=None):
        '''
            get user smtp configuration
            depend on host and username selector
            if configuration not exist will return None
            if username host set will return list of smtp user
        '''
        
        return self.__smtp_entity.get(host, username)
        
    def smtp_get(self):
        '''
            get user smtp object
            depend on host and username selector
        '''
        
        host = self.smtp_get_active().get('host')
        username = self.smtp_get_active().get('username')
        return self.__smtp_entity.get_smtp(host, username)
        
    def smtp_set_active(self, host, username):
        '''
            set current active user
            all smtp operation and modification will depend on current active user
        '''
        
        self.__active_smtp_user['host'] = host
        self.__active_smtp_user['username'] = username
        
    def smtp_get_active(self):
        '''
            get active user
            will return host and user name as dictionary
        '''
        
        return self.__active_smtp_user
        
    def smtp_login(self):
        '''
            login to smtp using host and username
            will search in imap user list
            if not exist will return smtp user not exist error code
            if success will return SUCCESS_USER_LOGIN flag
        '''
        
        smtp = self.smtp_get()
        
        host = self.smtp_get_active().get('host')
        username = self.smtp_get_active().get('username')
        password = self.__smtp_entity.get(host, username).get('password')
        
        # do login if imap user exist
        if smtp:
            try:
                smtp.login(username, password)
                self.smtp_get_user(host, username)['is_login'] = True
                return EntityFlag.SUCCESS_USER_LOGIN
                
            except smtplib.SMTPException as e:
                print(e)
                return EntityFlag.ERROR_USER_LOGIN
            
        return EntityFlag.ERROR_USER_NOT_EXIST
        
    def smtp_logout(self):
        '''
            logout from specific smtp object
            return
            EntityFlag.SUCCESS_USER_LOGOUT|EntityFlag.SUCCESS_USER_LOGOUT
        '''
        
        try:
            host = self.smtp_get_active().get('host')
            username = self.smtp_get_active().get('username')
            self.smtp_get_user(host, username)['is_login'] = False
            self.smtp_get().close()
            self.smtp_get().logout()
            self.smtp_get().shutdown()
            return EntityFlag.SUCCESS_USER_LOGOUT
        except Exception:
            return EntityFlag.ERROR_USER_LOGOUT
            
    def smtp_send_message(self, message):
        '''
            send message with option
            message = implementation of MessageBuilder object
            else is optional message which is like send_message method from smptlib
        '''
        
        self.smtp_get().send_message(message.generate(), from_addr=None, to_addrs=None, mail_options=message.get_mail_options(), rcpt_options=message.get_rcpt_options())
        
if __name__ == '__main__':
    pyemail = PxEmail()
    #pyemail.imap_add('imap.gmail.com', 'amru.rosyada@gmail.com', '', connection_type=EntityFlag.CONNECTION_SSL)
    #pyemail.imap_set_active('imap.gmail.com', 'amru.rosyada@gmail.com')
    #print(pyemail.imap_is_login())
    #pyemail.imap_login()
    #print(pyemail.imap_is_login())
    #pyemail.imap_mailbox_select()
    #filter_test = EmailFilter().set_from('amru.rosyada@gmail.com').set_all()
    #filter_test = filter_test.generate()
    #print(pyemail.imap_get_fetch_content('30110'))
            
    #pyemail.imap_logout()
    #print(pyemail.imap_is_login())
    #pyemail.imap_reconnect()
    #print(pyemail.imap_is_login())
    #print(dir(pyemail.imap_get().socket()))
    #pyemail.imap_logout()
    #print(pyemail.imap_is_login())
    #pyemail.imap_add('imap.gmail.com', 'amru.rosyada@gmail.com', '', connection_type=EntityFlag.CONNECTION_SSL, force=True)
    #pyemail.imap_login()

    message = MessageBuilder('amru.rosyada@gmail.com', ['wahyu@qajoo.com'], 'test from message manager')
    message.attach_text('halo mas wah')
    message.attach_application('Video.MOV')
    pyemail.smtp_add('smtp.gmail.com', 'amru.rosyada@gmail.com', '', connection_type=EntityFlag.CONNECTION_SSL)
    pyemail.smtp_set_active('smtp.gmail.com', 'amru.rosyada@gmail.com')
    pyemail.smtp_login()
    pyemail.smtp_send_message(message)
    pyemail.smtp_logout()
