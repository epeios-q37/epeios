/*
	Copyright (C) 2022 Claude SIMON (http://q37.info/contact/).

	This file is part of the 'TASq' tool.

    'TASq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'TASq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'TASq'.  If not, see <http://www.gnu.org/licenses/>.
*/


#include "tsqstts.h"

#include "stsfsm.h"

using namespace tsqstts;

#define C( name )	case t##name : return #name; break

const char *tsqstts::GetLabel(eType Type)
{
	switch ( Type ) {
	C( Timeless );
	C( Event );
	C( Timely );
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

eType tsqstts::GetType(const str::dString &Pattern)
{
	return stsfsm::GetId(Pattern, TypeAutomat_, t_Undefined, t_amount);
}

#define C( name )	case u##name : return #name; break

const char *tsqstts::GetLabel(eUnit Unit)
{
	switch ( Unit ) {
	C( Day );
	C( Week );
	C( Month );
	C( Year );
	default:
		qRFwk();
		break;
	}

	return NULL;	// To avoid a warning.
}

#undef C

namespace {
	stsfsm::wAutomat UnitAutomat_;

	void FillUnitAutomat_( void )
	{
		UnitAutomat_.Init();
		stsfsm::Fill<eUnit>(UnitAutomat_, u_amount, GetLabel);
	}
}

eUnit tsqstts::GetUnit(const str::dString &Pattern)
{
	return stsfsm::GetId(Pattern, UnitAutomat_, u_Undefined, u_amount);
}



qGCTOR( tsqstts )
{
	FillTypeAutomat_();
	FillUnitAutomat_();
}



