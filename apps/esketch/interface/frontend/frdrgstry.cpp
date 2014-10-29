/*
	'frdrgstry.cpp' by Claude SIMON (http://zeusw.org/).

	 This file is part of 'eSketch' software.

    'eSketch' is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'eSketch' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with 'eSketch'.  If not, see <http://www.gnu.org/licenses/>.
*/

// $Id: frdrgstry.cpp,v 1.1 2012/12/04 15:46:27 csimon Exp $

#include "frdrgstry.h"
#include "sclrgstry.h"

#include "flf.h"
#include "fnm.h"

using namespace frdrgstry;

static entry___ XSLFilesSet_( "XSLFilesSet", sclrgstry::Parameters );
static entry___ FreeXSLFiles_( "XSLFiles", XSLFilesSet_ );
static entry___ TaggedXSLFiles(RGSTRY_TAGGING_ATTRIBUTE("target"), FreeXSLFiles_ );

entry___ frdrgstry::XSLContentFile("Content", TaggedXSLFiles );
entry___ frdrgstry::XSLPaddingsFile("Paddings", TaggedXSLFiles );

