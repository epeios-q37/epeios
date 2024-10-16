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


#include "remote.h"

#include "registry.h"
#include "messages.h"
#include "device.h"

#include "sclm.h"

#include "csdcmn.h"

using namespace remote;

namespace {
  qENUM(Request_) { // Request issued by remote (received as string)
    rPing_1,
    rExecute_1,
    r_amount,
    r_Undefined
  };

#define C( name )	case r##name : return #name; break

  const char *GetLabel_(eRequest_ Request)
  {
    switch ( Request ) {
      C(Ping_1);
      C(Execute_1);
    default:
      qRFwk();
      break;
    }

    return NULL;	// To avoid a warning.
  }

#undef C

    stsfsm::wAutomat RemoteRequestAutomat_;

    void FillRemoteRequestAutomat_(void)
    {
      RemoteRequestAutomat_.Init();
      stsfsm::Fill<eRequest_>(RemoteRequestAutomat_, r_amount, GetLabel_);
    }

  eRequest_ GetRequest_(const str::dString &Pattern)
  {
    return stsfsm::GetId(Pattern, RemoteRequestAutomat_, r_Undefined, r_amount);
  }

  eRequest_ GetRequest_(flw::rRFlow &Flow)
  {
    eRequest_ Request = r_Undefined;
  qRH;
    str::wString RawRequest;
  qRB;
    RawRequest.Init();

    common::Get(Flow, RawRequest);

    Request = GetRequest_(RawRequest);
  qRR;
  qRT;
  qRE;
    return Request;
  }

  bso::sBool HandlePing_(
    flw::rRWFlow &Remote,
    flw::rRWFlow &Device,
    common::gTracker *Tracker)
  {
    bso::sBool Cont = true;
   qRH;
    str::wString Returned;
  qRB;
    common::Put(device::rPing, Device, Tracker);
    common::Commit(Device, Tracker);

    switch ( device::GetAnswer(Device, Tracker) ) {
    case device::aOK:
      Returned.Init();
      common::Get(Device, Returned, Tracker);
      common::Put(device::aOK, Remote);
      common::Put(Returned, Remote);
      common::Commit(Remote);
      break;
    case device::aPuzzled:
      Returned.Init();
      common::Get(Device, Returned, Tracker);
      common::Put(device::aPuzzled, Remote);
      common::Put(Returned, Remote);
      common::Commit(Remote);
      break;
    case device::aDisconnected:
      Cont = false;
      break;
    default:
      qRGnr();
      break;
    }
  qRR;
  qRT;
  qRE;
    return Cont;
  }

  bso::sBool HandleExecute_(
    flw::rRWFlow &Remote,
    flw::rRWFlow &Device,
    const common::gTracker *Tracker)
  {
    bso::sBool Cont = true;
  qRH;
    str::wString
      Script,     // Script to execute.
      Expression, // Expression to evaluate which result if JSONified and returned.
      Returned;   // Result of the JSONified evaluation the expression, or exception description if an error occured.
  qRB;
    tol::Init(Script, Expression);

    common::Get(Remote, Script);
    common::Get(Remote, Expression);

    common::Put(device::rExecute, Device, Tracker);
    common::Put(Script, Device, Tracker);
    common::Put(Expression, Device, Tracker);
    common::Commit(Device, Tracker);

    switch ( device::GetAnswer(Device, Tracker) ) {
    case device::aOK:
      Returned.Init();
      common::Get(Device, Returned, Tracker);
      common::Put(device::aOK, Remote);
      common::Put(Returned, Remote);
      common::Commit(Remote);
      break;
    case device::aError:
      Returned.Init();
      common::Get(Device, Returned, Tracker);
      common::Put(device::aError, Remote);
      common::Put(Returned, Remote);
      common::Commit(Remote);
      break;
    case device::aPuzzled:
      Returned.Init();
      common::Get(Device, Returned, Tracker);
      common::Put(device::aPuzzled, Remote);
      common::Put(Returned, Remote);
      break;
    case device::aDisconnected:
      Cont = false;
      break;
    default:
      qRGnr();
      break;
    }
  qRR;
  qRT;
  qRE;
    return Cont;
  }
}

void remote::Process(fdr::rRWDriver &Driver)
{
qRH;
  flw::rDressedRWFlow<> Device;
  flw::rDressedRWFlow<> Remote;
  str::wString Message, Command;
  device::wSelector Selector;
  common::rCaller *Caller = NULL;
  bso::sBool Cont = true;
  common::gTracker Tracker;
qRB;
  Remote.Init(Driver);

  Selector.Init();
  common::Get(Remote, Selector.Token);
  common::Get(Remote, Selector.Id);

  Caller = device::Hire(Selector, &Driver);

  Remote.Init(Driver);

  if ( Caller == NULL ) {
    Message.Init();
    messages::GetTranslation(messages::iNoDeviceWithGivenTokenAndId, Message, Selector.Token, Selector.Id);
    common::Put(Message, Remote);
    common::Commit(Remote);
  } else {
    common::Put("", Remote);
    common::Commit(Remote);

    Tracker.Candidate = &Driver;
    Tracker.Caller = Caller;

    Device.Init(*Caller->GetDriver());

    while ( !Remote.EndOfFlow() && Cont ) {
      switch ( GetRequest_(Remote) ) {
      case rExecute_1:
        if ( !HandleExecute_(Remote, Device, &Tracker) )
          break;
        break;
      case rPing_1:
        if ( !HandlePing_(Remote, Device, &Tracker) )
          break;
        break;
      default:
        qRGnr();
        break;
      }
      common::Dismiss(Device, &Tracker);
    }
   }
  qRR;
  qRT;
    if ( (Caller != NULL) && Caller->ShouldIDestroy(&Driver) ) {
      Device.reset(false); // To avoid action on underlying driver which will be destroyed.
      qDELETE(Caller);
    }
  qRE;
}

qGCTOR(remote)
{
  FillRemoteRequestAutomat_();
}
