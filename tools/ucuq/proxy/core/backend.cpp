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


#include "backend.h"

#include "registry.h"

#include "sclm.h"

#include "crt.h"

using namespace backend;

namespace {
  mtx::rMutex Mutex_ = mtx::Undefined; // To protect the too below members;
  crt::qCRATEw(dSelector, sRow) Selectors_;
  common::rCallers Backends_;
}

namespace {
  sRow New_(
    const dSelector &Selector,
    sck::rRWDriver *Driver)
  {
    sRow Row = Backends_.New(Driver);

    Selectors_.Allocate(Backends_.Extent());

    Selectors_.Store(Selector, Row);

    return Row;
  }

  namespace {
    bso::sBool Matches(
      const dSelector &S1,
      const dSelector &S2)
    {
      return S1.Token == S2.Token && S1.Id == S2.Id;
    }
  }

  sRow Get_(const dSelector &Selector)
  {
    sRow
      Row = Selectors_.First(),
      LastRow = qNIL;

    tol::sTimeStamp
      Timestamp = 0,
      LastTimestamp = 0;

    while ( Row != qNIL ) {
      if ( Matches(Selector, Selectors_.Get(Row))
           && ( LastTimestamp < ( Timestamp = Backends_.GetTimestamp(*Row)) ) )
      {
        LastRow = Row;
        LastTimestamp = Timestamp;
      }

      Row = Selectors_.Next(Row);
    }

    return LastRow;
  }

  void Withdraw_(sRow Row)
  {
    Selectors_(Row).reset();

    Backends_.Withdraw(*Row);
  }

}

eAnswer backend::GetAnswer(
  flw::rRFlow &Flow,
  const common::gTracker *Tracker)
{
  bso::sU8 Answer = a_Undefined;

  common::Get(Flow, Answer, Tracker);

  if ( Answer > a_amount )
    qRGnr();

  return (eAnswer)Answer;
}

sRow backend::New(
  const dSelector &Selector,
  sck::rRWDriver *Driver)
{
  sRow Row = qNIL;
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = Get_(Selector);

  if ( Row != qNIL )
    Withdraw_(Row);

  Row = New_(Selector, Driver);

  Selectors_.Allocate(Backends_.Extent());

  Selectors_.Store(Selector, Row);
qRR;
qRT;
qRE;
  return Row;
}

common::rCaller *backend::Hire(
  const dSelector &Selector,
  const void *UserDiscriminator)
{
  common::rCaller *Caller = NULL;
qRH;
  mtx::rHandle Locker;
  sRow Row = qNIL;
qRB;
  Locker.InitAndLock(Mutex_);
  Row = Get_(Selector);
  Locker.Unlock();

  if ( Row != qNIL )
    Caller = Backends_.Hire(*Row, UserDiscriminator);
qRR;
qRT;
qRE;
  return Caller;
}

void backend::Withdraw(sRow Row)
{
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);
  
  Withdraw_(Row);
qRR;
qRT;
qRE;
}

void backend::Withdraw(const dSelector &Selector)
{
qRH;
  mtx::rHandle Locker;
  sRow Row = qNIL;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = Get_(Selector);

  if ( Row != qNIL )
    Withdraw_(Row);
qRR;
qRT;
qRE;
}

void backend::Withdraw(const str::dString &Token)
{
qRH;
  mtx::rHandle Locker;
  sRow Row = qNIL;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = Selectors_.First();

  while ( Row != qNIL ) {
    if ( Selectors_(Row).Token == Token )
      Withdraw_(Row);

    Row = Selectors_.Next(Row);
  }
  qRR;
  qRT;
  qRE;
}

qGCTOR(backend)
{
  Mutex_ = mtx::Create();
  Backends_.Init();
  Selectors_.Init();
}

qGDTOR(backend) {
  if ( Mutex_ != mtx::Undefined )
    mtx::Delete(Mutex_, true);
}
