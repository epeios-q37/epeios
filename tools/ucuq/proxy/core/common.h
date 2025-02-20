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

  class rCaller {
  private:
    mtx::rMutex Mutex_; // To protect access to below two members.
    const void *UserDiscriminator_;   // 'NULL' if no it in use, otherwise a pointer which value is specific to the user which uses it.
    bso::sBool IsAlive_;  // The device behind is available.
    sck::rRWDriver *Driver_;
    sRow Row_;
  public:
    tol::sTimeStamp TimeStamp;
    void reset(bso::sBool P = true)
    {
      if ( P ) {
        qDELETE(Driver_);

        if ( Mutex_ != mtx::Undefined )
          mtx::Delete(Mutex_);
      }

      TimeStamp = 0;
      Driver_ = NULL;
      Mutex_ = mtx::Undefined;
      UserDiscriminator_ = NULL;
      IsAlive_ = false;
      Row_ = qNIL;
    }
    qCDTOR( rCaller );
    void Init(
      sck::rRWDriver* Driver,
      sRow Row)
    {
      reset();

      Mutex_ = mtx::Create();
      Driver_ = Driver;
      TimeStamp = tol::EpochTime(false);
      UserDiscriminator_ = NULL;
      IsAlive_ = true;
      Row_ = Row;
    }
    fdr::rRWDriver *GetDriver(void) const
    {
      return Driver_;
    }
    void Vanished(void)
    {
      if ( !IsAlive_ )
        qRGnr();

      IsAlive_ = false;
    }
    bso::sBool ShouldIDestroy(const void *UserDiscriminator);
    friend class rCallers;
    friend void Test_(void);
    qRODISCLOSEr(sRow, Row);
  };

  // TODO: Mutex to protect access of 'Callers_'.
  class rCallers
  {
  private:
    mtx::rMutex Mutex_; // To protect acces to following member.
    lstbch::qLBUNCHw(rCaller *, sRow) List_;
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
    tol::sTimeStamp GetTimestamp(sRow Row) const;
    void Withdraw(sRow Row); // The corresponding caller is made inaccessible and deleted if applied.
    rCaller *Hire(
      sRow Row,
      const void *UserDiscriminator) const;
    sdr::sSize Extent(void) const
    {
      return List_.Extent();
    }
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
