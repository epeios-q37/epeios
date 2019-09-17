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

#define TME_COMPILATION_

#include "tme.h"

#include <ctype.h>

using namespace tme;

/*
	Une heure est stock dans 'raw_time__', qui est en entier de 32 bits.

	Voici son encodage (bits de poids faibles vers bits de poids forts).

	0-2 (3)   : rserv  une utilisation future.
	4-31 (28) : heure en millime de secondes
*/

const char *tme::time__::ASCII(
	buffer__ &Buffer,
	format__ Format ) const
{
	bso::u8__ Indice = 0;
	_ASCII( Buffer );

	switch ( Format ) {
	case fH:
		Indice = 2;
		break;
	case fHM:
		Indice = 5;
		break;
	case fHMS:
		Indice = 8;
		break;
	case fHMSd:
		Indice = 10;
		break;
	case fHMSc:
		Indice = 11;
		break;
	case fHMSm:
		Indice = 12;
		break;
	default:
		qRFwk();
		break;
	}

	Buffer[Indice] = 0;

	return Buffer;
}

#define LIMIT	( BSO_U16_MAX / 10 )

typedef bso::u16__ item__;

static inline item__ ExtractItem_( const char *&Time )
{
	item__ Item = 0;

	if ( *Time == 0 )
		return 0;

	if( !isdigit( *Time ) )
		return 0;

	while( isdigit( *Time ) && ( Item < LIMIT ) )
		Item = Item * 10 + *Time++ - '0';

	if ( *Time == 0 )
		Time = NULL;

	return Item;
}

namespace {
	qENUM( Extension_ ) {
		eNone,
		eAM,
		ePM,
		e_amount,
		e_Undefined
	};
}

static inline bso::bool__ ExtractItems_(
	const char *&Time,
	item__ &Hours,
	item__ &Minutes,
	item__ &Seconds,
	item__ &Ticks,
	eExtension_ &Extension )
{
	Hours = Minutes = Seconds = Ticks = 0;
	Extension = eNone;

	if ( Time == NULL )
		qRFwk();

	if ( *Time == 0 )
		return false;

	Hours = ExtractItem_( Time );

	if  ( Time == NULL )
		return false;

	if ( *Time && ispunct( *Time ) )
		Time++;

	Minutes = ExtractItem_( Time );

	if  ( Time == NULL )
		return false;

	if ( *Time && ispunct( *Time ) )
		Time++;

	Seconds = ExtractItem_( Time );

	if  ( Time == NULL )
		return false;

	if ( *Time && ispunct( *Time ) )
		Time++;

	Ticks = ExtractItem_( Time );

	while ( ( *Time != 0 ) && isspace( *Time ) )
		Time++;

	if ( *Time != 0 ) {
		char X = tolower( *Time++ );

		if ( ( *Time != 0 ) && ( tolower( *Time++ ) == 'm' ) ) {
			switch ( X ) {
			case 'a':
				Extension = eAM;
				if ( *Time )
				break;
			case 'p':
				Extension = ePM;
				break;
			default:
				Extension = e_Undefined;
				return false;
				break;
			}
		}
		else {
			Extension = e_Undefined;
			return false;
		}
	}

	return true;
}

static inline bso::bool__ TestAndSet_(
	item__ HoursCandidate,
	item__ MinutesCandidate,
	item__ SecondsCandidate,
	item__ TicksCandidate,
	eExtension_ Extension,
	hours__ &Hours,
	minutes__ &Minutes,
	seconds__ &Seconds,
	ticks__ &Ticks )
{
	if ( HoursCandidate < 24 )
		Hours = (hours__)HoursCandidate;
	else
		return false;

	if (  MinutesCandidate < 60 )
		 Minutes = (minutes__)MinutesCandidate;
	else
		return false;

	if (  SecondsCandidate < 60 )
		 Seconds = (seconds__)SecondsCandidate;
	else
		return false;

	if ( TicksCandidate < 1000 )
		 Ticks = TicksCandidate;
	else
		return false;

	switch ( Extension ) {
	case eNone:
		break;
	case eAM:
		if ( Hours > 12 )
			return false;

		if ( Hours == 12 )
			Hours = 0;

		break;
	case ePM:
		if ( Hours > 12 )
			return false;

		if ( Hours == 0 )
			Hours = 12;

		break;
	case e_Undefined:
		return false;
		break;
	default:
		qRFwk();
		break;
	}

	return true;
}

raw_time__ tme::Convert(
	const char *Time,
	const char **End )
{
	item__ HoursCandidate, MinutesCandidate, SecondsCandidate, TicksCandidate;
	hours__ Hours;
	minutes__ Minutes;
	seconds__ Seconds;
	ticks__ Ticks;
	eExtension_ Extension = e_Undefined;

	ExtractItems_( Time, HoursCandidate, MinutesCandidate, SecondsCandidate, TicksCandidate, Extension );

	if ( !TestAndSet_( HoursCandidate, MinutesCandidate, SecondsCandidate, TicksCandidate, Extension, Hours, Minutes, Seconds, Ticks ) )
		return Undefined;

	if ( (End != NULL) && ( *End == NULL ) )
		*End = Time;

	return Convert( Hours, Minutes, Seconds, Ticks );
}
