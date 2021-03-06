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

import workshop._.z_1 as workshop
import workshop.de._ as _
from workshop.de.display import *


class _Core(_.Core):
    bodyI18n = {
        "Solve": "Lösen",
        "Solution": "Lösung"
    }
    i18n = {
        "BadValue": "Nur Zahlen zwischen 100 und -100 sind erlaubt!",
        "ACannotBe0": "'a' kann nicht Null sein!"
    }

    def __init__(self, dom):
        _.Core.__init__(self, dom)


def go(function, handleError):
    workshop.main(function, lambda dom: _Core(
        dom), _.defaultTitle, handleError)
