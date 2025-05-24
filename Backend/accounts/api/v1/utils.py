# utility
import threading


class EmailThread(threading.Thread):
    """
    This class extends threading.Thread to send an email asynchronously in a separate thread.
    """

    def __init__(self, email_obj):
        threading.Thread.__init__(self)
        self.email_obj = email_obj

    def run(self):
        self.email_obj.send()
