/*
	'dbpctx' module by Claude SIMON ((http://zeusw.org/epeios/contact.html))
	Part of the 'erpck' tool.
	Copyright (C) 2010 Claude SIMON.
*/

#include "dbpctx.h"

#include "bitbch.h"
#include "dte.h"

using namespace dbpctx;

typedef bitbch::E_BIT_BUNCHt_( rrow__ ) grid_;
E_AUTO( grid );

#define COEFF	3	// 

#define CONTEXT_TAG_NAME				"Context"
#define CONTEXTE_TARGET_ATTRIBUTE_NAME	"target"

#define POOL_TAG_NAME						"Pool"

#define POOL_CYCLE_AMOUNT_ATTRIBUTE_NAME	"CycleAmount"
#define POOL_SESSION_AMOUNT_ATTRIBUTE_NAME	"SessionAmount"
#define POOL_TIMESTAMP_ATTRIBUTE_NAME		"TimeStamp"


#define RECORD_TAG_NAME					"Record"
#define RECORD_ID_ATTRIBUTE_NAME		"Id"

void Dump_(
	const rrows_ &Records,
	xml::writer_ &Writer )
{
	sdr::row__ Row = Records.First();

	while ( Row != E_NIL ) {
		Writer.PushTag( RECORD_TAG_NAME );
		Writer.PutAttribute( RECORD_ID_ATTRIBUTE_NAME, bso::Convert( *Records.Get( Row ) ) );
		Writer.PopTag();

		Row = Records.Next( Row );
	}
}

// '<Record ...>/<Record>...
//          ^
//						 ^
static rrow__ RetrieveRecordId_( xml::parser___ &Parser )
{
	rrow__ Id = E_NIL;
	bso::bool__ Continue = true;
	sdr::row__ Error = E_NIL;

	while ( Continue ) {
		switch ( Parser.Parse( xml::tfObvious ) ) {
		case xml::tAttribute:
			if ( Parser.AttributeName() != RECORD_ID_ATTRIBUTE_NAME )
				ERRFwk();

			Id = Parser.Value().ToUInt( &Error );

			if ( Error != E_NIL )
				ERRFwk();
			break;
		case xml::tEndTag:
			Continue = false;
			break;
		default:
			ERRFwk();
			break;
		}
	}

	if ( Id == E_NIL )
		ERRFwk();

	return Id;
}


// '<... >...</...>...
//        ^
//				   ^
static void Retrieve_(
	xml::parser___ &Parser,
	rrows_ &Records )
{
	bso::bool__ Continue = true;
	sdr::row__ Error = E_NIL;
	rrow__ Row = E_NIL;

	while ( Continue ) {
		switch ( Parser.Parse( xml::tfObvious ) ) {
		case xml::tStartTag:
			if ( Parser.TagName() != RECORD_TAG_NAME )
				ERRFwk();

			Records.Append( RetrieveRecordId_( Parser ) );
			break;
		case xml::tEndTag:
			Continue = false;
			break;
		default:
			ERRFwk();
			break;
		}
	}
}

static void Dump_(
	const pool_ &Pool,
	amount__ SessionAmount,
	amount__ CycleAmount,
	time_t TimeStamp,
	xml::writer_ &Writer )
{
	Writer.PushTag( POOL_TAG_NAME );
	Writer.PutAttribute( POOL_SESSION_AMOUNT_ATTRIBUTE_NAME, bso::Convert( SessionAmount) );
	Writer.PutAttribute( POOL_CYCLE_AMOUNT_ATTRIBUTE_NAME, bso::Convert( CycleAmount) );
	Writer.PutAttribute( POOL_TIMESTAMP_ATTRIBUTE_NAME, bso::Convert( TimeStamp ) );
	Dump_( Pool, Writer );
	Writer.PopTag();
}

void dbpctx::Dump(
	const context_ &Context,
	xml::writer_ &Writer )
{
	Dump_( Context.Pool, Context.S_.Session, Context.S_.Cycle, Context.S_.TimeStamp, Writer );
}

static void RetrievePool_(
	xml::parser___ &Parser,
	context_ &Context )
{

	bso::bool__ Continue = true;

	while ( Continue ) {
		switch( Parser.Parse( xml::tfObvious | xml::tfStartTagClosed ) ) {
		case xml::tStartTag:
			if ( Parser.TagName() != POOL_TAG_NAME )
				ERRFwk();

			break;
		case xml::tAttribute:
			if ( Parser.AttributeName() == POOL_SESSION_AMOUNT_ATTRIBUTE_NAME )
				Context.S_.Session = Parser.Value().ToUInt();
			else if ( Parser.AttributeName() == POOL_CYCLE_AMOUNT_ATTRIBUTE_NAME )
				Context.S_.Cycle = Parser.Value().ToUInt();
			else if ( Parser.AttributeName() == POOL_TIMESTAMP_ATTRIBUTE_NAME )
				Context.S_.TimeStamp = Parser.Value().ToUInt();
			else
				ERRFwk();

			break;
		case xml::tStartTagClosed:
			Retrieve_( Parser, Context.Pool );
			break;
		case xml::tEndTag:
			Continue = false;
			break;
		default:
			ERRFwk();
			break;
		}
	}
}


void dbpctx::Retrieve(
	xml::parser___ &Parser,
	context_ &Context )
{
	RetrievePool_( Parser, Context );
}

static amount__ Remove_(
	const rrows_ &Records,
	amount__ Amount,
	amount__ TotalAmount,
	grid_ &Grid )
{
	sdr::row__ Row = Records.Last();
	amount__ Counter = 0;

	while ( ( Row != E_NIL ) && ( Counter < Amount ) ) {
		if ( *Records( Row ) < TotalAmount ) {
			Grid.Store( false, Records( Row ) );
			Counter++;
		}

		Row = Records.Previous( Row );
	}

	return Counter;
}

static rrow__ Pick_( const grid_ &Grid )
{
	rrow__ Row = E_NIL;

	tol::InitializeRandomGenerator();

	do {
		Row = rand() % Grid.Amount();
	} while ( Grid.Get( Row ) == false );

	return Row;
}

static void Add_(
	const rrows_ &Source,
	rrows_ &Target )
{
	sdr::row__ Row = Source.First();
	sdr::row__ Position = E_NIL;

	while ( Row != E_NIL ) {
		if ( ( Position = ( Target.Search( Source( Row ) ) ) ) != E_NIL )
			Target.Remove( Position );

		Target.Append( Source ( Row ) );

		Row = Source.Next( Row );
	}
}

static inline bso::bool__ IsNewSession_(
	time_t TimeStamp,
	bso::uint__ Duration )	// in minutes.
{
	if ( Duration == 0 )
		return false;
	else
		return difftime( time( NULL ), TimeStamp ) > ( Duration * 60 );
}


rrow__ dbpctx::context_::Pick(
	amount__ Amount,
	bso::uint__ Duration )
{
	rrow__ Row = E_NIL;
ERRProlog
	grid Grid;
	amount__ Applicaple = 0;
ERRBegin
	Grid.Init();
	Grid.Allocate( Amount );

	Grid.Reset( true );

	if ( ( S_.Session >= Amount ) || IsNewSession_( S_.TimeStamp, Duration ) ) {
		if ( ( S_.Session < Amount ) && ( S_.Session > S_.Cycle ) )
			S_.Cycle = S_.Session;
		S_.Session = 0;
	}

	if ( S_.Cycle >= Amount )
		S_.Cycle = 0;

	Applicaple = Amount / 3;

	Applicaple = ( Applicaple > S_.Session ? Applicaple : S_.Session );

	Applicaple = ( Applicaple > S_.Cycle ? Applicaple : S_.Cycle );

	if ( Pool.Amount() != 0 )
		Pool.Remove( Pool.First(), Pool.Amount() - Remove_( Pool, Applicaple, Amount, Grid ) );

	Row = Pick_( Grid );

	Pool.Append( Row );

	S_.Session++;
	S_.Cycle++;

	S_.TimeStamp = time( NULL );
ERRErr
ERREnd
ERREpilog
	return Row;
}

