@echo off
REM
REM		This file is part of 'eSketch' software.
REM
REM    'eSketch' is free software: you can redistribute it and/or modify
REM    it under the terms of the GNU General Public License as published by
REM    the Free Software Foundation, either version 3 of the License, or
REM    (at your option) any later version.
REM
REM    'eSketch' is distributed in the hope that it will be useful,
REM    but WITHOUT ANY WARRANTY; without even the implied warranty of
REM    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
REM    GNU General Public License for more details.
REM
REM    You should have received a copy of the GNU General Public License
REM    along with 'eSketch'.  If not, see <http://www.gnu.org/licenses/>.
REM

REM barq -s localhost:2000 ogzapi.xml
barq -e h:\bin\esketchbkd frdapi.xml
sabcmd file://H:\hg\epeios\stable\frd4cpp.xsl frdapi.xml frdapi.h
