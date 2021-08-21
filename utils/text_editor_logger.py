import logging
from PyQt5.QtCore import QObject, pyqtSignal


class QTextEditLogger(logging.Handler, QObject):
    appendPlainText = pyqtSignal(str)

    def __init__(self, widget):
        super().__init__()
        QObject.__init__(self)
        # self.widget = QtWidgets.QPlainTextEdit(parent)
        # self.widget.setReadOnly(True)
        self.appendPlainText.connect(widget.append)

        self._time_formarter = '<span style="color: blue">'

        self._error_formarter = '<span style="color: red; font-weight: 600;">'

        self._info_formarter = '<span style="color: green; font-weight: 600;">'

        self._message_formarter = '<span style="color: #0aadef">'

        self._end_formarter = '</span>'

    def emit(self, record):
        msg = self.format(record)
        send_msg = ''
        if msg is not None:
            split_msg = msg.split('-split-')
            if split_msg[1] == ' INFO ':
                send_msg = self._time_formarter + split_msg[0] + self._end_formarter + self._info_formarter +\
                           split_msg[1] + self._end_formarter + self._message_formarter + split_msg[2] + self._end_formarter
            else:
                send_msg = self._time_formarter + split_msg[0] + self._end_formarter + self._error_formarter + \
                           split_msg[1] + self._end_formarter + self._message_formarter + split_msg[
                               2] + self._end_formarter
        self.appendPlainText.emit(send_msg)
