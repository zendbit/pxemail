'''
    Author  : Amru Rosyada
    Email   : amru.rosyada@gmail.com
    License : GPL3
'''

import imaplib
import smtplib
imaplib.__MAXLINE = 10000000

class EntityFlag(object):
    '''
        EntityFlag with code
    '''
    ERROR_USER_EXIST = 1000
    ERROR_USER_NOT_EXIST = ERROR_USER_EXIST + 1
    ERROR_USER_LOGIN = ERROR_USER_NOT_EXIST + 1
    ERROR_USER_LOGOUT = ERROR_USER_LOGIN + 1
    
    ERROR_UNKNOWN_HOST = 2000
    
    SUCCESS_USER_LOGIN = 4000
    SUCCESS_USER_LOGOUT = SUCCESS_USER_LOGIN + 1
    
    SUCCESS_ADD_NEW_USER = 5000
    
    CONNECTION_PLAIN = 1
    CONNECTION_SSL = 2
    CONNECTION_LMTP = 3

class IMAPEntity(object):
    '''
        imap user model representation
    '''
    
    def __init__(self):
        '''
            create imap user object
            with no parameter
        '''
        
        self.__imap_entity = {}
        
    def is_entity_exist(self, host, username):
        '''
            check if user exist in IMAPEntity
            return True if exist
        '''
        
        if not self.__imap_entity.get(host):
            return False
            
        if not self.__imap_entity.get(host).get(username):
            return False
            
        return True
        
    def add(self, host, username, password, port=imaplib.IMAP4_PORT,
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
                value should be one of EntityFlag.CONNECTION_PLAIN|EntityFlag.CONNECTION_SSL
        '''
        
        if self.is_entity_exist(host, username):
            if not force:
                return EntityFlag.ERROR_USER_EXIST
        
        if not self.__imap_entity.get(host):
            self.__imap_entity[host] = {}
                 
        # imap is imap object
        # also auto create imap object when add imap user
        try:
            if connection_type == EntityFlag.CONNECTION_SSL:
                if port == imaplib.IMAP4_PORT:
                    port = imaplib.IMAP4_SSL_PORT
                imap = imaplib.IMAP4_SSL(host, port, keyfile, certfile, ssl_context)
            else:
                imap = imaplib.IMAP4(host, port)
                
        except imaplib.IMAP4.error as e:
            return EntityFlag.ERROR_UNKNOWN_HOST
             
        self.__imap_entity.get(host)[username] = {
            'password':password,
            'port':port,
            'connection_type':connection_type,
            'keyfile':keyfile,
            'certfile':certfile,
            'ssl_context':ssl_context,
            'imap':imap,
            'is_login':False}
        
        return EntityFlag.SUCCESS_ADD_NEW_USER
        
    def get(self, host, username=None):
        
        '''
            get user imap configuration
            depend on host and username selector
            if configuration not exist will return None
            if username nost set will return list of imap user
        '''
        
        imap_user = self.__imap_entity.get(host)
        
        # if username not set return list of imap user
        if not username:
            return imap_user
        
        # if username exist return imap user config
        if imap_user.get(username):
            return imap_user.get(username)
            
        return None
        
    def get_imap(self, host, username):
        
        '''
            get user imap configuration
            depend on host and username selector
            will return imap object for login and manipulating email
            if not exist return None
        '''
        
        imap_user = self.__imap_entity.get(host)
        
        # if username exist return imap user config
        if imap_user.get(username):
            return imap_user.get(username).get('imap')
            
        return None


class SMTPEntity(object):
    '''
        smtp user model representation
    '''
    
    def __init__(self):
        '''
            create smtp entity object
            with no parameter
        '''
        
        self.__smtp_entity = {}
        
    def add(self, host, username, password, port=smtplib.SMTP_PORT, local_hostname=None, source_address=None,
        connection_type=EntityFlag.CONNECTION_PLAIN, keyfile=None, certfile=None, context=None, force=False):
            
        '''
            add smtp entity to __smtp_entity
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
        
        if not self.__smtp_entity.get(host):
            self.__smtp_entity[host] = {}
        
        # check if user exist then return false if not force edit config    
        if self.__smtp_entity.get(host).get(username):
            if not force:
                return EntityFlag.ERROR_USER_EXIST
                 
        # smtp is smtp object
        # also auto create smtp object when add smtp user
        try:
            # SMTP SSL type
            if connection_type == EntityFlag.CONNECTION_SSL:
                if port == smtplib.SMTP_PORT or port == smtplib.LMTP_PORT:
                    port = smtplib.SMTP_SSL_PORT
                    
                smtp = smtplib.SMTP_SSL(host=host,
                    port=port,
                    local_hostname=local_hostname,
                    keyfile=keyfile,
                    certfile=certfile,
                    context=context,
                    source_address=source_address)
            # LMTP
            elif connection_type == EntityFlag.CONNECTION_LMTP:
                if port == smtplib.SMTP_PORT or port == smtplib.SMTP_SSL_PORT:
                    port = smtplib.LMTP_PORT
                    
                smtp = smtplib.LMTP(host, port, local_hostname, source_address)
            # SMTP PLAIN
            else:
                smtp = smtplib.SMTP(host=host,
                    port=port,
                    local_hostname=local_hostname,
                    source_address=source_address)
                
        except smtplib.SMTPException:
            return SMTPUser.ERROR_UNKNOWN_HOST
             
        self.__smtp_entity.get(host)[username] = {
            'password':password,
            'port':port,
            'local_hostname':local_hostname,
            'source_address':source_address,
            'keyfile':keyfile,
            'certfile':certfile,
            'context':context,
            'smtp':smtp,
            'is_login':False}
        
        return True
        
    def get(self, host, username=None):
        '''
            get user smtp configuration
            depend on host and username selector
            if configuration not exist will return None
            if username nost set will return list of smtp user
        '''
        
        smtp_entity = self.__smtp_entity.get(host)
        
        # if username not set return list of smtp user
        if not username:
            return smtp_entity
        
        # if username exist return smtp user config
        if smtp_entity.get(username):
            return smtp_entity.get(username)
            
        return None
        
    def get_smtp(self, host, username):
        '''
            get user smtp configuration
            depend on host and username selector
            will return smtp object for login and manipulating email
            if not exist return None
        '''
        
        smtp_entity = self.__smtp_entity.get(host)
        
        # if username exist return smtp user config
        if smtp_entity.get(username):
            return smtp_entity.get(username).get('smtp')
            
        return None
