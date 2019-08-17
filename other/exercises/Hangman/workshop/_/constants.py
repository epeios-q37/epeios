# coding: utf-8
""" 
MIT License

Copyright (c) 2019 Claude SIMON (https://q37.info/s/rmnmqd49)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

P_FACE = "Face"
P_HEAD = "Head"
P_TRUNK = "Trunk"
P_LEFT_ARM = "LeftArm"
P_RIGHT_ARM = "RightArm"
P_LEFT_LEG = "LeftLeg"
P_RIGHT_LEG = "RightLeg"

F_PICK_WORD = "PickWord"
F_IS_LETTER_IN_WORD = "IsLetterInWord"
F_GET_MASK = "GetMask"
F_UPDATE_BODY = "UpdateBody"
F_RESET = "Reset"
F_HANDLE_GUESS = "HandleGuess"
F_HANGMAN = "Hangman"   # Instancies a new user object.

S_RESTART = "Restart"
S_SECRET_WORD = "SecretWord"
S_LETTER = "Letter"
S_EXPECTED = "Expected"
S_OBTAINED = "Obtained"
S_TRUE = "True"
S_FALSE = "False"