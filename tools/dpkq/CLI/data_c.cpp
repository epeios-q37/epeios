/*
	Copyright (C) 2010-2015 Claude SIMON (http://q37.info/contact/).

	This file is part of dpkq.

    dpkq is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

    dpkq is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with dpkq.  If not, see <http://www.gnu.org/licenses/>
*/

#include "data_c.h"

#include "registry.h"

#include "sclm.h"

using namespace data_c;

str::wString data_c::NamespaceLabel;

void data_c::Initialize( void )
{
	if ( NamespaceLabel.Amount() != 0 )
		qRChk();

	NamespaceLabel.Init();
	sclm::MGetValue( registry::NamespaceLabel, NamespaceLabel );
	NamespaceLabel.Append( ':' );
}