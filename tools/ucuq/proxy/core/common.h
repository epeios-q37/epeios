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


#ifndef COMMON_INC_
# define COMMON_INC_

# include "ucucmn.h"

# include "csdcmn.h"
# include "csdbns.h"

# include "sdr.h"
# include "tol.h"
# include "sck.h"
# include "lstbch.h"


namespace common {
  using namespace ucucmn;

  qROW(Row);

  class rCaller_;

  class rCallers
  {
  private:
    mtx::rMutex Mutex_; // To protect acces to following member.
    lstbch::qLBUNCHw(rCaller_ *, sRow) List_;
  public:
    void reset(bso::sBool P = true)
    {
      if ( P ) {
        if ( Mutex_ != mtx::Undefined )
          mtx::Delete(Mutex_);
      }

      Mutex_ = mtx::Undefined;

      tol::reset(P, List_);
    }
    qCDTOR(rCallers);
    void Init(void)
    {
      reset();

      Mutex_ = mtx::Create();
      tol::Init(List_);
    }
    sRow New(sck::rRWDriver *Driver);
    void Withdraw(sRow Row); // The corresponding caller is made inaccessible and deleted if applied.
    bso::sBool Hire(
      sRow Row,
      bso::sBool *BreakFlag) const;
    sck::rRWDriver *GetDriver(
      sRow Row,
      const bso::sBool *BreakFlag) const;
    bso::sBool Release(
      sRow Row,
      const bso::sBool *BreakFlag);
  };

  inline void Test_(void)
  {}  // For future use.

  template <typename integer> integer Get(
    flw::rRFlow &Flow,
    integer &Integer)
  {
    Test_();

    return ucucmn::Get(Flow, Integer);
  }

  inline const str::dString &Get(
    flw::rRFlow &Flow,
    str::dString &String)
  {
    Test_();

    return ucucmn::Get(Flow, String);
  }

  inline const str::dStrings &Get(
    flw::rRFlow &Flow,
    str::dStrings &Strings)
  {
    Test_();

    return ucucmn::Get(Flow, Strings);
  }

  inline const str::dStrings &Get(
    flw::rRFlow &Flow,
    str::wStrings &Strings)
  {
    Test_();

    return ucucmn::Get(Flow, Strings);
  }

  inline void Put(
    const str::dString &String,
    flw::rWFlow &Flow)
  {
    Test_();

    return ucucmn::Put(String, Flow);
  }

  template <typename integer> void Put(
    integer Integer,
    flw::rWFlow &Flow)
  {
    Test_();

    return ucucmn::Put(Integer, Flow);
  }

  inline void Commit(flw::rWFlow &Flow)
  {
    Test_();

    ucucmn::Commit(Flow);
  }

  inline void Dismiss(flw::rRFlow &Flow)
  {
    Test_();

    ucucmn::Dismiss(Flow);
  }
}


#endif
