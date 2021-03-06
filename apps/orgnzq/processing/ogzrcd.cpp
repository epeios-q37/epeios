/*
	Copyright (C) 2015-2016 Claude SIMON (http://q37.info/contact/).

	This file is part of 'orgnzq' software.

    'orgnzq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'orgnzq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'orgnzq'.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "ogzrcd.h"

using namespace ogzrcd;

void ogzrcd::mRecords::Add(
	ogzbsc::sFRow Field,
	sRow RecordRow ) const
{
qRH
	wRecord Record;
qRB
	Record.Init();
	Recall( RecordRow, Record );

	Record.Add( Field );

	Store( Record, RecordRow );
qRR
qRT
qRE
}

bso::sBool ogzrcd::mRecords::Erase(
	ogzbsc::sFRow Field,
	sRow RecordRow,
	qRPN ) const
{
	sdr::sRow Row = qNIL;
qRH
	wRecord Record;
qRB
	Record.Init();
	Recall( RecordRow, Record );

	Row = Record.Search( Field );

	if ( Row != qNIL ) {
		Record.Remove( Row );
		Store( Record, RecordRow );
	} else if ( qRPT )
			qRGnr();


qRR
qRT
qRE
	return Row != qNIL;
}


bso::sBool ogzrcd::mRecords::IsEmpty( sRow RecordRow ) const
{
	bso::sBool IsEmpty = false;
qRH
	wRecord Record;
qRB
	Record.Init();
	Recall( RecordRow, Record );

	IsEmpty = Record.IsEmpty();
qRR
qRT
qRE
	return IsEmpty;
}


