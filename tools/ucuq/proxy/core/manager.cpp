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

#include "device.h"
#include "messages.h"
#include "remote.h"

#include "ucumng.h"

#include "flw.h"
#include "str.h"

using namespace manager;

namespace {
  void Close_(flw::rRWFlow &Manager)
  {
  qRH;
    str::string Token, Id;
  qRB;
    tol::Init(Token, Id);
    ucucmn::Get(Manager, Token);
    ucucmn::Get(Manager, Id);
    ucucmn::Dismiss(Manager);

    if ( Id.Amount() )
      device::WithdrawDevice(Token, Id);
    else
      device::WithdrawDevices(Token);
  qRR;
  qRT;
  qRE;
  }

  void Execute_(flw::rRWFlow &Manager)
  {
  qRH;
    flw::rDressedRWFlow<> Device;
    str::wString RToken, Id;
    str::wString Script, Expression, Message, Response;
    common::sRow Row = qNIL;
    bso::sBool Cont = true;
    bso::sBool DummyBreakFlagAsDiscrimitator = false;
  qRB;
    tol::Init(RToken, Id, Script, Expression);

    common::Get(Manager, RToken);
    common::Get(Manager, Id);
    common::Get(Manager, Script);
    common::Get(Manager, Expression);

    Row = device::Hire(RToken, Id, &DummyBreakFlagAsDiscrimitator);

    if ( Row == qNIL ) {
      Message.Init();

      messages::GetTranslation(messages::iNoDeviceWithGivenTokenAndId, Message, RToken, Id);

      common::Put(ucumng::aError, Manager);
      common::Put(Message, Manager);
      common::Commit(Manager);
    } else {

      Device.Init(device::GetDriver(Row, &DummyBreakFlagAsDiscrimitator));

      common::Put(device::rExecute, Device);
      common::Put(Script, Device);
      common::Put(Expression, Device);
      common::Commit(Device);

      if ( Expression.Amount() )
        switch ( device::GetAnswer(Device) ) {
        case device::aResult:
          Response.Init();

          common::Get(Device, Response);
          common::Dismiss(Device);

          common::Put(ucumng::aOK, Manager);
          common::Put(Response, Manager);

          common::Commit(Manager);
          break;
        case device::aSensor:
          qRUnx();
          break;
        case device::aError:
        case device::aPuzzled:
          Response.Init();

          common::Get(Device, Response);
          common::Dismiss(Device);

          common::Put(ucumng::aError, Manager);
          common::Put(Response, Manager);

          common::Commit(Manager);
          break;
        case device::aDisconnected:
          common::Dismiss(Device);
          break;
        default:
          qRGnr();
          break;
        }
    }
  qRR;
  qRT;
    DummyBreakFlagAsDiscrimitator = true;

    device::Release(Row, &DummyBreakFlagAsDiscrimitator);
  qRE;
  }

  void Create_(flw::rRWFlow &Manager)
  {
  qRH;
    str::wString
      VToken,
      RToken,
      Id;  // Can be empty.
  qRB;
    tol::Init(VToken, RToken, Id);

    ucucmn::Get(Manager, VToken);
    ucucmn::Get(Manager, RToken);
    ucucmn::Get(Manager, Id);

    ucucmn::Dismiss(Manager);

    device::CreateVToken(VToken, RToken, Id);

    ucucmn::Put(ucumng::aOK, Manager);
    ucucmn::Put(str::Empty, Manager);

    ucucmn::Commit(Manager);
  qRR;
  qRT;
  qRE;
  }

  void Delete_(flw::rRWFlow &Manager)
  {
  qRH;
    str::wString RToken, VToken;
  qRB;
    tol::Init(RToken, VToken);

    ucucmn::Get(Manager, RToken);
    ucucmn::Get(Manager, VToken);

    ucucmn::Dismiss(Manager);

    if ( VToken.Amount() )
      device::DeleteVToken(RToken, VToken);
    else
      device::DeleteVTokens(RToken);

    ucucmn::Put(ucumng::aOK, Manager);
    ucucmn::Put(str::Empty, Manager);

    ucucmn::Commit(Manager);
  qRR;
  qRT;
  qRE;
  }

  void Fetch_(flw::rRWFlow &Manager)
  {
  qRH;
    str::wString RToken;
    str::wStrings RTokenIds, VTokens, VTokenIds;
  qRB;
    RToken.Init();  

    ucucmn::Get(Manager, RToken);

    ucucmn::Dismiss(Manager);

    tol::Init(RTokenIds, VTokens, VTokenIds);
    device::GetTokensFeatures(RToken, RTokenIds, VTokens, VTokenIds);

    ucucmn::Put(ucumng::aOK, Manager);
    ucucmn::Put(str::Empty, Manager);
    ucucmn::Put(RTokenIds, Manager);
    ucucmn::Put(VTokens, Manager);
    ucucmn::Put(VTokenIds, Manager);

    ucucmn::Commit(Manager);
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
  case ucumng::rClose_1:
    Close_(Flow);
    break;
  case ucumng::rExecute_1:
    Execute_(Flow);
    break;
  case ucumng::rCreate_1:
    Create_(Flow);
    break;
  case ucumng::rDelete_1:
    Delete_(Flow);
    break;
  case ucumng::rFetch_1:
    Fetch_(Flow);
    break;
  default:
    qRGnr();
    break;
  }
qRR;
qRT;
qRE;
}
