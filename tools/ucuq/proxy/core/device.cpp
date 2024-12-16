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


#include "device.h"

#include "registry.h"
#include "seeker.h"

#include "sclm.h"

#include "lstcrt.h"
#include "str.h"
#include "idxbtq.h"

using namespace device;

namespace {
  typedef seeker::sRow sSRow_;
  typedef seeker::dRows dSRows_;
  typedef seeker::wRows wSRows_;

  mtx::rMutex Mutex_ = mtx::Undefined;
  common::rCallers Callers_;
}

eAnswer device::GetAnswer(
  flw::rRFlow &Flow,
  const common::gTracker *Tracker)
{
  bso::sU8 Answer = a_Undefined;

  common::Get(Flow, Answer, Tracker);

  if ( Answer > a_amount )
    qRGnr();

  return (eAnswer)Answer;
}

namespace {
  void Withdraw_(sSRow_ Row)
  {
    Callers_.Withdraw(seeker::GetCaller(Row));
    seeker::Delete(Row);
  }
}

bso::sBool device::New(
  const str::dString &RToken,
  const str::dString &Id,
  sck::rRWDriver *Driver,
  qRPN)
{
  sSRow_ Row = qNIL;
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = seeker::GetVToken(str::Empty, RToken);  // If != 'qNIL', 'RToken' exists as virtual.

  if ( Row == qNIL ) {
    Row = seeker::GetRToken(RToken, Id);

    if ( Row != qNIL )
      Withdraw_(Row);

    Row = seeker::New(RToken, Id, Callers_.New(Driver));
  } else
    Row = qNIL;

  if ( qRPT && ( Row == qNIL ) )
    qRGnr();
qRR;
qRT;
qRE;
  return Row != qNIL;
}

common::rCaller *device::Hire(
  const str::dString &RToken,
  const str::dString &Id,
  const void *UserDiscriminator)
{
  common::rCaller *Caller = NULL;
qRH;
  mtx::rHandle Locker;
  sSRow_ Row = qNIL;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = seeker::GetRToken(RToken, Id);

  if ( Row != qNIL )
    Caller = Callers_.Hire(seeker::GetCaller(Row), UserDiscriminator);
qRR;
qRT;
qRE;
  return Caller;
}

void device::WithdrawDevice(
  const str::dString &RToken,
  const str::dString &Id)
{
qRH;
  mtx::rHandle Locker;
  sSRow_ Row = qNIL;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = seeker::GetRToken(RToken, Id);

  if ( Row != qNIL )
    Withdraw_(Row);
qRR;
qRT;
qRE;
}

void device::WithdrawDevices(const str::dString &RToken)
{
qRH;
  mtx::rHandle Locker;
  wSRows_ Rows;
  sdr::sRow Row = qNIL;
qRB;
  Locker.InitAndLock(Mutex_);

  Rows.Init();

  seeker::GetRTokens(RToken, Rows);

  Row = Rows.First();

  while ( Row != qNIL ) {
    Withdraw_(Rows(Row));

    Row = Rows.Next(Row);
  }
qRR;
qRT;
qRE;
}

void device::DeleteVTokens(const str::dString &RToken)
{
qRH;
  mtx::rHandle Locker;
  wSRows_ Rows;
  sdr::sRow Row = qNIL;
qRB;
  Locker.InitAndLock(Mutex_);

  Rows.Init();

  seeker::GetVTokens(RToken, Rows);

  Row = Rows.First();

  while ( Row != qNIL ) {
    seeker::Delete(Rows(Row));

    Row = Rows.Next(Row);
  }
qRR;
qRT;
qRE;
}

bso::sBool device::CreateVToken(
  const str::dString &VToken,
  const str::dString &RToken,
  const str::dString &Id,
  qRPN)
{
  sSRow_ Row = qNIL; 
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = seeker::Create(VToken, RToken, Id);

  if ( qRPT && ( Row == qNIL ) )
    qRGnr();
qRR;
qRT;
qRE;
  return Row != qNIL;
}

bso::sBool device::DeleteVToken(
  const str::dString &RToken,
  const str::dString &VToken)
{
  sSRow_ Row = qNIL;
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = seeker::GetVToken(RToken, VToken);

  if ( Row != qNIL ) 
    seeker::Delete(Row);
qRR;
qRT;
qRE;
  return Row != qNIL;
}


void device::GetRTokenIds(
  const str::dString &RToken,
  str::dStrings &Ids,
  bso::sBool Lock)
{
 qRH;
  mtx::rHandle Locker;
  wSRows_ Rows;
  sdr::sRow Row = qNIL;
  seeker::wSet Set;
qRB;
  if ( Lock )
    Locker.InitAndLock(Mutex_);

  Rows.Init();

  seeker::GetRTokens(RToken, Rows);

  Row = Rows.First();

  while ( Row != qNIL ) {
    Set.Init();

    seeker::Get(Rows(Row), Set);

    if ( Set.ROrV != RToken )
      qRGnr();

    if ( Set.VOrR.Amount() )
      qRGnr();

    Ids.Append(Set.IdOrR);

    Row = Rows.Next(Row);
  }
  qRR;
qRT;
qRE;
}

void device::GetRTokenVTokens(
  const str::dString &RToken,
  str::dStrings &VTokens,
  bso::sBool Lock)
{
 qRH;
  mtx::rHandle Locker;
  wSRows_ Rows;
  sdr::sRow Row = qNIL;
  seeker::wSet Set;
qRB;
  if ( Lock )
    Locker.InitAndLock(Mutex_);

  Rows.Init();

  seeker::GetVTokens(RToken, Rows);

  Row = Rows.First();

  while ( Row != qNIL ) {
    Set.Init();

    seeker::Get(Rows(Row), Set);

    if ( Set.VOrR != RToken )
      qRGnr();

    VTokens.Append(Set.ROrV);

    Row = Rows.Next(Row);
  }
  qRR;
qRT;
qRE;
}

bso::sBool device::GetVTokenId(
  const str::dString &RToken,
  const str::dString &VToken,
  str::dString &Id,
  bso::sBool Lock)
{
  sSRow_ Row = qNIL;
qRH;
  mtx::rHandle Locker;
  seeker::wSet Set;
qRB;
  if ( Lock )
    Locker.InitAndLock(Mutex_);

  Row = seeker::GetVToken(RToken, VToken);

  if ( Row != qNIL ) {
    Set.Init();

    seeker::Get(Row, Set);

    if ( Set.ROrV != VToken )
      qRUnx();

    if ( Set.VOrR != RToken )
      qRUnx();

    if ( Set.IdOrR.Amount() )
      Id = Set.IdOrR;
  }
qRR;
qRT;
qRE;
  return Row != qNIL;
}

void device::GetTokensFeatures(
  const str::dString &RToken,
  str::dStrings &Ids,
  str::dStrings &VTokens,
  str::dStrings &VTokenIds)
{
qRH;
  mtx::rHandle Locker;
  sdr::sRow Row = qNIL;
  str::wString Id;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = VTokens.Last();

  GetRTokenIds(RToken, Ids, false);
  GetRTokenVTokens(RToken, VTokens, false);

  Row = VTokens.Next(Row);

  while ( Row != qNIL ) {
    Id.Init();
    GetVTokenId(RToken, VTokens(Row), Id, false);

    VTokenIds.Append(Id);

    Row = VTokens.Next(Row);
  }
qRR;
qRT;
qRE;
}

qGCTOR(device)
{
  Mutex_ = mtx::Create();
  Callers_.Init();
}

qGDTOR(device) {
  if ( Mutex_ != mtx::Undefined )
    mtx::Delete(Mutex_, true);
}
