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
    aResult,
    aSensor,
    aError,
    aPuzzled,
    aDisconnected,
    a_amount,
    a_Undefined
  };

  eAnswer GetAnswer(
    flw::rRFlow &Flow,
    const common::gTracker *Tracker);

  qENUM(State) { // State of the connection.
    sConnected,
    sClosePending,
    s_amount,
    s_Undefined
  };

  bso::sBool New(
    const str::dString &Token,
    const str::dString &Id,
    sck::rRWDriver *Driver,
    qRPD);
  common::rCaller *Hire(
    const str::dString &RToken,
    const str::dString &Id,
    const void *User);
  void WithdrawDevice(
    const str::dString &RToken,
    const str::dString &Id );
  void WithdrawDevices(const str::dString &RToken);
  void DeleteVTokens(const str::dString &RToken);
  bso::sBool CreateVToken(
    const str::dString &VToken,
    const str::dString &RToken,
    const str::dString &Id,
    qRPD);
  bso::sBool DeleteVToken(
    const str::dString &RToken,
    const str::dString &VToken);
  void GetRTokenIds(
    const str::dString &RToken,
    str::dStrings & Ids,
    bso::sBool Lock = true);
  void GetRTokenVTokens(
    const str::dString &RToken,
    str::dStrings &VTokens,
    bso::sBool Lock = true);
  bso::sBool GetVTokenId(
    const str::dString &RToken,
    const str::dString &VToken,
    str::dString &Id,
    bso::sBool Lock = true);
  void GetTokensFeatures(
    const str::dString &RToken,
    str::dStrings &Ids,
    str::dStrings &VTokens,
    str::dStrings &VTokenIds);
}

#endif
