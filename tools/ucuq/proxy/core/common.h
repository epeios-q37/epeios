/*
  Copyright (C) 2024 Claude SIMON (http://q37.info/contact/).

  This file is part of the 'UCUq' tool.

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


#ifndef COMMON_INC_
# define COMMON_INC_

# include "csdcmn.h"
# include "csdbns.h"

# include "sdr.h"
# include "tol.h"
# include "sck.h"
# include "lstbch.h"


namespace common {
  qENUM(Caller) {
    cFrontend,
    cBackend,
    c_amount,
    c_Undefined
  };

  const char *GetLabel(eCaller Caller);

  eCaller GetCaller(const str::dString &Pattern);

  struct rCaller {
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
    qCDTOR( rCaller );
    void Init(sck::rRWDriver* Driver)
    {
      qDELETE(this->Driver);

      this->Driver = Driver;
      TimeStamp = tol::EpochTime(false);
    }
  };

  // TODO: Mutex to protect access of 'Callers_'.
  class rCallers
  {
  private:
    lstbch::qLBUNCHw(rCaller *, sdr::sRow) List_;
  public:
    void reset(bso::sBool P = true)
    {
      List_.reset(P);
    }
    qCDTOR(rCallers);
    void Init(void)
    {
      reset();

      List_.Init();
    }
    sdr::tRow New(sck::rRWDriver *Driver);
    void Delete(sdr::sRow Row);
    sck::rRWDriver& Get(sdr::tRow Row);
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
