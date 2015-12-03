'''
    Author  : Amru Rosyada
    Email   : amru.rosyada@gmail.com
    License : GPL3 (http://www.gnu.org/licenses/gpl-3.0.en.html)
'''

import smtplib, os
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.message import MIMEMessage

from email.utils import COMMASPACE, formatdate
from email import encoders


class MessageBuilder(object):
    '''
        build email to make it easy to send
    '''
    
    def __init__(self, msg_from, msg_to, msg_subject):
        '''
            msg_from = 'amru.rosyada@gmail.com'
            msg_to = ['john@gmail.com', 'doe@gmail.com']
            msg_subject = 'Good Morning'
        '''
        
        self.__message = MIMEMultipart()
        self.__message['From'] = msg_from
        self.__message['To'] = COMMASPACE.join(msg_to)
        self.__message['Subject'] = msg_subject
            
        self.__message_attachment = []
        
        self.__rcpt_options = []
        self.__mail_options = []
        
    def set_CC(self, CC):
        '''
            CC should be in list string of email address format
            CC = ['a@domain.com', 'b@domain.com']
        '''
        
        self.__message['CC'] = COMMASPACE.join(CC)
        return self
        
    def set_BCC(self, BCC):
        '''
            BCC should be in list string of email address format
            BCC = ['a@domain.com', 'b@domain.com']
        '''
        
        self.__message['BCC'] = COMMASPACE.join(BCC)
        return self
        
    def set_mail_options(self, mail_options=[]):
        '''
            add mail options
            options is like send_mail options
            see smtplib send_mail
            should be in list
        '''
        
        self.__mail_options = mail_options
        return self
        
    def get_mail_options(self):
        return self.__mail_options
        
    def set_rcpt_options(self, rcpt_options=[]):
        '''
            add recepient options
            options is like send_mail options
            see smtplib send_mail
        '''
        
        self.__rcpt_options = rcpt_options
        return self
        
    def get_rcpt_options(self):
        return self.__rcpt_options
            
    def attach_application(self, file_path, mime_type='octet-stream', encoder=encoders.encode_base64, disposition=True, **param):
        '''
            attach application
            example:
                attach_application('/home/amru/timesheet.xlsx')
        '''

        self.__message_attachment.append({
                'file':file_path,
                'mime_type':mime_type,
                'encoder':encoder,
                'param':param,
                'disposition':disposition,
                'type':'application'
            })
            
        return self
        
    def attach_text(self, text, mime_type='plain', charset=None, disposition=False):
        '''
            attach text can be as disposition or not
            default is not disposition
            if disposition True, text should be to file_path, like '/home/amru/test.txt'
        '''

        self.__message_attachment.append({
                'file':text,
                'mime_type':mime_type,
                'charset':charset,
                'disposition':disposition,
                'type':'text'
            })
            
        return self

    def attach_image(self, file_path, mime_type=None, encoder=encoders.encode_base64, disposition=True, **params):
        '''
            attach image
            example:
                attach_image('/home/amru/timesheet.png')
        '''

        self.__message_attachment.append({
                'file':file_path,
                'mime_type':mime_type,
                'encoder':encoder,
                'param':param,
                'disposition':disposition,
                'type':'image',
            })
            
        return self
        
    def attach_message(self, message_obj, mime_type='rfc822', disposition=True):
        '''
            attach message
            example:
                attach_message(message_obj)
        '''

        self.__message_attachment.append({
                'msg':message_obj,
                'mime_type':mime_type,
                'disposition':disposition,
                'type':'message',
            })
            
        return self

    def attach_audio(self, file_path, mime_type=None, encoder=encoders.encode_base64, disposition=True, **param):
        '''
            attach audio
            example:
                attach_audio('/home/amru/timesheet.ogg')
        '''

        self.__message_attachment.append({
                'file':file_path,
                'mime_type':mime_type,
                'encoder':encoder,
                'param':param,
                'disposition':disposition,
                'type':'audio'
            })
            
        return self

    def attach_base(self, file_path, mime_main='application', mime_type='octet-stream', encoder=encoders.encode_base64, disposition=True, **param):
        '''
            attach base
            example:
                attach_base('/home/amru/timesheet.ogg', 'audio/ogg-vorbis')
        '''

        self.__message_attachment.append({
                'file':file_path,
                'main_mime':mime_main,
                'mime_type':mime_type,
                'encoder':encoder,
                'param':param,
                'disposition':disposition,
                'type':'base'
            })

        return self
        
    def generate(self):
        '''
            generate message to send with send message
        '''

        for attachment in self.__message_attachment:
            part = None
            f = None
            
            if attachment.get('type') == 'application':
                f = open(attachment.get('file'), 'rb')
                part = MIMEApplication(
                    f.read(),
                    attachment.get('mime_type'),
                    attachment.get('encoder'),
                    **attachment.get('param'))
                    
            elif attachment.get('type') == 'image':
                f = open(attachment.get('file'), 'rb')
                part = MIMEImage(
                    f.read(),
                    attachment.get('mime_type'),
                    attachment.get('encoder'),
                    **attachment.get('param'))
            
            elif attachment.get('type') == 'audio':
                f = open(attachment.get('file'), 'rb')
                part = MIMEAudio(
                    f.read(),
                    attachment.get('mime_type'),
                    attachment.get('encoder'),
                    **attachment.get('param'))
            
            elif attachment.get('type') == 'base':
                f = open(attachment.get('file'), 'rb')
                part = MIMEBase(
                    attachment.get('mime_main'),
                    attachment.get('mime_type'))
                part.set_payload(open(attachment.get('file'), "rb").read())
                attachment.get('encoder')(part)
                    
            elif attachment.get('type') == 'message':
                part = MIMEMessage(
                    attachment.get('msg'),
                    attachment.get('mime_type'))
                                    
            elif attachment.get('type') == 'text':
                if os.path.isfile(attachment.get('file')):
                    f = open(attachment.get('file'), 'rb')
                    part = MIMEText(
                        f.read(),
                        attachmentEncoders.encode_base64.get('mime_type'),
                        attachment.get('charset'))
                        
                else:
                    part = MIMEText(
                        attachment.get('file'),
                        attachment.get('mime_type'),
                        attachment.get('charset'))
            
            if part:            
                if attachment.get('disposition') and f:
                    part.add_header('Content-Disposition', 'attachment; filename="' + f.name + '"')
                    
                self.__message.attach(part)

            if f:
                f.close()

        return self.__message