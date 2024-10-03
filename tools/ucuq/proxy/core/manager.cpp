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


#include "manager.h"

#include "backend.h"

#include "ucumng.h"

#include "flw.h"
#include "str.h"

using namespace manager;

namespace {
  void CloseDevices_(flw::rRWFlow &Flow)
  {
  qRH;
    str::string Token;
  qRB;
    Token.Init();
    ucucmn::Get(Flow, Token);
    ucucmn::Dismiss(Flow);

    backend::Withdraw(Token);
  qRR;
  qRT;
  qRE;
  }
}

void manager::Process(fdr::rRWDriver &Driver)
{
qRH;
  flw::rDressedRWFlow<> Flow;
  str::wString RawRequest;
qRB;
Flow.Init(Driver);

  RawRequest.Init();
  ucucmn::Get(Flow, RawRequest);

  switch ( ucumng::GetRequest(RawRequest) ) {
  case ucumng::rCloseDevices:
    CloseDevices_(Flow);
    break;
  default:
    qRGnr();
    break;
  }
qRR;
qRT;
qRE;
}
