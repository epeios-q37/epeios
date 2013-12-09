/*
	'scltool.cpp' by Claude SIMON (http://zeusw.org/).

	'scltool' is part of the Epeios framework.

    The Epeios framework is free software: you can redistribute it and/or
	modify it under the terms of the GNU General Public License as published
	by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The Epeios framework is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with The Epeios framework.  If not, see <http://www.gnu.org/licenses/>.
*/

#define SCLTOOL__COMPILATION

#include "scltool.h"

/******************************************************************************/
				  /* do not modify anything above this limit */
				  /*			  unless specified			 */
				  /*******************************************/

#include "cio.h"

#include "sclrgstry.h"
#include "scllocale.h"
#include "sclmisc.h"
#include "sclerror.h"

using namespace scltool;

using cio::COut;
using scllocale::GetLocale;

static STR_BUFFER___ Language_;

#define DEFAULT_LANGUAGE	"en"

static rgstry::multi_level_registry Registry_;

static rgstry::level__ RegistryConfigurationLevel_ = RGSTRY_UNDEFINED_LEVEL;
static rgstry::level__ RegistryProjectLevel_ = RGSTRY_UNDEFINED_LEVEL;
static rgstry::level__ RegistrySetupLevel_ = RGSTRY_UNDEFINED_LEVEL;

const rgstry::multi_level_registry_ &scltool::GetRegistry( void )
{
	return Registry_;
}

rgstry::level__ scltool::GetRegistryConfigurationLevel( void )
{
	return RegistryConfigurationLevel_;
}

rgstry::level__ scltool::GetRegistryProjectLevel( void )
{
	return RegistryProjectLevel_;
}

rgstry::level__ scltool::GetRegistrySetupLevel( void )
{
	return RegistrySetupLevel_;
}


static rgstry::entry___ ArgumentsHandling_( "ArgumentsHandling" );
#define ARGUMENT_TAG "Argument"
#define ARGUMENT_ID_ATTRIBUTE "id"
static rgstry::entry___ ShortTaggedArgument_( RGSTRY_TAGGED_ENTRY( ARGUMENT_TAG, "short" ), ArgumentsHandling_ );
static rgstry::entry___ LongTaggedArgument_( RGSTRY_TAGGED_ENTRY( ARGUMENT_TAG, "long" ), ArgumentsHandling_ );
static rgstry::entry___ IdTaggedArgument_( RGSTRY_TAGGED_ENTRY( ARGUMENT_TAG, ARGUMENT_ID_ATTRIBUTE ), ArgumentsHandling_ );
#define ARGUMENT_TAGGING_ID_ATTRIBUTE "@"  ARGUMENT_ID_ATTRIBUTE
static rgstry::entry___ LongTaggedArgumentId_( ARGUMENT_TAGGING_ID_ATTRIBUTE, LongTaggedArgument_ );
static rgstry::entry___ ShortTaggedArgumentId_( ARGUMENT_TAGGING_ID_ATTRIBUTE, ShortTaggedArgument_ );
static rgstry::entry___ IdTaggedArgumentPath_( "@Path", IdTaggedArgument_ );
static rgstry::entry___ IdTaggedArgumentValue_( "@Value", IdTaggedArgument_ );

static const str::string_ &GetMandatoryValue_( 
	const rgstry::tentry___ &Entry,
	str::string_ &Value )
{
	if ( !Registry_.GetValue( Entry, Value ) )
		sclrgstry::ReportBadOrNoValueForEntryErrorAndAbort( Entry );
}

static const str::string_ &GetLongTaggedArguemntId_(
	str::string_ &Name,
	str::string_ &Id )
{
	return GetMandatoryValue_( rgstry::tentry___( LongTaggedArgumentId_, Name ), Id );
}

static const str::string_ &GetShortTaggedArguemntId_(
	str::string_ &Name,
	str::string_ &Id )
{
	return GetMandatoryValue_( rgstry::tentry___( ShortTaggedArgumentId_, Name ), Id );
}


const char *scltool::GetLanguage( void )
{
	if ( Language_ == NULL )
		return DEFAULT_LANGUAGE;

	return Language_;
}

void scltool::AddDefaultCommands( clnarg::description_ &Description )
{
	Description.AddCommand( CLNARG_NO_SHORT, "version", cVersion );
	Description.AddCommand( CLNARG_NO_SHORT, "help", cHelp );
	Description.AddCommand( CLNARG_NO_SHORT, "license", cLicense );
}


void scltool::PrintDefaultCommandDescriptions(
	const char *ProgramName,
	const clnarg::description_ &Description )
{
ERRProlog
	CLNARG_BUFFER__ Buffer;
	lcl::meaning Meaning;
	str::string Translation;
ERRBegin
	Translation.Init();
	COut << scllocale::GetLocale().GetTranslation( "ProgramDescription", GetLanguage(), Translation ) << txf::nl;
	COut << txf::nl;

	COut << ProgramName << ' ' << Description.GetCommandLabels( cVersion, Buffer ) << txf::nl;
	Meaning.Init();
	clnarg::GetVersionCommandDescription( Meaning );
	Translation.Init();
	GetLocale().GetTranslation( Meaning, GetLanguage(), Translation );
	COut << txf::pad << Translation << '.' << txf::nl;

	COut << ProgramName << ' ' << Description.GetCommandLabels( cLicense, Buffer ) << txf::nl;
	Meaning.Init();
	clnarg::GetLicenseCommandDescription( Meaning );
	Translation.Init();
	GetLocale().GetTranslation( Meaning, GetLanguage(), Translation );
	COut << txf::pad << Translation << '.' << txf::nl;

	COut << ProgramName << ' ' << Description.GetCommandLabels( cHelp, Buffer ) << txf::nl;
	Meaning.Init();
	clnarg::GetHelpCommandDescription( Meaning );
	Translation.Init();
	GetLocale().GetTranslation( Meaning, GetLanguage(), Translation );
	COut << txf::pad << Translation << '.' << txf::nl;

ERRErr
ERREnd
ERREpilog
}

void scltool::ReportAndAbort( const char *Text )
{
ERRProlog
	lcl::meaning Meaning;
ERRBegin
	Meaning.Init();

	Meaning.SetValue( Text );

	ReportAndAbort( Meaning );
ERRErr
ERREnd
ERREpilog
}

void scltool::ReportUnknownOptionErrorAndAbort( const char *Option )
{
ERRProlog
	lcl::meaning Meaning;
ERRBegin
	Meaning.Init();

	clnarg::GetUnknownOptionErrorMeaning( Option, Meaning );

	ReportAndAbort( Meaning );
ERRErr
ERREnd
ERREpilog
}

void scltool::ReportWrongNumberOfArgumentsErrorAndAbort( void )
{
ERRProlog
	lcl::meaning Meaning;
ERRBegin
	Meaning.Init();

	clnarg::GetWrongNumberOfArgumentsErrorMeaning( Meaning );

	ReportAndAbort( Meaning );
ERRErr
ERREnd
ERREpilog
}

void scltool::ReportMissingCommandErrorAndAbort( void )
{
ERRProlog
	lcl::meaning Meaning;
ERRBegin
	Meaning.Init();

	clnarg::GetMissingCommandErrorMeaning( Meaning );

	ReportAndAbort( Meaning );
ERRErr
ERREnd
ERREpilog
}

enum type__ {
	tShort,	// '-...'
	tLong,	// '--...'
	t_amount,
	t_Undefined
};

class flag_
{
public:
	struct s {
		type__ Type;
		str::string_::s Name;
	} &S_;
	str::string_ Name;
	flag_( s &S )
	: S_( S ),
	  Name( S.Name )
	{}
	void reset( bso::bool__ P = true )
	{
		S_.Type = t_Undefined;
		Name.reset( P );
	}
	void plug( sdr::E_SDRIVER__ &SD )
	{
		Name.plug( SD );
	}
	void plug( ags::E_ASTORAGE_ &AS )
	{
		Name.plug( AS );
	}
	flag_ &operator =( const flag_ &F )
	{
		S_.Type = F.S_.Type;
		Name = F.Name;

		return *this;
	}
	void Init( type__ Type = t_Undefined )
	{
		S_.Type = Type;
		Name.Init();
	}
	void Init(
		type__ Type,
		const str::string_ &Name )
	{
		Init( Type );

		this->Name = Name;
	}
	E_RODISCLOSE_( type__, Type );
};

E_AUTO( flag );

typedef ctn::E_MCONTAINER_( flag_ ) flags_;
E_AUTO( flags );

class option_
: public flag_
{
public:
	struct s 
	: public flag_::s
	{
		str::string_::s Value;
	};
	str::string_ Value;
	option_( s &S )
	: flag_( S ),
		Value( S.Value )
	{}
	void reset( bso::bool__ P = true )
	{
		flag_::reset( P );

		Value.reset( P );
	}
	void plug( ags::E_ASTORAGE_ &AS )
	{
		flag_::plug( AS );

		Value.plug( AS );
	}
	option_ &operator =( const option_ &O )
	{
		flag_::operator=( O );

		Value = O.Value;

		return *this;
	}
	void Init( void )
	{
		flag_::Init();

		Value.Init();
	}
	void Init(
		type__ Type,
		const str::string_ &Name,
		const char *Value )
	{
		Init();

		flag_::Init( Type, Name );

		this->Value = Value;
	}
	void Init(
		type__ Type,
		const str::string_ &Name,
		const str::string_ &Value )
	{
		flag_::Init( Type, Name );

		this->Value.Init( Value );
	}
};

E_AUTO( option );

typedef ctn::E_CONTAINER_( option_ ) options_;
E_AUTO( options );


typedef str::string_ argument_;
E_AUTO( argument );

typedef ctn::E_MCONTAINER_( argument_ ) arguments_;
E_AUTO( arguments );

static void ReportBadArgumentAndAbort_(	const char *Arg )
{
ERRProlog
	lcl::meaning Meaning;
ERRBegin
	Meaning.Init();
	Meaning.SetValue( SCLTOOL_NAME "_BadArgument" );
	Meaning.AddTag( Arg );
	ReportAndAbort( Meaning );
ERRErr
ERREnd
ERREpilog
}

void FillShort_(
	const char *First,
	const char *Last,
	flags_ &Flags )
{
ERRProlog
	const char *Current = First;
	flag Flag;
ERRBegin
	while ( Current <= Last ) {
		Flag.Init( tShort, str::string( Current ) );

		Flags.Append( Flag );

		Current++;
	}
ERRErr
ERREnd
ERREpilog
}

void FillShort_(
	const char *Arg,
	options_ &Options )
{
ERRProlog
	const char *Equal = NULL, *Last = NULL;
	option Option;
	str::string Name, Value;
ERRBegin
	Equal = strchr( Arg, '=' );

	if ( ( Equal - Arg  ) != 1 )
		ERRFwk();

	Last = Arg + strlen( Arg );

	Name.Init();
	Name.Append( *Arg );

	Value.Init();
	Value.Append( Equal + 1, Last - Equal -1 );

	Option.Init( tShort, Name, Value );

	Options.Append( Option );
ERRErr
ERREnd
ERREpilog
}

void FillShort_( 
	const char *Arg,
	flags_ &Flags,
	options_ &Options )
{
	const char
		*Equal = strchr( Arg, '=' ),
		*Last = Arg + strlen( Arg ) - 1;

	if ( Equal == NULL )
		FillShort_( Arg, Last, Flags );
	else {
		if ( Equal == Arg )
			ReportBadArgumentAndAbort_( Arg );

		FillShort_( Arg, Equal - 2, Flags );
		FillShort_( Equal - 1, Options );
	}
}

void FillLong_(
	const char *Arg,
	flags_ &Flags )
{
ERRProlog
	flag Flag;
ERRBegin
	Flag.Init( tLong, str::string( Arg ) );

	Flags.Append( Flag );
ERRErr
ERREnd
ERREpilog
}

void FillLong_(
	const char *Arg,
	options_ &Options )
{
ERRProlog
	const char *Equal = NULL, *Last = NULL;
	option Option;
	str::string Name, Value;
ERRBegin
	Equal = strchr( Arg, '=' );

	if ( Equal == Arg  )
		ReportBadArgumentAndAbort_( Arg );

	Last = Arg + strlen( Arg );

	Name.Init();
	Name.Append( Arg, Equal - Arg );

	Value.Init();
	Value.Append( Equal + 1, Last - Equal );

	Option.Init( tShort, Name, Value );

	Options.Append( Option );
ERRErr
ERREnd
ERREpilog
}


static void FillLong_( 
	const char *Arg,
	flags_ &Flags,
	options_ &Options )
{
	const char*Equal = strchr( Arg, '=' );

	if ( Equal == NULL )
		FillLong_( Arg, Flags );
	else
		FillLong_( Arg, Options );

}

bso::bool__ Fill_(
	const char *Arg,
	flags_ &Flags,
	options_ &Options,
	arguments_ &Arguments )
{
	size_t Size = strlen( Arg );

	switch ( Size ) {
	case 0:
		ERRDta();
		break;
	case 1:
		Arguments.Append( str::string( Arg ) );
		break;
	case 2:
		if ( ( Arg[0] == '-' ) && ( Arg[1] == '-' ) )
			return true;

		FillShort_( Arg + 1, Flags, Options );

		break;
	default:
		if ( Arg[0] == '-' )
			if ( Arg[1] == '-' )
				FillLong_( Arg + 2, Flags, Options );
			else
				FillShort_( Arg + 1, Flags, Options );
		else
			Arguments.Append( str::string( Arg ) );
		break;
	}

	return false;
}


void Fill_(
	int argc,
	const char **argv,
	flags_ &Flags,
	options_ &Options,
	arguments_ &Arguments )
{
	int Current = 1;
	bso::bool__ FreeArgumentsOnly = false;

	while ( ( Current < argc ) && ( !FreeArgumentsOnly ) )
	{
		FreeArgumentsOnly = Fill_( argv[Current++], Flags, Options, Arguments );
	}

	while ( Current < argc )
		Arguments.Append( str::string( argv[Current++] ) );
}

static const str::string_ &GetId_(
	const str::string_ &Name,
	rgstry::entry___ &Entry,
	str::string_ &Id )
{
ERRProlog
	rgstry::tags Tags;
	str::string Path;
ERRBegin
	Tags.Init();
	Tags.Append( Name );

	Path.Init();
	Registry_.GetValue( Entry.GetPath( Tags, Path ), Id );
ERRErr
ERREnd
ERREpilog
	return Id;
}

static const str::string_ &GetId_(
	const str::string_ &Name,
	type__ Type,
	str::string_ &Id )
{
	switch ( Type ) {
	case tShort:
		GetId_( Name, ShortTaggedArgumentId_, Id );
		break;
	case tLong:
		GetId_( Name, LongTaggedArgumentId_, Id );
		break;
	default:
		ERRFwk();
		break;
	}

	return Id;
}


static const str::string_ &GetId_(
	const flag_ &Flag,
	str::string_ &Id )
{
	return GetId_( Flag.Name, Flag.Type(), Id );
}

const str::string_ &GetIdTagged_(
	const str::string_ &Id,
	rgstry::entry___ &Entry,
	str::string_ &Path )
{
ERRProlog
	str::strings Tags;
	str::string PathBuffer;
ERRBegin
	Tags.Init();
	Tags.Append( Id );

	PathBuffer.Init();
	Registry_.GetValue( Entry.GetPath( Tags, PathBuffer ), Path );
ERRErr
ERREnd
ERREpilog
	return Path;
}

const str::string_ &GetPath_(
	const str::string_ &Id,
	str::string_ &Path )
{
	return GetIdTagged_( Id, IdTaggedArgumentPath_, Path );
}

const str::string_ &GetValue_(
	const str::string_ &Id,
	str::string_ &Path )
{
	return GetIdTagged_( Id, IdTaggedArgumentValue_, Path );
}

static void FillSetupRegistry_( const flag_ &Flag )
{
ERRProlog
	str::string Id;
	lcl::meaning  Meaning;
	str::strings Tags;
	str::string Path;
	str::string Value;
	sdr::row__ Error = E_NIL;
ERRBegin
	Id.Init();

	if ( GetId_( Flag, Id ).Amount() == 0 ) {
		Meaning.Init();
		Meaning.SetValue( SCLTOOL_NAME "_UnknownFlag" );
		Meaning.AddTag( Flag.Name );
		sclerror::SetMeaning( Meaning );
		ERRAbort();
	}

	Path.Init();
	GetPath_( Id, Path );

	if ( Path.Amount() == 0 ) {
		Meaning.Init();
		Meaning.SetValue( SCLTOOL_NAME "_NoPathForFlag" );
		Meaning.AddTag( Flag.Name );
		sclerror::SetMeaning( Meaning );
		ERRAbort();
	}

	Value.Init();
	GetValue_( Id, Value );

	if ( Value.Amount() == 0 ) {
		Meaning.Init();
		Meaning.SetValue( SCLTOOL_NAME "_NoValueForFlag" );
		Meaning.AddTag( Flag.Name );
		sclerror::SetMeaning( Meaning );
		ERRAbort();
	}

	Registry_.SetValue( Path, Value, &Error );

	if ( Error != E_NIL ) {
		Meaning.Init();
		Meaning.SetValue( SCLTOOL_NAME "_BadPathForFlag" );
		Meaning.AddTag( Flag.Name );
		sclerror::SetMeaning( Meaning );
		ERRAbort();
	}
ERRErr
ERREnd
ERREpilog
}

static void FillSetupRegistry_( const option_ &Option )
{
ERRProlog
	str::string Id;
	lcl::meaning  Meaning;
	str::strings Tags;
	str::string Path;
	sdr::row__ Error = E_NIL;
ERRBegin
	Id.Init();

	if ( GetId_( Option, Id ).Amount() == 0 ) {
		Meaning.Init();
		Meaning.SetValue( SCLTOOL_NAME "_UnknownOption" );
		Meaning.AddTag( Option.Name );
		sclerror::SetMeaning( Meaning );
		ERRAbort();
	}

	Path.Init();
	GetPath_( Id, Path );

	if ( Path.Amount() == 0 ) {
		Meaning.Init();
		Meaning.SetValue( SCLTOOL_NAME "_NoPathForOption" );
		Meaning.AddTag( Option.Name );
		sclerror::SetMeaning( Meaning );
		ERRAbort();
	}

	Registry_.SetValue( Path, Option.Value, &Error );

	if ( Error != E_NIL ) {
		Meaning.Init();
		Meaning.SetValue( SCLTOOL_NAME "_BadPathForOption" );
		Meaning.AddTag( Option.Name );
		sclerror::SetMeaning( Meaning );
		ERRAbort();
	}
ERRErr
ERREnd
ERREpilog
}

template <typename c, typename i> static void FillSetupRegistry_( const c &Conteneur )
{
	i Item;
	sdr::row__ Row = Conteneur.First();

	Item.Init( Conteneur );

	while ( Row != E_NIL ) {
		FillSetupRegistry_( Item( Row ) );

		Row = Conteneur.Next( Row );
	}
}

static void FillSetupRegistry_(
	flags_ &Flags,
	options_ &Options,
	arguments_ &Arguments )
{
	FillSetupRegistry_<flags_, ctn::E_CMITEM( flag_ )>( Flags );
	FillSetupRegistry_<options_, ctn::E_CITEM( option_ )>( Options );
}

#define ARGUMENTS	"_/Arguments"
#define RAW	ARGUMENTS "/Raw"
#define RAW_ARGUMENT	RAW "/Argument"

static void PutIndice_(
	const char *Before,
	bso::uint__ Indice,
	const char *After,
	str::string_ &Result )
{
	bso::integer_buffer__ Buffer;

	Result.Append( Before );
	Result.Append( "[indice=\"" );
	Result.Append( bso::Convert( Indice, Buffer ) );
	Result.Append( "\"]" );

	if ( ( After != NULL ) && ( *After ) ) {
		Result.Append( '/' );
		Result.Append( After );
	}
}

static void DumpInSetupRegistry_(
	int argc,
	const char **argv )
{
ERRProlog
	bso::integer_buffer__ Buffer;
	int i = 0;
	str::string Path;
ERRBegin
	Registry_.SetValue( str::string( RAW "/@Amount" ), str::string( bso::Convert( (bso::int__)argc, Buffer ) ) );

	while ( i < argc ) {
		Path.Init();
		PutIndice_( RAW_ARGUMENT, i, "", Path );

		Registry_.SetValue( Path, str::string( argv[i++] ) );
	}
ERRErr
ERREnd
ERREpilog
}

#define ARGUMENT_FLAGS	ARGUMENTS "/Flags"
#define ARGUMENT_FLAG	ARGUMENT_FLAGS "/Flag"

static void DumpInSetupRegistry_(
	bso::int__ Indice,
	const flag_ &Flag )
{
ERRProlog
	str::string Path;
ERRBegin
	Path.Init();
	PutIndice_( ARGUMENT_FLAG, Indice, "", Path );
	Registry_.SetValue( Path, Flag.Name );
ERRErr
ERREnd
ERREpilog
}

#define ARGUMENT_OPTIONS	ARGUMENTS "/Options"
#define ARGUMENT_OPTION		ARGUMENT_OPTIONS "/Option"

static void DumpInSetupRegistry_(
	bso::int__ Indice,
	const option_ &Option )
{
ERRProlog
	str::string Path;
ERRBegin
	Path.Init();
	PutIndice_( ARGUMENT_OPTION, Indice, "Name", Path );
	Registry_.SetValue( Path, Option.Name );

	Path.Init();
	PutIndice_( ARGUMENT_OPTION, Indice, "Value", Path );
	Registry_.SetValue( Path, Option.Value );
ERRErr
ERREnd
ERREpilog
}

#define ARGUMENT_FREES	ARGUMENTS "/Frees"
#define ARGUMENT_FREE	ARGUMENT_FREES "/Free"

static void DumpInSetupRegistry_(
	bso::int__ Indice,
	const argument_ &Argument )
{
ERRProlog
	str::string Path;
ERRBegin
	Path.Init();
	PutIndice_( ARGUMENT_FREE, Indice, "", Path );
	Registry_.SetValue( Path, Argument );
ERRErr
ERREnd
ERREpilog
}

template <typename c, typename i> static void DumpInSetupRegistry_(
	const char *Prefix,
	const c &Conteneur )
{
ERRProlog
	i Item;
	sdr::row__ Row = Conteneur.First();
	bso::integer_buffer__ Buffer;
	str::string Path;
ERRBegin
	Path.Init( Prefix );
	Path.Append( "/@Amount" );

	Registry_.SetValue( Path, str::string( bso::Convert( Conteneur.Amount(), Buffer ) ) );

	Item.Init( Conteneur );

	while ( Row != E_NIL ) {
		DumpInSetupRegistry_( *Row, Item( Row ) );

		Row = Conteneur.Next( Row );
	}
ERRErr
ERREnd
ERREpilog
}


static void DumpInSetupRegistry_(
	int argc,
	const char **argv,
	const flags_ &Flags,
	const options_ &Options,
	const arguments_ &Arguments )
{
	DumpInSetupRegistry_( argc, argv );

	DumpInSetupRegistry_<flags_, ctn::E_CMITEM( flag_ )>( ARGUMENT_FLAGS, Flags );
	DumpInSetupRegistry_<options_, ctn::E_CITEM( option_ )>( ARGUMENT_OPTIONS, Options );
	DumpInSetupRegistry_<arguments_, ctn::E_CMITEM( argument_ )>( ARGUMENT_FREES, Arguments );
}

static void FillSetupRegistry_(
	int argc,
	const char **argv )
{
ERRProlog
	flags Flags;
	options Options;
	arguments Arguments;
ERRBegin
	Flags.Init();
	Options.Init();
	Arguments.Init();

	Fill_( argc, argv, Flags, Options, Arguments );

	FillSetupRegistry_( Flags, Options, Arguments );

	DumpInSetupRegistry_( argc, argv, Flags, Options, Arguments );
ERRErr
ERREnd
ERREpilog
}


static bso::bool__ ReportSCLPendingError_( void )
{
	return sclerror::ReportPendingError( GetLanguage() );
}

static bso::bool__ main_(
	int argc,
	const char *argv[] )
{
	bso::bool__ Success = false;
ERRProlog
	str::string Language;
ERRBegin
	sclmisc::Initialize( TargetName, NULL );

	Language.Init();

	if ( sclrgstry::GetRegistry().GetValue( sclrgstry::Language, sclrgstry::GetRoot(), Language ) ) 
		Language.Convert( Language_ );

	Registry_.Init();

	RegistryConfigurationLevel_ = Registry_.PushImportedLevel( sclrgstry::GetRegistry(), sclrgstry::GetRoot() );
	RegistryProjectLevel_ = Registry_.PushEmbeddedLevel( str::string( "Project" ) );
	RegistrySetupLevel_ = Registry_.PushEmbeddedLevel( str::string( "Setup" ) );

	FillSetupRegistry_( argc, argv );

	Main( argc, argv );
ERRErr
	if ( ERRType >= err::t_amount ) {
		switch ( ERRType ) {
		case err::t_Abort:
			Success = !ReportSCLPendingError_();
			ERRRst();
			break;
		case err::t_Free:
			ERRRst();
			ERRFwk();
			break;
		case err::t_None:
			ERRRst();
			ERRFwk();
			break;
		case err::t_Return:
			ERRRst();
			ERRFwk();
			break;
		default:
			ERRRst();
			ERRFwk();
			break;
		}
	}
ERREnd
ERREpilog
	return Success;
}

int main(
	int argc,
	const char *argv[] )
{
	int ExitValue = EXIT_SUCCESS;
ERRFProlog
ERRFBegin
	if ( !main_( argc, argv ) )
		ExitValue = EXIT_FAILURE;
ERRFErr
ERRFEnd
	cio::COut << txf::commit;
	cio::CErr << txf::commit;
ERRFEpilog
	return ExitValue;
}

#define PROJECT_ROOT_PATH	"Projects/Project[@target=\"%1\"]"

void scltool::LoadProject(
	const char *FileName,
	const char *Target )
{
ERRProlog
	str::string Path;
	STR_BUFFER___ Buffer;
	rgstry::context___ Context;
	lcl::meaning Meaning;
ERRBegin
	Path.Init( PROJECT_ROOT_PATH );
	str::ReplaceTag( Path, 1, str::string( Target ), '%' );

	if ( Registry_.Fill( RegistryProjectLevel_, FileName, xpp::criterions___(), Path.Convert( Buffer ), Context ) != rgstry::sOK ) {
		Meaning.Init();
		rgstry::GetMeaning( Context, Meaning );
		ReportAndAbort( Meaning );
	};

ERRErr
ERREnd
ERREpilog
}

void scltool::LoadProject(
	const str::string_ &FileName,
	const char *Target )
{
ERRProlog
	STR_BUFFER___ Buffer;
ERRBegin
	LoadProject( FileName.Convert( Buffer ), Target );
ERRErr
ERREnd
ERREpilog
}

bso::bool__ scltool::GetValue(
	const rgstry::tentry__ &Entry,
	str::string_ &Value )
{
	return Registry_.GetValue( Entry, Value );
}

bso::bool__ scltool::GetValues(
	const rgstry::tentry__ &Entry,
	str::strings_ &Values )
{
	return Registry_.GetValues( Entry, Values );
}

const str::string_ &scltool::GetOptionalValue(
	const rgstry::tentry__ &Entry,
	str::string_ &Value,
	bso::bool__ *Missing )
{
	if ( !GetValue( Entry, Value ) )
		if ( Missing != NULL )
			*Missing = true;
	
	return Value;
}

const char *scltool::GetOptionalValue(
	const rgstry::tentry__ &Entry,
	STR_BUFFER___ &Buffer,
	bso::bool__ *Missing )
{
ERRProlog
	str::string Value;
	bso::bool__ LocalMissing = false;
ERRBegin
	Value.Init();

	GetOptionalValue( Entry, Value, &LocalMissing );

	if ( LocalMissing ) {
		if ( Missing != NULL )
			*Missing = true;
	} else
		Value.Convert( Buffer );
ERRErr
ERREnd
ERREpilog
	return Buffer;
}

const str::string_ &scltool::GetMandatoryValue(
	const rgstry::tentry__ &Entry,
	str::string_ &Value )
{
	if ( !GetValue( Entry, Value ) )
		sclrgstry::ReportBadOrNoValueForEntryErrorAndAbort( Entry );

	return Value;
}

const char *scltool::GetMandatoryValue(
	const rgstry::tentry__ &Entry,
	STR_BUFFER___ &Buffer )
{
ERRProlog
	str::string Value;
ERRBegin
	Value.Init();

	GetMandatoryValue( Entry, Value );

	Value.Convert( Buffer );
ERRErr
ERREnd
ERREpilog
	return Buffer;
}

template <typename t> static bso::bool__ GetUnsignedNumber_(
	const rgstry::tentry__ &Entry,
	t Limit,
	t &Value )
{
	bso::bool__ Present = false;
ERRProlog
	str::string RawValue;
	sdr::row__ Error = E_NIL;
ERRBegin
	RawValue.Init();

	if ( !( Present = GetValue( Entry, RawValue ) ) )
		ERRReturn;

	RawValue.ToNumber( Limit, Value, &Error );

	if ( Error != E_NIL )
		sclrgstry::ReportBadOrNoValueForEntryErrorAndAbort( Entry );
ERRErr
ERREnd
ERREpilog
	return Present;
}

template <typename t> static bso::bool__ GetSignedNumber_(
	const rgstry::tentry__ &Entry,
	t LowerLimit,
	t UpperLimit,
	t &Value )
{
	bso::bool__ Present = false;
ERRProlog
	str::string RawValue;
	sdr::row__ Error = E_NIL;
ERRBegin
	RawValue.Init();

	if ( !( Present = GetValue( Entry, RawValue ) ) )
		ERRReturn;

	RawValue.ToNumber( UpperLimit, LowerLimit, Value, &Error );

	if ( Error != E_NIL )
		sclrgstry::ReportBadOrNoValueForEntryErrorAndAbort( Entry );
ERRErr
ERREnd
ERREpilog
	return Present;
}

#define UN( name, type )\
	type scltool::GetMandatory##name(\
		const rgstry::tentry__ &Entry,\
		type Limit  )\
	{\
		type Value;\
\
		if ( !GetUnsignedNumber_( Entry, Limit, Value ) )\
			sclrgstry::ReportBadOrNoValueForEntryErrorAndAbort( Entry );\
\
		return Value;\
	}\
	type scltool::Get##name(\
		const rgstry::tentry__ &Entry,\
		type DefaultValue,\
		type Limit )\
	{\
		type Value;\
\
		if ( !GetUnsignedNumber_( Entry, Limit, Value ) )\
			Value = DefaultValue;\
\
		return Value;\
	}


UN( UInt, bso::uint__ )
#ifdef BSO__64BITS_ENABLED
UN( U64, bso::u64__ )
#endif
UN( U32, bso::u32__ )
UN( U16, bso::u16__ )
UN( U8, bso::u8__ )

#define SN( name, type )\
	type scltool::GetMandatory##name(\
		const rgstry::tentry__ &Entry,\
		type Min,\
		type Max)\
	{\
		type Value;\
\
		if ( !GetSignedNumber_( Entry, Min, Max, Value ) )\
			sclrgstry::ReportBadOrNoValueForEntryErrorAndAbort( Entry );\
\
		return Value;\
	}\
	type scltool::Get##name(\
		const rgstry::tentry__ &Entry,\
		type DefaultValue,\
		type Min,\
		type Max )\
	{\
		type Value;\
\
		if ( !GetSignedNumber_( Entry, Min, Max, Value ) )\
			Value = DefaultValue;\
\
		return Value;\
	}

	SN( SInt, bso::sint__ )
#ifdef BSO__64BITS_ENABLED
	SN( S64, bso::s64__ )
#endif
	SN( S32, bso::s32__ )
	SN( S16, bso::s16__ )
	SN( S8, bso::s8__ )



/* Although in theory this class is inaccessible to the different modules,
it is necessary to personalize it, or certain compiler would not work properly */

class scltoolpersonnalization
{
public:
	scltoolpersonnalization( void )
	{
		/* place here the actions concerning this library
		to be realized at the launching of the application  */
	}
	~scltoolpersonnalization( void )
	{
		/* place here the actions concerning this library
		to be realized at the ending of the application  */
	}
};


				  /********************************************/
				  /* do not modify anything belove this limit */
				  /*			  unless specified		   	  */
/******************************************************************************/

static scltoolpersonnalization Tutor;
