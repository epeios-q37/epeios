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


#ifndef SEEKER_INC_
# define SEEKER_INC_

# include "common.h"

# include "idxbtq.h"
# include "lstbch.h"

namespace seeker {
  qROW(Row);

  typedef bch::qBUNCHdl(sRow) dRows;
  qW(Rows);

  void DisplayTies(void);

  class dSet
  {
  public:
    struct s
    {
      str::dString::s
        ROrV,
        IdOrR,
        VOrR;
    };
    str::dString
      ROrV,
      IdOrR,
      VOrR;
    dSet(s &S):
      ROrV(S.ROrV),
      IdOrR(S.IdOrR),
      VOrR(S.VOrR)
    {
      reset(false);
    }
    void reset(bso::sBool P = true)
    {
      tol::reset(P, ROrV, IdOrR, VOrR);
    }
    qDTOR(dSet);
    void Init(void)
    {
      tol::Init(ROrV, IdOrR, VOrR);
    }
  };

  qW(Set);

  const dSet &Get(
    sRow Row,
    dSet &Set);

  common::sRow GetCaller(sRow Row);

  sRow GetRToken(
    const str::dString &RToken,
    const str::dString &Id);

  const dRows &GetRTokens(
    const str::dString &RToken,
    dRows &Rows);

  sRow GetVToken(
    const str::dString &RToken,
    const str::dString &VToken);

  const dRows &GetVTokens(
    const str::dString &RToken,
    dRows &Rows);

  sRow New(
    const str::dString &RToken,
    const str::dString &Id,
    common::sRow Caller);

  sRow Create(
    const str::dString &VToken,
    const str::dString &RToken,
    const str::dString &Id);  // Id may be empty.

  void Delete(sRow Row);
}

#endif
