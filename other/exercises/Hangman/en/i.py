# coding: utf-8

import sys
sys.path.append(".")
from workshop.en.i import *

DISCLOSE_SECRET_WORD = TRUE


def pickWord(*args):
  return workshop.rfPickWord(*args)


def isLetterInWord(*args):
    return workshop.rfIsLetterInWord(*args)


def getMask(*args):
    return workshop.rfGetMask(*args)


def updateBody(*args):
  return workshop.rfUpdateBody(*args)


"""
Let's introduce object-oriented programmation.
Class name must be 'Hangman',
but variables and methods name are free.
"""
class Hangman:
  def reset(self):
    self.goodGuesses = ""
    self.errorsAmount = 0

  def __init__(self):
    self.reset()

  """
  Update the good guesses ot the amount of errors wether 'guess' is
  good ot not. Return TRUE if 'guess' is good, FALSE otherwise.
  """
  def handleAndTestGuess(self,guess,secretWord):
    if isLetterInWord(guess,secretWord):
      if not isLetterInWord(guess,self.goodGuesses):
        self.goodGuesses += guess
      return TRUE
    else:
      self.errorsAmount += 1
      return FALSE


"""
Same as previous exercise, but this time we use an object. 
"""
def reset(hangman,suggestion,randomWord):
  hangman.reset()
  secretWord = pickWord(suggestion,randomWord)
  print(secretWord)
  eraseAndDisplay(getMask(secretWord,""))

  return secretWord


"""
Idem.
"""
def handleGuess(hangman,guess,secretWord):
  if hangman.handleAndTestGuess(guess):
    eraseAndDisplay(getMask(secretWord,hangman.goodGuesses))
  else:
    updateBody(hangman.errorsAmount)

go(globals())
