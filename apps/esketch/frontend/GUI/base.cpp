/*
	Copyright (C) 2018 Claude SIMON (http://zeusw.org/epeios/contact.html).

	This file is part of 'eSketch' software.

    'eSketch' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'eSketch' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'eSketch'.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "base.h"

#include "core.h"
#include "login.h"
#include "main.h"
#include "prolog.h"

using namespace base;

E_CDEF(char *, base:: Name, NAME);

void base::Register(
	const char *Name,
	cAction &Callback )
{
	core::Core.AddActionCallback( Name, Callback );
}