/*
  Copyright (C) 2024 Claude SIMON (http://q37.info/contact/).

  This file is part of the 'UCUq' tool.

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

#define C( name )	case c##name : return #name; break

const char *common::GetLabel(eCaller Caller)
{
	switch ( Caller ) {
		C(Frontend);
		C(Backend);
	default:
		qRFwk();
		break;
	}

	return NULL;	// To avoid a warning.
}

#undef C

namespace {
	stsfsm::wAutomat CallerAutomat_;

	void FillCallerAutomat_(void)
	{
		CallerAutomat_.Init();
		stsfsm::Fill<eCaller>(CallerAutomat_, c_amount, GetLabel);
	}
}

eCaller common::GetCaller(const str::dString &Pattern)
{
	return stsfsm::GetId(Pattern, CallerAutomat_, c_Undefined, c_amount);
}

sdr::tRow common::rCallers::New(sck::rRWDriver *Driver)
{
	sdr::sRow Row = qNIL;
qRH;
	rCaller *Caller = NULL;
qRB;
	Caller = qNEW(rCaller);

	Caller->Init(Driver);

	Row = List_.Add(Caller);
qRR;
	qDELETE(Caller);
qRT;
qRE;
	return *Row;
}

void common::rCallers::Delete(sdr::sRow Row)
{
	rCaller *Caller = List_.Get(Row);

	if ( Caller == NULL )
		qRGnr();

	qDELETE(Caller);

	List_.Delete(Row);
}

sck::rRWDriver& common::rCallers::Get(sdr::tRow Row)
{
	rCaller *Caller = List_.Get(Row);

	if ( Caller == NULL )
		qRGnr();

	if ( Caller->Driver == NULL )
		qRGnr();

	return *Caller->Driver;
}

namespace {
	const str::dString &GetTranslation_(
		eCaller Caller,
		str::dString &Translation)
	{
		messages::eId Id = messages::i_Undefined;

		switch ( Caller ) {
		case cFrontend:
			Id = messages::iFrontend;
			break;
		case cBackend:
			Id = messages::iBackend;
			break;
		default:
			qRGnr();
			break;
		}

		return messages::GetTranslation(Id, Translation);
	}
}

sdr::tRow common::rCallers::Get(void) const
{
	sdr::sRow Row = List_.First();
	sdr::sRow RowLast = qNIL;
	tol::sTimeStamp TimeStamp = 0;
	rCaller *Caller = NULL;

	while ( Row != qNIL ) {
		Caller = List_.Get(Row);

		if ( Caller == NULL )
			qRGnr();

		if ( Caller->TimeStamp > TimeStamp ) {
			TimeStamp = Caller->TimeStamp;
			RowLast = Row;
		}

		Row = List_.Next(Row);
	}

	return *RowLast;
}

qGCTOR(common)
{
	FillCallerAutomat_();
}

