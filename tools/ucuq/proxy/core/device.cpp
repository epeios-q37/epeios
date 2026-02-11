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
  qW(SRows_);

  typedef common::sRow sCRow_;

  mtx::rMutex Mutex_ = mtx::Undefined;  // Protection of below two members.
  common::rCallers Callers_;
}

eAnswer device::GetAnswer(flw::rRFlow &Flow)
{
  bso::sU8 Answer = a_Undefined;

  if ( !Flow.EndOfFlow() )
    common::Get(Flow, Answer);
  else
    Answer = aDisconnected;

   if ( Answer > a_amount )
    qRGnr();

  return (eAnswer)Answer;
}

namespace {
  void Withdraw_(sSRow_ Row)
  {
    Callers_.Withdraw(seeker::GetCallerRow(Row));
    seeker::Delete(Row);
  }
}

bso::sBool device::New(
  const str::dString &RToken,
  const str::dString &Id,
  sck::rRWDriver *Driver,
  qRPN)
{
  sSRow_ SRow = qNIL;
qRH;
  mtx::rHandle Locker;
  sCRow_ CRow = qNIL;
qRB;
  Locker.InitAndLock(Mutex_);

  SRow = seeker::GetVToken(str::Empty, RToken);  // If != 'qNIL', 'RToken' exists as virtual.

  if ( SRow == qNIL ) {
    SRow = seeker::GetRToken(RToken, Id);

    if ( SRow != qNIL )
      Withdraw_(SRow);

    SRow = seeker::New(RToken, Id, CRow = Callers_.New(Driver));
  } else
    SRow = qNIL;

  if ( qRPT && ( SRow == qNIL ) )
    qRGnr();
qRR;
qRT;
qRE;
  return SRow != qNIL;
}

common::sRow device::Hire(
  const str::dString &Token,
  const str::dString &Id,
  bso::sBool *BreakFlag)
{
  common::sRow Row = qNIL;
qRH;
  mtx::rHandle Locker;
  sSRow_ SRow = qNIL;
qRB;
  Locker.Init(Mutex_, false);

  do {
    Locker.Lock();

    SRow = seeker::GuessRToken(Token, Id);

    if ( SRow == qNIL )
      break;

    Row = seeker::GetCallerRow(SRow);

    if ( Row == qNIL )
      qRGnr();

    if ( Callers_.Hire(Row, BreakFlag) )
      break;

    Row = qNIL;

    Locker.Unlock();

    tht::Suspend(500);
  } while ( true );
qRR;
qRT;
qRE;
  return Row;
}

sck::rRWDriver &device::GetDriver(
  common::sRow Row,
  const bso::sBool *BreakFlag)
{
  sck::rRWDriver *Driver = NULL;
qRH;
  mtx::rHandle Locker;
  sSRow_ SRow = qNIL;
qRB;
  Locker.InitAndLock(Mutex_);

  Driver = Callers_.GetDriver(Row, BreakFlag);

  if ( Driver == NULL )
    qRGnr();
qRR;
qRT;
qRE;
  return *Driver;
}

bso::sBool device::Release(
  common::sRow Row,
  const bso::sBool *BreakFlag)
{
  bso::sBool IsWithdrawed = false;
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  IsWithdrawed = Callers_.Release(Row, BreakFlag);
qRR;
qRT;
qRE;
  return IsWithdrawed;
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

  Row = seeker::GetVToken(RToken, VToken);

  if ( Row != qNIL )
    seeker::Delete(Row);

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

void device::GetRTokenIds(const str::dString &RToken,
  str::dStrings &Ids,
  ucucmn::dTimeStamps &TimeStamps,
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
    TimeStamps.Append(Set.TimeStamp());

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

bso::sBool device::GetVTokenId(const str::dString &RToken,
  const str::dString &VToken,
  str::dString &Id,
  tol::sTimeStamp &TimeStamp,
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

    if ( Set.TimeStamp() == tol::UndefinedTimeStamp )
      qRUnx();

    TimeStamp = Set.TimeStamp();
  }
qRR;
qRT;
qRE;
  return Row != qNIL;
}

void device::GetTokensFeatures(
  const str::dString &RToken,
  str::dStrings &Ids,
  ucucmn::dTimeStamps &IdsTimeStamps,
  str::dStrings &VTokens,
  ucucmn::dTimeStamps &VTokensTimeStamps,
  str::dStrings &VTokenIds)
{
qRH;
  mtx::rHandle Locker;
  sdr::sRow Row = qNIL;
  str::wString Id;
  tol::sTimeStamp TimeStamp = tol::UndefinedTimeStamp;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = VTokens.Last();

  GetRTokenIds(RToken, Ids, IdsTimeStamps, false);
  GetRTokenVTokens(RToken, VTokens, false);

  Row = VTokens.Next(Row);

  while ( Row != qNIL ) {
    Id.Init();
    GetVTokenId(RToken, VTokens(Row), Id, TimeStamp, false);

    VTokenIds.Append(Id);
    VTokensTimeStamps.Append(TimeStamp);

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
