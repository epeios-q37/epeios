/*
	Copyright (C) 2022 Claude SIMON (http://q37.info/contact/).

	This file is part of the 'mscfdraftq' tool.

    'mscfdraftq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'mscfdraftq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'mscfdraftq'.  If not, see <http://www.gnu.org/licenses/>.
*/


#include "tsqchrns.h"

#include "stsfsm.h"

using namespace tsqchrns;

#define C( name )	case t##name : return #name; break

const char *tsqchrns::GetLabel(eType Type)
{
	switch ( Type ) {
	C( Pending );
	C( Completed );
	C( Due );
	C( Event );
	default:
		qRFwk();
		break;
	}

	return NULL;	// To avoid a warning.
}

#undef C

namespace {
	stsfsm::wAutomat TypeAutomat_;

	void FillTypeAutomat_( void )
	{
		TypeAutomat_.Init();
		stsfsm::Fill<eType>(TypeAutomat_, t_amount, GetLabel);
	}
}

eType tsqchrns::GetType(const str::dString &Pattern)
{
	return stsfsm::GetId(Pattern, TypeAutomat_, t_Undefined, t_amount);
}

qGCTOR( tsqchrns )
{
	FillTypeAutomat_();
}



