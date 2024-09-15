/*
	Copyright (C) 2021 Claude SIMON (http://q37.info/contact/).

	This file is part of the 'McRq' tool.

    'McRq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'McRq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'McRq'.  If not, see <http://www.gnu.org/licenses/>.
*/


#ifndef COMMON_INC_
# define COMMON_INC_

# include "csdcmn.h"
# include "csdbns.h"

# include "sdr.h"
# include "tol.h"
# include "sck.h"
# include "lstbch.h"


namespace common {
  qENUM(Action) {
    aContinue,
    aStopAndDelete,
    aStopAndKeep,
    a_amount,
    a_Undefined
  };

  class cProcessing {
  protected:
    virtual eAction COMMONProcess(flw::rRWFlow &Flow) = 0;
  public:
    eAction Process(flw::rRWFlow& Flow)
    {
      return COMMONProcess(Flow);
    }
    qCALLBACK(Processing);
  };

  qENUM(Target) {
    tClient,
    tServer,
    t_amount,
    t_Undefined
  };

  struct rItem_ {
  public:
    tol::sTimeStamp TimeStamp;
    sck::rRWDriver* Driver;
    void reset(bso::sBool P = true)
    {
      TimeStamp = 0;

      if ( P ) {
        qDELETE(Driver);
      }

      Driver = NULL;
    }
    qCDTOR(rItem_);
    void Init(sck::rRWDriver* Driver)
    {
      qDELETE(this->Driver);

      this->Driver = Driver;
      TimeStamp = tol::EpochTime(false);
    }
  };

  // TODO: Mutex to protect access of 'Items_'.
  class rHandler
  {
  private:
    lstbch::qLBUNCHw(rItem_ *, sdr::sRow) Items_;
  public:
    void reset(bso::sBool P = true)
    {
      Items_.reset(P);
    }
    qCDTOR(rHandler);
    void Init(void)
    {
      reset();

      Items_.Init();
    }
    sdr::tRow New(sck::sSocket Socket);
    void Delete(sdr::sRow Row);
    sck::rRWDriver& Get(sdr::tRow Row);
    void Process(
      csdbns::sService Service,
      const char* ProtocolId,
      csdcmn::sVersion ProtocolLastVersion,
      eTarget ProtocolTarget,
      cProcessing& Processing);
    sdr::tRow Get(void) const;
  };

  inline const str::dString &Get(
    flw::rRFlow &Flow,
    str::dString &String)
  {
    return csdcmn::Get(Flow, String);
  }

  inline void Put(
    const str::dString &String,
    flw::rWFlow &Flow)
  {
    return csdcmn::Put(String, Flow);
  }
}

#endif
