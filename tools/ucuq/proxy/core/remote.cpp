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
#include "modules.h"

#include "sclm.h"

#include "csdcmn.h"

#include "mtk.h"


using namespace remote;

namespace {
  qENUM(Request_) { // Request issued by remote (received as string)
    rExecute_1,
    rUpload_1,
    r_amount,
    r_Undefined
  };

#define C( name )	case r##name : return #name; break

  const char *GetLabel_(eRequest_ Request)
  {
    switch ( Request ) {
      C(Execute_1);
      C(Upload_1);
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

  namespace {
    void Execute_(
      const str::dString &Module,
      const str::dString &Expression,
      flw::rWFlow &Device,
      const common::gTracker *Tracker)
    {
      bso::sBool Cont = true;
    qRH;
      str::wString Returned;   // Result of the JSONified evaluation the expression, or exception description if an error occured.
    qRB;
      common::Put(device::rExecute, Device, Tracker);
      common::Put(Module, Device, Tracker);
      common::Put(Expression, Device, Tracker);
      common::Commit(Device, Tracker);
    qRR;
    qRT;
    qRE;
    }

  }

  bso::sBool Execute_(
    flw::rRFlow &Remote,
    flw::rWFlow &Device,
    const common::gTracker *Tracker)
  {
    bso::sBool Cont = true;
  qRH;
  str::wString
    Module,     // Module to execute.
    Expression; // Expression to evaluate which result if JSONified and returned.
  qRB;
    tol::Init(Module, Expression);

    common::Get(Remote, Module);
    common::Get(Remote, Expression);

    Execute_(Module, Expression, Device, Tracker);
  qRR;
  qRT;
  qRE;
    return Cont;
  }

  namespace {
    void EleminateDuplicates_(str::dStrings &Strings)
    {
      sdr::sRow Row = Strings.Last();

      while ( Row != qNIL ) {
        if ( str::Search(Strings(Row), Strings) != Row ) {
          if ( Strings.Last() == Row ) {
            Row = Strings.Previous(Row);

            Strings.Remove(Strings.Last());
          }
          else {
            Strings.Remove(Row);

            Row = Strings.Previous(Row);
          }
        } else {
          Row = Strings.Previous(Row);
        }
      }
    }
        
    void GetGlobalModule_(
      str::dStrings &ModuleNames,
      str::dString &GlobalModule)
    {
      ctn::qCMITEMsl(str::dString) Name;
      sdr::sRow Row = ModuleNames.First();

      Name.Init(ModuleNames);

      while ( Row != qNIL ) {
        modules::GetModule(Name(Row), GlobalModule, ModuleNames);

        Row = ModuleNames.Next(Row);
      }
    }
  }

  bso::sBool Upload_(
    flw::rRFlow &Remote,
    flw::rWFlow &Device,
    const common::gTracker *Tracker)
  {
    bso::sBool Cont = true;
  qRH;
    str::wStrings ModuleNames;     // Modules to upload.
    str::wString Module, Returned;
  qRB;
    ModuleNames.Init();

    common::Get(Remote, ModuleNames, Tracker);

    EleminateDuplicates_(ModuleNames);

    Module.Init();

    GetGlobalModule_(ModuleNames, Module);

    Execute_(Module, str::Empty, Device, Tracker);
  qRR;
  qRT;
  qRE;
    return Cont;
  }
}

namespace routine_ {
  namespace process_ {
    void RemoteToDevice(
      flw::rRFlow &Remote,
      flw::rWFlow &Device,
      const common::gTracker *Tracker)
    {
      while ( !Remote.EndOfFlow() ) {
        switch ( GetRequest_(Remote) ) {
        case rExecute_1:
          if ( !Execute_(Remote, Device, Tracker) )
            break;
          break;
        case rUpload_1:
          if ( !Upload_(Remote, Device, Tracker) )
            break;
          break;
        default:
          qRGnr();
          break;
        }
      }
    }
    
    void DeviceToRemote(
      flw::rRFlow &Device,
      flw::rWFlow &Remote,
      const common::gTracker *Tracker)
    {
    qRH;
      str::wString Returned;   // Result of the JSONified evaluation the expression, or exception description if an error occured.
    qRB;
      while ( true ) {
        switch ( device::GetAnswer(Device, Tracker) ) {
        case device::aResult:
          Returned.Init();
          common::Get(Device, Returned, Tracker);
          common::Put(device::aResult, Remote);
          common::Put(Returned, Remote);
          common::Commit(Remote);
          break;
        case device::aSensor:
          qRVct();
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
          break;
        default:
          qRGnr();
          break;
        }
        common::Dismiss(Device, Tracker);
      }
    qRR;
    qRT;
    qRE;
    }
  }

  namespace data {
    struct gRemoteToDevice
    {
      flw::rRFlow *Remote;
      flw::rWFlow *Device;
      const common::gTracker *Tracker;
      gRemoteToDevice(void)
      {
        Remote = NULL;
        Device = NULL;
        Tracker = NULL;
      }
    };
  
    struct gDeviceToRemote
    {
      flw::rRFlow *Device;
      flw::rWFlow *Remote;
      const common::gTracker *Tracker;
      gDeviceToRemote(void)
      {
        Device = NULL;
        Remote = NULL;
        Tracker = NULL;
      }
    };
  }

  void RemoteToDevice(
    data::gRemoteToDevice &Data,
    mtk::gBlocker &Blocker)
  {
    flw::rRFlow &Remote = *Data.Remote;
    flw::rWFlow &Device = *Data.Device;
    const common::gTracker *Tracker = Data.Tracker;

    Blocker.Release();

    process_::RemoteToDevice(Remote, Device, Tracker);
  }

  void DeviceToRemote(
    data::gDeviceToRemote &Data,
    mtk::gBlocker &Blocker)
  {
    flw::rRFlow &Device = *Data.Device;
    flw::rWFlow &Remote = *Data.Remote;
    const common::gTracker *Tracker = Data.Tracker;

    Blocker.Release();

    process_::DeviceToRemote(Device, Remote, Tracker);
  }
}

void remote::Process(sck::rRWDriver &RemoteDriver)
{
qRH;
  flw::rDressedRWFlow<> Device;
  flw::rDressedRWFlow<> Remote;
  str::wString Message, Command;
  str::wString RToken, Id;
  common::rCaller *Caller = NULL;
  bso::sBool Cont = true;
  common::gTracker Tracker;
  routine_::data::gRemoteToDevice RemoteToDeviceData;
  routine_::data::gDeviceToRemote DeviceToRemoteData;
qRB;
  Remote.Init(RemoteDriver);

  tol::Init(RToken, Id);
  common::Get(Remote, RToken);
  common::Get(Remote, Id);

  Caller = device::Hire(RToken, Id, (const void *) &RemoteDriver);  // '&RemoteDriver' serves only as discriminator.

  Remote.Init(RemoteDriver);

  if ( Caller == NULL ) {
    Message.Init();
    messages::GetTranslation(messages::iNoDeviceWithGivenTokenAndId, Message, RToken, Id);
    common::Put(Message, Remote);
    common::Commit(Remote);
  } else {
    common::Put("", Remote);
    common::Commit(Remote);

    Tracker.Candidate = &RemoteDriver;
    Tracker.Caller = Caller;

    common::Dismiss(Remote, &Tracker);

    Device.Init(*Caller->GetDriver());

    RemoteToDeviceData.Remote = &Remote;
    RemoteToDeviceData.Device = &Device;
    RemoteToDeviceData.Tracker = &Tracker;

    mtk::Launch<routine_::data::gRemoteToDevice>(routine_::RemoteToDevice, RemoteToDeviceData);

    DeviceToRemoteData.Device = &Device;
    DeviceToRemoteData.Remote = &Remote;
    DeviceToRemoteData.Tracker = &Tracker;

    mtk::Launch<routine_::data::gDeviceToRemote>(routine_::DeviceToRemote, DeviceToRemoteData);

    while ( true )
      tht::Suspend(1000);
  }
qRR;
qRT;
  if ( (Caller != NULL) && Caller->ShouldIDestroy(&RemoteDriver) ) {
    Device.reset(false); // To avoid action on underlying driver which will be destroyed.
    qDELETE(Caller);
  }
qRE;
}

qGCTOR(remote)
{
  FillRemoteRequestAutomat_();
}
