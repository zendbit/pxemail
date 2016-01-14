'''
    Author  : Amru Rosyada
    Email   : amru.rosyada@gmail.com
    License : GPL3 (http://www.gnu.org/licenses/gpl-3.0.en.html)
'''

import email
import imaplib
import smtplib
import pickle
import copy
import json
import os

from email.parser import HeaderParser
from pickle import Pickler, Unpickler

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
        
        self.__imap_local_dir = os.getcwd() + os.path.sep + 'pxemail_cache'
        
        # this will be override when call imap_set_active(host, username)
        self.__active_imap_user = {'host':'', 'username':''}
        self.__active_smtp_user = {'host':'', 'username':''}
        
    ####################################
    ####### IMAP4 FUNCTIONALITY #########
    ####################################
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
    
    def imap_serialize(self, filename):
        '''
            serialize imap object
            save it as pickle object
        '''
            
        try:
            imap_entity_dump = {}
            imap_entity = self.__imap_entity.get_all()
            
            for entity in imap_entity:
                imap_entity_item = copy.copy(imap_entity.get(entity))
                imap_entity_dump[entity] = {}
                for imap_user in imap_entity_item:
                    imap_entity_dump[entity][imap_user] = imap_entity_item.get(imap_user)
                    imap_entity_dump.get(entity).get(imap_user)['imap'] = None
            
            # serialize imap user         
            Pickler(open(filename + '.imap.entity', 'wb'), protocol=pickle.HIGHEST_PROTOCOL).dump(imap_entity_dump)
            # serialize imap directory
            Pickler(open(filename + '.imap.maildir', 'wb'), protocol=pickle.HIGHEST_PROTOCOL).dump(self.__imap_local_dir)
        except Exception as e:
            print(e)
            
    def imap_unserialize(self, filename):
        '''
            unserialize imap object
            load and init __imap_entity
        '''
        
        try:
            return {'entity':Unpickler(open(filename + '.imap.entity', 'rb')).load(),
                'maildir':Unpickler(open(filename + '.imap.maildir', 'rb')).load()}
        except Exception as e:
            print(e)
            
        return None
        
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
        
        status, msg = self.imap_get().list()
        
        try:
            msg = [mailbox.decode('UTF-8') for mailbox in msg]
        except Exception as e:
            print(e)
        
        return {'status':status, 'msg':msg}
            
    def imap_mailbox_select(self, mailbox='INBOX', readonly=False):
        '''
            select mailbox from imap object
            default is INBOX
        '''
            
        status, msg = self.imap_get().select(mailbox, readonly)
        
        return {'status':status, 'msg':msg}
    
    def imap_get_search(self, *criterion):
        '''
            do search in imap
            get email from imap object
            *criterion is for search criterion ex: 'FROM', '"LDJ"' or '(FROM "LDJ")'
        '''
        
        status, msg = self.imap_get().uid('search', None, *criterion)
        
        email_ids = []
        if len(msg):
            msg_ids = msg[0].decode('UTF-8')
            if msg_ids != '':
                email_ids = msg_ids.split(' ')
        
        return {'status':status, 'msg':email_ids}
        
    def imap_get_fetch(self, email_id, *criterion):
        '''
            do fetch email information
            for specific email_id
        '''
        
        status, msg = self.imap_get().uid('fetch', email_id, *criterion)
        
        return {'status':status, 'msg':msg}
        
    def imap_store_command(self, message_id, command, flag_list):
        '''
            store imap flags
            command should be 'FLAGS', '+FLAGS', '-FLAGS', optionaly with suffix of ."SILENT".
            flag_list must be valid flag '\\Deleted', '\\Seen' etc
        '''
        
        status, msg = self.imap_get().uid('STORE', message_id, command, flag_list)
        
        return {'status':status, 'msg':msg}
    
    def imap_expunge(self):
        '''
            commit all change command to email
            should call this after change email flag
        '''
        
        status, msg = self.imap_get().expunge()
        
        return {'status':status, 'msg':msg}
        
    def imap_get_fetch_header(self, email_id):
        '''
            get header of messages
            return parsed header messages
            parameter is email_id returned from serach result
        '''
        
        # check serialize cache
        email_cache = self.imap_unserialize_email_from_file(email_id)
        if email_cache:
            return {'status':'OK', 'msg':email_cache}
        
        email_info = self.imap_get_fetch(email_id, '(BODY[HEADER])')
        if email_info.get('status').lower() != 'ok':
            return None
        
        header = email_info.get('msg')[0][1].decode('UTF-8') #get header string then decode
        parser = HeaderParser()
        
        # serialize
        parsed_header = parser.parsestr(header)
        serialized_eml = {}
        serialized_eml['ID'] = email_id
        serialized_eml['From'] = parsed_header.get('From')
        serialized_eml['To'] = parsed_header.get('To')
        serialized_eml['CC'] = parsed_header.get('CC')
        serialized_eml['BCC'] = parsed_header.get('BCC')
        serialized_eml['Subject'] = parsed_header.get('Subject')
        serialized_eml['Date'] = parsed_header.get('Date')
        self.imap_serialize_email_to_file(serialized_eml)
            
        return {'status':'OK', 'msg':parsed_header}
        
    def imap_get_fetch_content(self, email_id, download_attachment=False):
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
        
        cache_dir = self.imap_init_serialize_dir(email_id)
        
        # check serialize cache
        email_cache = self.imap_get_fetch_header(email_id)
        if email_cache and email_cache.get('msg') and email_cache.get('msg').get('Message'):
            return email_cache
        
        email_cache = email_cache.get('msg')
        
        #email_content = {'content':[], 'attachment':[], 'inline_attachment':[]}
        email_cache['Message'] = []
        email_cache['Attachment'] = []
        email_cache['InlineAttachment'] = []
        email_cache['ID'] = email_id
        
        body = self.imap_get_fetch(email_id, '(BODY[])')
        status = body.get('status')
        data = body.get('msg')[0][1]
        email_msg = email.message_from_bytes(data)
        
        if status.lower() != 'ok':
            return None
        
        # check if download_attachment is set
        for part in email_msg.walk():
            if part.get('Content-Disposition') and download_attachment:
                # save attachment
                filename = part.get_filename()
                fp = open(filename, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
                # add attachment filename
                #email_content.get('attachment').append({'name':filename, 'mime':part.get_content_type()})
                email_cache.get('Attachment').append({'name':filename, 'mime':part.get_content_type()})
                
            # if plain text or html and not disposition
            elif part.get_content_type() == 'text/plain' or part.get_content_type() == 'text/html':
                body = part.get_payload(decode=True)
                body = body.decode()
                #email_content.get('content').append(body)
                email_cache.get('Message').append(body)
                    
            # else save as inline attachment
            # elif part.get_content_type().find('image/') != -1 or part.get_content_type().find('video/') != -1 or part.get_content_type().find('application/') != -1 or part.get('Content-Disposition'):
            elif download_attachment:
                # save attachment
                filename = part.get_filename()
                fp = open(cache_dir + os.path.sep + filename, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
                # add attachment filename
                #email_content.get('inline_attachment').append({'name':filename, 'mime':part.get_content_type()})
                email_cache.get('InlineAttachment').append({'name':filename, 'mime':part.get_content_type()})
                # append inline attachment value to content
                #email_content.get('content').append('[pxemail:inline' + filename + ']')
                email_cache.get('Message').append('[pxemail:inline' + filename + ']')
        
        # make sure content is in text
        #email_content['content'] = ''.join(email_content.get('content'))
        email_cache['Message'] = ''.join(email_cache.get('Message'))
        
        #return {'status':status, 'msg':email_content}
        self.imap_serialize_email_to_file(email_cache)
        return {'status':status, 'msg':email_cache}
    
    def imap_set_directory(self, directory):
        '''
            set imap directory
            retrieved email will save to the directory
        '''
        
        self.__imap_local_dir = directory
    
    def imap_init_serialize_dir(self, email_id):
        '''
            check if local directory for serialize already exists
            if not create it
        '''
        
        dir_path = self.__imap_local_dir + os.path.sep + self.__active_imap_user.get('username') + os.path.sep + email_id
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
            
        return dir_path
    
    def imap_unserialize_email_from_file(self, email_id):
        '''
            unserialize json from email cache to variable
        '''
        
        dir_path = self.imap_init_serialize_dir(email_id)
        file = dir_path + os.path.sep + email_id
        
        content = None
        
        '''if os.path.exists(file):
            f = open(file, 'r')
            content = f.readline()
            f.close()
            
            if content:
                content = json.loads(content)
        ''' 
        
        try:
            return Unpickler(open(file, 'rb')).load()
            
        except Exception as e:
            print(e)
               
        return content
        
    def imap_serialize_email_to_file(self, email_data):
        '''
            email_data = {
                'Subject':'',
                'CC':'',
                'BCC':'',
                'Attachment':[],
                'InlineAttachment':[],
                'ID':''
            }
        '''
        
        try:
            dir_path = self.imap_init_serialize_dir(email_data.get('ID'))
            file = dir_path + os.path.sep + email_data.get('ID')
            Pickler(open(file, 'wb'), protocol=pickle.HIGHEST_PROTOCOL).dump(email_data)
            
        except Exception as e:
            print(e)
                
    def is_email_serialized(self, email_id):
        '''
            check email data is alrady exists or not
        '''
        
        return os.path.exists(self.__imap_local_dir + os.path.sep + self.__active_imap_user.get('username') + os.path.sep + email_id)
        
    ####################################
    ####### SMTP FUNCTIONALITY #########
    ####################################
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
    
    def smtp_serialize(self, filename):
        '''
            serialize smtp object
            save it as pickle object
        '''
            
        try:
            smtp_entity_dump = {}
            smtp_entity = self.__smtp_entity.get_all()
            
            for entity in smtp_entity:
                smtp_entity_item = copy.copy(smtp_entity.get(entity))
                smtp_entity_dump[entity] = {}
                for smtp_user in smtp_entity_item:
                    smtp_entity_dump[entity][smtp_user] = smtp_entity_item.get(smtp_user)
                    smtp_entity_dump.get(entity).get(smtp_user)['smtp'] = None
            
            # serialize smtp user         
            Pickler(open(filename + '.smtp.entity', 'wb'), protocol=pickle.HIGHEST_PROTOCOL).dump(smtp_entity_dump)
        except Exception as e:
            print(e)
            
    def smtp_unserialize(self, filename):
        '''
            unserialize smtp object
            load and init __smtp_entity
        '''
        
        try:
            return {'entity':Unpickler(open(filename + '.smtp.entity', 'rb')).load()}
        except Exception as e:
            print(e)
            
        return None
            
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
    pyemail.imap_add('imap.gmail.com', 'amru.rosyada@gmail.com', 'secret', connection_type=EntityFlag.CONNECTION_SSL)
    #pyemail.imap_add('imap.gmail.com', 'amrurosyada@gmail.com', '', connection_type=EntityFlag.CONNECTION_SSL)
    #pyemail.imap_serialize('test')
    #print(pyemail.imap_unserialize('test'))
    pyemail.imap_set_active('imap.gmail.com', 'amru.rosyada@gmail.com')
    #print(pyemail.imap_is_login())
    pyemail.imap_login()
    #print(pyemail.imap_get_list())
    #print(pyemail.imap_is_login())
    pyemail.imap_mailbox_select(readonly=False)
    #filter_test = EmailFilter().set_seen().set_from('developer@insideapple.apple.com')
    filter_test = EmailFilter().set_from('developer@insideapple.apple.com')
    filter_test = filter_test.generate()
    #print(filter_test)
    emails = pyemail.imap_get_search(filter_test)
    #serialized_eml = {}
    if emails:
        for eml in emails.get('msg'):
            #print(eml)
            #print(pyemail.imap_get_fetch_header(eml))
            #print(pyemail.imap_get_fetch_header(eml).get('msg'))
            emaildata = pyemail.imap_get_fetch_content(eml).get('msg')
            if emaildata:
                print('++++++++++')
                print('From %s' % emaildata.get('From'))
                print('Subject %s' % emaildata.get('Subject'))
                print('Date %s' % emaildata.get('Date'))
    #print(serialized_eml)
    #print(pyemail.imap_get_fetch_content('30110'))
    #print(pyemail.imap_get_fetch_header('30411'))
    #print(pyemail.imap_store_command('30411', '-FLAGS', '(\Seen)'))
    #print(pyemail.imap_expunge())
    pyemail.imap_logout()
    
    #print(pyemail.imap_is_login())
    #pyemail.imap_reconnect()
    #print(pyemail.imap_is_login())
    #print(dir(pyemail.imap_get().socket()))
    #pyemail.imap_logout()
    #print(pyemail.imap_is_login())
    #pyemail.imap_add('imap.gmail.com', 'amru.rosyada@gmail.com', '', connection_type=EntityFlag.CONNECTION_SSL, force=True)
    #pyemail.imap_login()

    #message = MessageBuilder('amru.rosyada@gmail.com', ['wahyu@qajoo.com'], 'test from message manager')
    #message.attach_text('halo mas wah')
    #message.attach_application('Video.MOV')
    #pyemail.smtp_add('smtp.gmail.com', 'amru.rosyada@gmail.com', '', connection_type=EntityFlag.CONNECTION_SSL)
    #pyemail.smtp_add('smtp.gmail.com', 'amrurosyada@gmail.com', '', connection_type=EntityFlag.CONNECTION_SSL)
    #pyemail.smtp_serialize('test')
    #print(pyemail.smtp_unserialize('test'))
    #pyemail.smtp_set_active('smtp.gmail.com', 'amru.rosyada@gmail.com')
    #pyemail.smtp_login()
    #pyemail.smtp_send_message(message)
    #pyemail.smtp_logout()
