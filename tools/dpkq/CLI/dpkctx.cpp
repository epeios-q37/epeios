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

#include "dpkctx.h"

#include "bitbch.h"
#include "dte.h"
#include "rnd.h"

using namespace dpkctx;

typedef bitbch::qBBUNCHd( sRRow ) dGrid;
qW( Grid );

#define COEFF	3	//

#define CONTEXT_TAG_NAME				"Context"
#define CONTEXTE_TARGET_ATTRIBUTE_NAME	"target"

#define POOL_TAG_NAME	"Pool"

#define POOL_AMOUNT_ATTRIBUTE_NAME			"Amount"
#define POOL_CYCLE_AMOUNT_ATTRIBUTE_NAME	"CycleAmount"
#define POOL_SESSION_AMOUNT_ATTRIBUTE_NAME	"SessionAmount"
#define POOL_TIMESTAMP_ATTRIBUTE_NAME		"TimeStamp"


#define RECORD_TAG_NAME				"Record"
#define RECORD_ROW_ATTRIBUTE_NAME	"Row"

void DumpRecords_(
	const dRRows &Records,
	xml::rWriter &Writer )
{
	sdr::row__ Row = Records.First();

	while ( Row != qNIL ) {
		Writer.PushTag( RECORD_TAG_NAME );
		xml::PutAttribute( RECORD_ROW_ATTRIBUTE_NAME, *Records.Get( Row ), Writer );
		Writer.PopTag();

		Row = Records.Next( Row );
	}
}

// '<Record ...>/<Record>...
//          ^
//						 ^
static sRRow RetrieveRecordId_( xml::parser___ &Parser )
{
	sRRow Id = qNIL;
	bso::bool__ Continue = true;
	sdr::row__ Error = qNIL;

	while ( Continue ) {
		switch ( Parser.Parse( xml::tfObvious ) ) {
		case xml::tAttribute:
			if ( Parser.AttributeName() != RECORD_ROW_ATTRIBUTE_NAME )
				qRGnr();

			Id = Parser.Value().ToUInt( &Error );

			if ( Error != qNIL )
				qRGnr();
			break;
		case xml::tEndTag:
			Continue = false;
			break;
		default:
			qRGnr();
			break;
		}
	}

	if ( Id == qNIL )
		qRGnr();

	return Id;
}

static void Dump_(
	const dPool &Pool,
	xml::rWriter &Writer )
{
	Writer.PushTag( POOL_TAG_NAME );
	Writer.PutAttribute( POOL_AMOUNT_ATTRIBUTE_NAME, Pool.Amount() );
	xml::PutAttribute( POOL_SESSION_AMOUNT_ATTRIBUTE_NAME, Pool.S_.Session, Writer );
	xml::PutAttribute( POOL_CYCLE_AMOUNT_ATTRIBUTE_NAME, Pool.S_.Cycle, Writer );
	xml::PutAttribute( POOL_TIMESTAMP_ATTRIBUTE_NAME, Pool.S_.TimeStamp, Writer );
	DumpRecords_( Pool, Writer );
	Writer.PopTag();
}

void dpkctx::Dump(
	const context_ &Context,
	xml::rWriter &Writer )
{
	Dump_( Context.Pool, Writer );
}

namespace {
	namespace {
		void RetrieveRecords_(
			xml::parser___ &Parser,
			dRRows &Records)
		{
			bso::bool__ Continue = true;

			while ( Continue ) {
				switch ( Parser.Parse(xml::tfObvious) ) {
				case xml::tStartTag:
					if ( Parser.TagName() != RECORD_TAG_NAME )
						qRGnr();

					Records.Append(RetrieveRecordId_(Parser));
					break;
				case xml::tEndTag:
					Continue = false;
					break;
				default:
					qRGnr();
					break;
				}
			}
		}
	}

	void Retrieve_(
		xml::rParser &Parser,
		dPool &Pool)
	{
		bso::sBool Continue = true;

		while ( Continue ) {
			switch ( Parser.Parse(xml::tfObvious | xml::tfStartTagClosed) ) {
			case xml::tAttribute:
				if ( Parser.AttributeName() == POOL_SESSION_AMOUNT_ATTRIBUTE_NAME )
					Pool.S_.Session = Parser.Value().ToUInt();
				else if ( Parser.AttributeName() == POOL_CYCLE_AMOUNT_ATTRIBUTE_NAME )
					Pool.S_.Cycle = Parser.Value().ToUInt();
				else if ( Parser.AttributeName() == POOL_TIMESTAMP_ATTRIBUTE_NAME )
					Pool.S_.TimeStamp = Parser.Value().ToUInt();
				else if ( Parser.AttributeName() != POOL_AMOUNT_ATTRIBUTE_NAME )
					qRGnr();
				break;
			case xml::tStartTagClosed:
				RetrieveRecords_(Parser, Pool);
				Continue = false;
				break;
			default:
				qRGnr();
				break;
			}
		}
	}
}

static void Retrieve_(
	xml::parser___ &Parser,
	context_ &Context )
{
	bso::sBool Continue = true;

	while ( Continue ) {
		switch ( Parser.Parse( xml::tfStartTag | xml::tfEndTag ) ) {
		case xml::tStartTag:
			if ( Parser.TagName() == POOL_TAG_NAME )
				Retrieve_( Parser, Context.Pool );
			else
				qRGnr();
			break;
		case xml::tEndTag:
			Continue = false;
			break;
		default:
			qRGnr();
			break;
		}
	}
}

void dpkctx::Retrieve(
	xml::parser___ &Parser,
	context_ &Context )
{
	Retrieve_( Parser, Context );
}

static amount__ Remove_(
	const dRRows &Records,
	amount__ Amount,
	amount__ TotalAmount,
	dGrid &Grid )
{
	sdr::row__ Row = Records.Last();
	amount__ Counter = 0;

	while ( ( Row != qNIL ) && ( Counter < Amount ) ) {
		if ( *Records( Row ) < TotalAmount ) {
			Grid.Store( false, Records( Row ) );
			Counter++;
		}

		Row = Records.Previous( Row );
	}

	return Counter;
}

static sRRow Pick_( const dGrid &Grid )
{
	sRRow Row = qNIL;

	rnd::InitializeRandomGenerator();

	do {
		Row = rnd::Rand() % Grid.Amount();
	} while ( Grid.Get( Row ) == false );

	return Row;
}

#if 0
static void Add_(
	const dRRows &Source,
	dRRows &Target )
{
	sdr::row__ Row = Source.First();
	sdr::row__ Position = qNIL;

	while ( Row != qNIL ) {
		if ( ( Position = ( Target.Search( Source( Row ) ) ) ) != qNIL )
			Target.Remove( Position );

		Target.Append( Source ( Row ) );

		Row = Source.Next( Row );
	}
}
#endif

static inline bso::bool__ IsNewSession_(
	time_t TimeStamp,
	bso::uint__ Duration )	// in minutes.
{
	if ( Duration == 0 )
		return false;
	else
		return difftime( time( NULL ), TimeStamp ) > ( Duration * 60 );
}

sRRow dpkctx::context_::Pick(
	amount__ Amount,
	bso::uint__ Duration )
{
	sRRow Row = qNIL;
qRH
	wGrid Grid;
	amount__ ToExclude = 0;	// Amount of last picked records to exclude.
qRB
	Grid.Init();
	Grid.Allocate( Amount );

	Grid.Reset( true );

	if ( ( Pool.S_.Session >= Amount ) || IsNewSession_( Pool.S_.TimeStamp, Duration ) ) {
		if ( ( Pool.S_.Session < Amount ) && ( Pool.S_.Session > Pool.S_.Cycle ) )
			Pool.S_.Cycle = Pool.S_.Session;
		Pool.S_.Session = 0;
	}

	if ( Pool.S_.Cycle >= Amount ) {
		Pool.S_.Cycle = 0;
	}


	ToExclude = Amount / 3;

	ToExclude = ( ToExclude > Pool.S_.Session ? ToExclude : Pool.S_.Session );

	ToExclude = ( ToExclude > Pool.S_.Cycle ? ToExclude : Pool.S_.Cycle );

	if ( ( Pool.S_.Cycle == 0 ) && ( Pool.S_.Session == 0 ) )
		ToExclude = 0;

	if ( Pool.Amount() != 0 )
		Pool.Remove( Pool.First(), Pool.Amount() - Remove_( Pool, ToExclude, Amount, Grid ) );

	Row = ::Pick_( Grid );

	Pool.Append( Row );

	Pool.S_.Session++;
	Pool.S_.Cycle++;

	Pool.S_.TimeStamp = time( NULL );
qRR
qRT
qRE
	return Row;
}
