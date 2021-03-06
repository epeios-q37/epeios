/*
	Copyright (C) 2018 by Claude SIMON (http://zeusw.org/epeios/contact.html).

	This file is part of 'esketchcli'.

    'esketchcli' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'esketchcli' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'esketchcli'.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef ESKETCHCLI_INC_
# define ESKETCHCLI_INC_

# include "sktinf.h"

# include "scli.h"

# define NAME_MC			SKTINF_MC "cli"
# define NAME_LC			SKTINF_LC "cli"
# define NAME_UC			SKTINF_UC "CLI"
# define WEBSITE_URL		SKTINF_WEBSITE_URL
# define AUTHOR_NAME		SKTINF_AUTHOR_NAME
# define AUTHOR_CONTACT		SKTINF_AUTHOR_CONTACT
# define OWNER_NAME			SKTINF_OWNER_NAME
# define OWNER_CONTACT		SKTINF_OWNER_CONTACT
# define COPYRIGHT			COPYRIGHT_YEARS " " OWNER_NAME " (" OWNER_CONTACT ")"	

SCLI_DEC( esketchcli );

#endif