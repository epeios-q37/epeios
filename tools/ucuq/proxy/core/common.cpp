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

sRow common::rCallers::New(sck::rRWDriver *Driver)
{
	sRow Row = qNIL;
qRH;
	rCaller *Caller = NULL;
	mtx::rHandle Locker;
qRB;
	Caller = qNEW(rCaller);

	Locker.InitAndLock(Mutex_);

	Row = List_.Add(Caller);

	Caller->Init(Driver, Row);
qRR;
	qDELETE(Caller);
qRT;
qRE;
	return Row;
}

tol::sTimeStamp common::rCallers::GetTimestamp(sRow Row) const
{
	tol::sTimeStamp Timestamp = 0;
qRH;
	mtx::rHandle Locker;
	rCaller *Caller = NULL;
qRB;
	Locker.InitAndLock(Mutex_);

	Caller = List_.Get(Row);

	if ( Caller == NULL )
		qRGnr();

	Timestamp = Caller->TimeStamp;
qRR;
qRT;
qRE;
	return Timestamp;
}

void common::rCallers::Withdraw(sRow Row)
{
qRH;
	rCaller *Caller = NULL;
	mtx::rHandle ListLocker, CallerLocker;
qRB;
	ListLocker.InitAndLock(Mutex_);

	Caller = List_.Get(Row);

	List_.Delete(Row);

	ListLocker.Unlock();

	if ( Caller == NULL )
		qRGnr();

	CallerLocker.InitAndLock(Caller->Mutex_);

	if ( Caller->UserDiscriminator_ == NULL ) {
		CallerLocker.Unlock();	// To avoid an error on destroying the underlying mutex because it is still locked.
		CallerLocker.reset(false);	// The corresponding mutes will be destroyed.
		qDELETE(Caller);
	} else
		Caller->IsAlive_ = false;
qRR;
qRT;
qRE;
}

rCaller *common::rCallers::Hire(
	sRow Row,
	const void *UserDiscriminator) const
{
	rCaller *Caller = NULL;
qRH;
	mtx::rHandle Locker;
qRB;
	Locker.InitAndLock(Mutex_);

	Caller = List_.Get(Row);

	if ( Caller == NULL )
		qRGnr();

	if ( !Caller->IsAlive_ )
		Caller = NULL;
	else
		Caller->UserDiscriminator_ = UserDiscriminator;
	qRR;
	qRT;
	qRE;
		return Caller;
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

bso::sBool common::rCaller::ShouldIDestroy(const void *UserDiscriminator)
{
	bso::sBool Answer = false;
qRH;
	mtx::rHandle Locker;
qRB;
	Locker.InitAndLock(Mutex_);

	if ( !IsAlive_ && (UserDiscriminator == UserDiscriminator_) )
		Answer = true;
qRR;
qRT;
qRE;
	return Answer;
}
