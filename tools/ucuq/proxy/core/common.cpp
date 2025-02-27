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


#include "common.h"

#include "messages.h"
#include "registry.h"

#include "sclm.h"

#include "mtk.h"

using namespace common;

class common::rCaller_
{
private:
  bso::sBool *BreakFlag_;   // Acts also as discriminator.
  sck::rRWDriver *Driver_;
	bso::sBool IsAlive_(void) const
	{
		if ( Driver_ == NULL )
			qRGnr();

		return Driver_ - IsAlive_();
	}
public:
  void reset(bso::sBool P = true)
  {
    if ( P ) {
      qDELETE(Driver_);
    }

    Driver_ = NULL;
    BreakFlag_ = NULL;
  }
  qCDTOR(rCaller_);
  void Init(
    sck::rRWDriver *Driver,
    sRow Row)
  {
    reset();

    Driver_ = Driver;
    BreakFlag_ = NULL;
  }
	// If returning 'false', a break is send and the hire must be tried again.
  bso::sBool Hire(bso::sBool *BreakFlag)
  {
		if ( !IsAlive_() )
			qRGnr();;

    if ( BreakFlag_ != NULL ) {
			if ( BreakFlag == BreakFlag_ )
				qRGnr();

      *BreakFlag_ = true;

			return false;
		}

    BreakFlag_ = BreakFlag;

		Driver_->SetBreakFlag(2, BreakFlag_);

		return true;
  }
	// If returns 'true', this object should be destroyed.
	bso::sBool Release(const bso::sBool *BreakFlag)
	{
		if ( BreakFlag == NULL )
			qRGnr();

			if ( BreakFlag_ == NULL )
				qRGnr();

			if ( IsAlive_() ) {
				if ( BreakFlag_ == BreakFlag )
					BreakFlag_ = NULL;

				Driver_->RearmAfterBreak(fdr::ts_Default);

				return false;
			} else if ( BreakFlag_ == BreakFlag ) {
				BreakFlag_ = NULL;

				return true;
			}

			return false;
	}
	// Mark as must break if in use and return true, or retun false if no more in use.
	bso::sBool MarkForBreak(void)
	{
		if ( BreakFlag_ == NULL )
			return false;

		*BreakFlag_ = true;

		return true;
	}
	sck::rRWDriver *GetDriver(const bso::sBool *BreakFlag) const
	{
		if ( !IsAlive_() )
			qRGnr();

		if ( BreakFlag_ != BreakFlag )
			qRGnr();

		return Driver_;
	}
};

sRow common::rCallers::New(sck::rRWDriver *Driver)
{
	sRow Row = qNIL;
	qRH;
	rCaller_ *Caller = NULL;
	mtx::rHandle Locker;
	qRB;
	Caller = qNEW(rCaller_);

	Locker.InitAndLock(Mutex_);

	Row = List_.Add(Caller);

	Caller->Init(Driver, Row);
	qRR;
	qDELETE(Caller);
	qRT;
	qRE;
	return Row;
}

void common::rCallers::Withdraw(sRow Row)
{
	qRH;
	mtx::rHandle Locker;
	rCaller_ *Caller = NULL;
	qRB;
	Locker.InitAndLock(Mutex_);

	Caller = List_.Get(Row);

	List_.Delete(Row);

	if ( Caller == NULL )
		qRGnr();

	if ( !Caller->MarkForBreak() )
		qDELETE(Caller);
	qRR;
	qRT;
	qRE;
}

bso::sBool common::rCallers::Hire(
	sRow Row,
	bso::sBool *BreakFlag) const
{
	rCaller_ *Caller = NULL;
	qRH;
	mtx::rHandle Locker;
	qRB;
	Locker.InitAndLock(Mutex_);

	Caller = List_.Get(Row);

	if ( Caller == NULL )
		qRGnr();

	if ( !Caller->Hire(BreakFlag) )
		Caller = NULL;
qRR;
qRT;
qRE;
	return Caller != NULL;
}

sck::rRWDriver *common::rCallers::GetDriver(
	sRow Row,
	const bso::sBool *BreakFlag) const
{
	sck::rRWDriver *Driver = NULL;
qRH;
	mtx::rHandle Locker;
	rCaller_ *Caller = NULL;
qRB;
	Locker.InitAndLock(Mutex_);

	Caller = List_.Get(Row);

	if ( Caller == NULL )
		qRGnr();

	Driver = Caller->GetDriver(BreakFlag);

	if ( Driver == NULL )
		qRGnr();

qRR;
qRT;
qRE;
	return Driver;
}

bso::sBool common::rCallers::Release(
	sRow Row,
	const bso::sBool *BreakFlag)
{
	bso::sBool Withdrawed = false;
qRH;
	mtx::rHandle Locker;
	rCaller_ *Caller = NULL;
qRB;
	Locker.InitAndLock(Mutex_);

	Caller = List_.Get(Row);

	if ( Caller == NULL )
		qRGnr();

	if ( Caller->Release( BreakFlag) ) {
		Withdrawed = true;
		Withdraw(Row);
	}
qRR;
qRT;
qRE;
	return Withdrawed;
}

namespace {
	const str::dString &GetTranslation_(
		ucucmn::eCaller Caller,
		str::dString &Translation)
	{
		messages::eId Id = messages::i_Undefined;

		switch ( Caller ) {
		case ucucmn::cRemote:
			Id = messages::iRemote;
			break;
		case ucucmn::cDevice:
			Id = messages::iDevice;
			break;
		default:
			qRGnr();
			break;
		}

		return messages::GetTranslation(Id, Translation);
	}
}
