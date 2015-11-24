'''
Author  : Amru Rosyada
Email   : amru.rosyada@gmail.com
License : GPL3
'''

class EmailFilter(object):
    '''
        this is filter builder that will return filter
    '''
    
    def __init__(self):
        self.__filter_email = []
        
    def set_all(self):
        '''
            Returns all messages in the folder.
            You may run in to imaplib size limits if you request all the messages in a large folder.
            See Size Limits.
        '''
        
        self.__filter_email.append('ALL')
        return self
        
    def set_before(self, date):
        '''
            These three search keys return, respectively,messages that were received by the IMAP server before given date.
            The date must be formatted like 05-Jul-2015.
        '''
        
        self.__filter_email.append('BEFORE ' + date)
        return self
        
    def set_since(self, date):
        '''
            These three search keys return, respectively,messages that were received by the IMAP server since given date.
            The date must be formatted like 05-Jul-2015.
        '''
        
        self.__filter_email.append('SINCE ' + date)
        return self
        
    def set_on(self, date):
        '''
            These three search keys return, respectively,messages that were received by the IMAP server on given date.
            The date must be formatted like 05-Jul-2015.
        '''
        
        self.__filter_email.append('ON ' + date)
        return self
        
    def set_subject(self, text):
        '''
            add filter by subject that contain in text
            if text contain space add double quote:
            ex: '"amru rosyada"'
        '''
        
        self.__filter_email.append('SUBJECT ' + text)
        return self
        
    def set_body(self, text):
        '''
            add filter that body contain in text
            if text contain space add double quote:
            ex: '"amru rosyada"'
        '''
        
        self.__filter_email.append('BODY ' + text)
        return self
        
    def set_text(self, text):
        '''
            add filter that contain text
            if text contain space add double quote:
            ex: '"amru rosyada"'
        '''
        
        self.__filter_email.append('TEXT ' + text)
        return self
        
    def set_from(self, from_addr):
        '''
            add filter from address
            if more than one address should be user double quote
            '"amru.rosyada@gmail.com amru.rosyada@hotmail.com"'
        '''
        
        self.__filter_email.append('FROM ' + from_addr)
        return self
        
    def set_cc(self, cc_addr):
        '''
            add filter bb address
            if more than one address should be user double quote
            '"amru.rosyada@gmail.com amru.rosyada@hotmail.com"'
        '''
        
        self.__filter_email.append('CC ' + cc_addr)
        return self
        
    def set_bcc(self, bcc_addr):
        '''
            add filter bcc address
            if more than one address should be user double quote
            '"amru.rosyada@gmail.com amru.rosyada@hotmail.com"'
        '''
        
        self.__filter_email.append('BCC ' + bcc_addr)
        return self
        
    def set_seen(self):
        '''
            add filter seen
            filter all email with flag \Seen
        '''
        
        self.__filter_email.append('SEEN')
        return self
        
    def set_unseen(self):
        '''
            add filter unseen
            filter all email without flag \Seen
        '''
        
        self.__filter_email.append('UNSEEN')
        return self
        
    def set_answered(self):
        '''
            add filter answered
            Returns all messages with the \Answered flag
        '''
        
        self.__filter_email.append('ANSWERED')
        return self
        
    def set_unanswered(self):
        '''
            add filter unanswered
            Returns all messages without the \Answered flag
        '''
        
        self.__filter_email.append('UNANSWERED')
        return self
        
    def set_deleted(self):
        '''
            add filter deleted
            Returns all messages with the \Deleted flag
        '''
        
        self.__filter_email.append('DELETED')
        return self
        
    def set_undeleted(self):
        '''
            add filter undeleted
            Returns all messages without the \Deleted flag
        '''
        
        self.__filter_email.append('UNDELETED')
        return self
        
    def set_draft(self):
        '''
            add filter draft
            Returns all messages with the \Draft flag
        '''
        
        self.__filter_email.append('DRAFT')
        return self
        
    def set_undraft(self):
        '''
            add filter undraft
            Returns all messages without the \Draft flag
        '''
        
        self.__filter_email.append('UNDRAFT')
        return self
        
    def set_flagged(self):
        '''
            add filter flagged
            Returns all messages with the \Flagged flag
        '''
        
        self.__filter_email.append('FLAGGED')
        return self
        
    def set_unflagged(self):
        '''
            add filter unflagged
            Returns all messages without the \Flagged flag
        '''
        
        self.__filter_email.append('UNFLAGGED')
        return self
        
    def set_larger(self, n_bytes):
        '''
            add filter larger than n_bytes
        '''
        
        self.__filter_email.append('LARGER')
        return self
        
    def set_smaller(self, n_bytes):
        '''
            add filter smaller than n_bytes
        '''
        
        self.__filter_email.append('SMALLER')
        return self
        
    def set_not(self, search_key):
        '''
            Returns the messages that search-key would not have returned
        '''
        
        self.__filter_email.append('NOT')
        return self
        
    def set_or(self, search_key):
        '''
            Returns the messages that match either the first or second search-key
        '''
        
        self.__filter_email.append('OR')
        return self
        
    def generate(self):
        '''
            return all into list of filter
            then reset all value to empty
        '''
        
        return ' '.join(self.__filter_email).strip()
