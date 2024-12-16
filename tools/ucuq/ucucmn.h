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


// UCUq CoMmoN

#ifndef UCUCMN_INC_
# define UCUCMN_INC_

# include "tol.h"
# include "csdcmn.h"

namespace ucucmn {
  qENUM(Caller) {
    cAdmin,
    cManager,
    cRemote,
    cDevice,
    c_amount,
    c_Undefined
  };

  const char *GetLabel(eCaller Caller);

  eCaller GetCaller(const str::dString &Pattern);

  namespace protocol {
    extern const char *Id;
    qCDEF(csdcmn::sVersion, LastVersion, 0);
  }

  template <typename integer> integer Get(
    flw::rRFlow &Flow,
    integer &Integer)
  {
    return csdcmn::Get(Flow, Integer);
  }

  inline const str::dString &Get(
    flw::rRFlow &Flow,
    str::dString &String)
  {
    return csdcmn::Get(Flow, String);
  }

  inline const str::dStrings &Get(
    flw::rRFlow &Flow,
    str::dStrings &Strings)
  {
    return csdcmn::Get(Flow, Strings);
  }

  inline const str::dStrings &Get(
    flw::rRFlow &Flow,
    str::wStrings &Strings)
  {
    return csdcmn::Get(Flow, Strings);
  }

  inline void Put(
    const str::dString &String,
    flw::rWFlow &Flow)
  {
    return csdcmn::Put(String, Flow);
  }

  inline void Put(
    const str::dStrings &Strings,
    flw::rWFlow &Flow)
  {
    return csdcmn::Put(Strings, Flow);
  }

  inline void Put(
    const str::wStrings &Strings,
    flw::rWFlow &Flow)
  {
    return csdcmn::Put(Strings, Flow);
  }

  template <typename integer> void Put(
    integer Integer,
    flw::rWFlow &Flow)
  {
    return csdcmn::Put(Integer, Flow);
  }

  inline void Commit(flw::rWFlow &Flow)
  {
    Flow.Commit();
  }

  inline void Dismiss(flw::rRFlow &Flow)
  {
    Flow.Dismiss();
  }
}

#endif
