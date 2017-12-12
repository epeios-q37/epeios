/*
	Copyright (C) 2017 Claude SIMON (http://zeusw.org/epeios/contact.html).

	This file is part of 'XDHq' software.

    'XDHq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'XDHq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'XDHq'.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef SERVER_INC_
# define SERVER_INC_

# include "flw.h"
# include "str.h"

namespace server {
	void Handshake(
		flw::sRFlow &Flow,
		str::dString &Language );

	void GetAction(
		flw::sRWFlow &Flow,
		str::dString &Id,
		str::dString &Action );

#define SERVER_SETP_ 	const str::dString &, const str::dString &, const str::dString &, const char *, flw::sWFlow &Flow

	typedef void(* fSet)( SERVER_SETP_ );

	void SetLayout( SERVER_SETP_ );

	void GetContents(
		const str::dStrings &Ids,
		flw::sRWFlow &Flow,
		str::dStrings &Contents );

	void SetContents(
		const str::dStrings &Ids,
		const str::dStrings &Contents,
		flw::sWFlow &Flow );

	void SetCasts(
		const str::dString &Id,
		const str::dStrings &Tags,
		const str::dStrings &Values,
		flw::sWFlow &Flow );

	void GetAttribute(
		const str::dString &Id,
		const str::dString &Name,
		flw::sRWFlow &Flow,
		str::dString &Value );

	void SetAttribute(
		const str::dString &Id,
		const str::dString &Name,
		const str::dString &Value,
		flw::sWFlow &Flow );

	void GetProperty(
		const str::dString &Id,
		const str::dString &Name,
		flw::sRWFlow &Flow,
		str::dString &Value );

	void SetProperty(
		const str::dString &Id,
		const str::dString &Name,
		const str::dString &Value,
		flw::sWFlow &Flow );
}

#endif