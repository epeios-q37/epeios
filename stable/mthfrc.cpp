/*
	Copyright (C) 1999 Claude SIMON (http://q37.info/contact/).

	This file is part of the Epeios framework.

	The Epeios framework is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

	The Epeios framework is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with the Epeios framework.  If not, see <http://www.gnu.org/licenses/>
*/

#define MTHFRC_COMPILATION_

#include "mthfrc.h"

using namespace mthfrc;

void mthfrc::Simplify( fraction_ &Fraction )
{
qRH
	integer PGCD;
qRB
	PGCD.Init();

	mthitg::PGCD( Fraction.N, Fraction.D, PGCD );

	Fraction.N /= PGCD;
	Fraction.D /= PGCD;
qRR
qRT
qRE
}
