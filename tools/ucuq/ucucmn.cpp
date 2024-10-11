/*
  Copyright (C) 2024 Claude SIMON (http://q37.info/contact/).

  This file is part of the 'UCUq' toolkit.

  'UCUq' is free software: you can redistribute it and/or modify it
  under the terms of the GNU Affero General Public License as published
  by the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  'UCUq' is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with 'UCUq'.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "ucucmn.h"

#include "stsfsm.h"

using namespace ucucmn;

qCDEF(char *, ucucmn::protocol::Id, "c37cc83e-079f-448a-9541-5c63ce00d960");

#define C( name )	case c##name : return #name; break

const char *ucucmn::GetLabel(eCaller Caller)
{
	switch ( Caller ) {
		C(Admin);
		C(Manager);
		C(Remote);
		C(Device);
	default:
		qRFwk();
		break;
	}

	return NULL;	// To avoid a warning.
}

#undef C

namespace {
	stsfsm::wAutomat CallerAutomat_;

	void FillCallerAutomat_(void)
	{
		CallerAutomat_.Init();
		stsfsm::Fill<eCaller>(CallerAutomat_, c_amount, GetLabel);
	}
}

eCaller ucucmn::GetCaller(const str::dString &Pattern)
{
	return stsfsm::GetId(Pattern, CallerAutomat_, c_Undefined, c_amount);
}

qGCTOR(ucucmn)
{
	FillCallerAutomat_();
}
