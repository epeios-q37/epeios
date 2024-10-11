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


#ifndef DEVICE_INC_
# define DEVICE_INC_

# include "common.h"

# include "sdr.h"
# include "sck.h"

namespace device {
  qENUM(Request) { // Request sent to device (as integer)
    rPing,
    rExecute,
    r_amount,
    r_Undefined
  };

  qENUM(Answer) {
    aOK,
    aError,
    aPuzzled,
    aDisconnected,
    a_amount,
    a_Undefined
  };

  eAnswer GetAnswer(
    flw::rRFlow &Flow,
    const common::gTracker *Tracker);

  qROW( Row );

  struct dSelector {
  public:
    struct s {
      str::dString::s
        Token,
        Id;
    };
    str::dString
      Token,
      Id;
    dSelector(s &S)
    : Token(S.Token),
      Id(S.Id)
    {}
    void reset(bso::sBool P = true)
    {
      tol::reset(P, Token, Id);
    }
    void plug(qASd *AS)
    {
      Token.plug(AS);
      Id.plug(AS);
    }
    dSelector &operator =(const dSelector &S)
    {
      Token = S.Token;
      Id = S.Id;

      return *this;
    }
    void Init(void)
    {
      tol::Init(Token, Id);
    }
  };

  qW(Selector);

  qENUM(State) { // State of the connection.
    sConnected,
    sClosePending,
    s_amount,
    s_Undefined
  };

  sRow New(
    const dSelector &Selector,
    sck::rRWDriver *Driver);
  common::rCaller *Hire(
    const dSelector &Selector,
    const void *User);
  void Withdraw(sRow Row);  // Make unavailable and delete if applied.
  void Withdraw(const dSelector &Selector);
  void Withdraw(const str::dString &Token);
  bso::sBool CreateVToken(
    const str::dString &Token,
    const str::dString &VToken, const str::dString & TrueId);
  bso::sBool DeleteVToken(const str::dString &Token);
}

#endif
