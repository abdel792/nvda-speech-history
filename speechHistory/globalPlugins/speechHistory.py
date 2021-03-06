# NVDA Add-on: Speech History
# Copyright (C) 2012 Tyler Spivey
# Copyright (C) 2015-2017 James Scholes
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2).
# See the file LICENSE for more details.

import addonHandler
import api
import globalPluginHandler
from queueHandler import eventQueue, queueFunction
import speech
import tones
import ui

from globalCommands import SCRCAT_SPEECH

addonHandler.initTranslation()

oldSpeak = speech.speak
oldSpeakSpelling = speech.speakSpelling
data = ''
history = []
history_pos = 0

def append_to_history(string):
    global history, history_pos
    if len(history) == 100:
        history.pop()
    history.insert(0, string)
    history_pos = 0

def mySpeak(sequence, *args, **kwargs):
    global data
    text = u''.join([x for x in sequence if isinstance(x, basestring)])
    if text:
        data = text
        oldSpeak(sequence, *args, **kwargs)
        queueFunction(eventQueue, append_to_history, text)

def mySpeakSpelling(text, *args, **kwargs):
    global data
    if text:
        data = text
    oldSpeakSpelling(text, *args, **kwargs)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self, *args, **kwargs):
        super(GlobalPlugin, self).__init__(*args, **kwargs)
        global oldSpeak, oldSpeakSpelling
        oldSpeak = speech.speak
        speech.speak = mySpeak
        oldSpeakSpelling = speech.speakSpelling
        speech.speakSpelling = mySpeakSpelling

    def script_copyLast(self, gesture):
        if api.copyToClip(history[history_pos]):
            tones.beep(1500, 120)

    # Translators: Documentation string for copy currently selected speech history item script
    script_copyLast.__doc__ = _('Copy the currently selected speech history item to the clipboard, which by default will be the most recently spoken text by NVDA.')
    script_copyLast.category = SCRCAT_SPEECH

    def script_prevString(self, gesture):
        global history_pos
        history_pos += 1
        if history_pos > len(history) - 1:
            tones.beep(200, 100)
            history_pos -= 1

        oldSpeak([history[history_pos]])

    # Translators: Documentation string for previous speech history item script
    script_prevString.__doc__ = _('Review the previous item in NVDA\'s speech history.')
    script_prevString.category = SCRCAT_SPEECH

    def script_nextString(self, gesture):
        global history_pos
        history_pos -= 1
        if history_pos < 0:
            tones.beep(200, 100)
            history_pos += 1

        oldSpeak([history[history_pos]])

    # Translators: Documentation string for next speech history item script
    script_nextString.__doc__ = _('Review the next item in NVDA\'s speech history.')
    script_nextString.category = SCRCAT_SPEECH

    def terminate(self):
        speech.speak = oldSpeak
        speech.speakSpelling = oldSpeakSpelling

    __gestures = {
        "kb:f12":"copyLast",
        "kb:shift+f11":"prevString",
        "kb:shift+f12":"nextString",
    }
