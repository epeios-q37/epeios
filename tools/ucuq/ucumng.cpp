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

#include "ucumng.h"

#include "stsfsm.h"

using namespace ucumng;

#define C( name )	case r##name : return #name; break

const char *ucumng::GetLabel(eRequest Request)
{
  switch ( Request ) {
    C(Close_1);
    C(Execute_1);
    C(CreateVToken_1);
    C(DeleteVToken_1);
  default:
    qRFwk();
    break;
  }

  return NULL;	// To avoid a warning.
}

namespace {
  stsfsm::wAutomat RequestAutomat_;

  void FillRequestAutomat_(void)
  {
    RequestAutomat_.Init();
    stsfsm::Fill<eRequest>(RequestAutomat_, r_amount, GetLabel);
  }
}

eRequest ucumng::GetRequest(const str::dString &Pattern)
{
  return stsfsm::GetId(Pattern, RequestAutomat_, r_Undefined, r_amount);
}

qGCTOR(ucumng)
{
  FillRequestAutomat_();
}
