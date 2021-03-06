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

#define SCLFRNTND_COMPILATION_

#include "sclfrntnd.h"

#include "scllocale.h"
#include "sclmisc.h"

using namespace sclfrntnd;

using sclrgstry::registry_;

rgstry::entry___ sclfrntnd::registry::parameter::Login( "Login", sclrgstry::Parameters );
rgstry::entry___ sclfrntnd::registry::parameter::login::UserID( "UserID", Login );
rgstry::entry___ sclfrntnd::registry::parameter::login::Password( "Password", Login );


namespace parameter_ {
	rgstry::entry___ Backend_( "Backend", sclrgstry::Parameters );

	namespace backend_ {
		rgstry::entry___ Type_( "@Type", Backend_ );
		rgstry::entry___ Feature_( Backend_ );
	}

	namespace project_ {
		using namespace sclrgstry::parameter::project;

		rgstry::entry___ Handling_( "@Handling", sclrgstry::parameter::Project );
	}

	rgstry::entry___ &Login_ = registry::parameter::Login;

	namespace login_ {
		rgstry::rEntry &UserID_ = registry::parameter::login::UserID;
		rgstry::rEntry &Password_ = registry::parameter::login::Password;
		rgstry::entry___ CypherKey_( "@CypherKey", Login_ );
		rgstry::entry___ Mode_( "@Mode", Login_ );
	}

	rgstry::rEntry Watchdog_( "Watchdog", sclrgstry::Parameters );

	namespace watchdog {
		sclrgstry::rEntry
			Key_( "Key", Watchdog_ ),
			Code_( "Code", Watchdog_ );
	}
}

rgstry::rEntry &sclfrntnd::BackendParametersRegistryEntry = parameter_::Backend_;

namespace definition_ {

	namespace tagged_project_ {
		rgstry::entry___ Alias_( "@Alias", sclrgstry::definition::TaggedProject );
	}

	rgstry::entry___ Backends_( "Backends", sclrgstry::Definitions );

	namespace backends {
		rgstry::entry___ DefaultBackendId( "@Default", Backends_ );

		rgstry::entry___ Backend_( "Backend", Backends_ );

		namespace backend_ {
			rgstry::entry___ Id_( "@id", Backend_ );
		}

		rgstry::entry___ TaggedBackend( RGSTRY_TAGGING_ATTRIBUTE( "id" ), Backend_);

		namespace tagged_backend {
			rgstry::entry___ Alias( "@Alias", TaggedBackend );
			rgstry::entry___ Plugin( "@Plugin", TaggedBackend );
		}
	}

	namespace {
		rgstry::entry___ FrontendPlugins_( "FrontendPlugins", sclrgstry::Definitions );
	}

	namespace frontend_plugins {
		rgstry::entry___ Plugin( "Plugin", FrontendPlugins_ );

		rgstry::entry___ TaggedPlugin( RGSTRY_TAGGING_ATTRIBUTE( "id" ), Plugin );

		namespace tagged_plugin {
			rgstry::entry___ Path( TaggedPlugin );
		}
	}
}

void sclfrntnd::GetFrontendPluginFilename(
	const str::string_ &Id,
	str::string_ &Filename )
{
	if ( Id.Amount() != 0 )
		sclmisc::MGetValue( rgstry::tentry___( definition_::frontend_plugins::tagged_plugin::Path, Id ), Filename );
}


#define C( name )	case l##name : return #name; break

const char *sclfrntnd::GetLabel( eLogin Login )
{
	switch ( Login ) {
	C( Blank );
	C( Partial );
	C( Full );
	C( Automatic );
	default:
		qRFwk();
		break;
	}

	return NULL;	// To avoid a warning.
}

#undef C

namespace {
	stsfsm::wAutomat LoginAutomat_;

	void FillLoginAutomat_( void )
	{
		LoginAutomat_.Init();
		stsfsm::Fill<eLogin>( LoginAutomat_, l_amount, GetLabel );
	}
}

eLogin sclfrntnd::GetLogin( const str::dString &Pattern )
{
	return stsfsm::GetId( Pattern, LoginAutomat_, l_Undefined, l_amount );
}

eLogin sclfrntnd::GetLoginParameters(
	str::dString &UserID,
	str::dString &Password )
{
	eLogin Login = l_Undefined;
qRH
	str::wString Mode;
qRB
	Mode.Init();

	if ( !sclmisc::OGetValue( parameter_::login_::Mode_, Mode ) ) {
		Login = lBlank;
	} else {
		switch ( Login = GetLogin( Mode ) ) {
		case lBlank:
			break;
		case lFull:
		case lAutomatic:
			sclmisc::MGetValue( parameter_::login_::Password_, Password );
		case lPartial:
			sclmisc::MGetValue( parameter_::login_::UserID_, UserID );
			break;
		default:
			sclrgstry::ReportBadOrNoValueForEntryErrorAndAbort( parameter_::login_::Mode_ );
			break;
		}
	}
qRR
qRT
qRE
	return Login;
}

eLogin sclfrntnd::GetLoginFeatures( xml::rWriter &Writer )
{
	eLogin Login = l_Undefined;
qRH
	str::wString UserID, Password;
qRB
	UserID.Init();
	Password.Init();
	Login = GetLoginParameters( UserID, Password );

	Writer.PushTag( "Login" );
	Writer.PutAttribute("Mode", GetLabel( Login ) );

	switch ( Login ) {
	case lBlank:
		break;
	case lFull:
	case lAutomatic:
		Writer.PutValue( Password, "Password" );
	case lPartial:
		Writer.PutValue( UserID, "UserID" );
		break;
	default:
		qRFwk();
		break;
	}
qRR
qRT
qRE
	return Login;
}

void sclfrntnd::sReportingCallback::FBLFRDReport(
	fblovl::reply__ Reply,
	const str::dString &Message )
{
qRH
	str::wString Translation;
qRB
	switch ( Reply ) {
	case fblovl::rRequestError:
		sclmisc::ReportAndAbort( SCLFRNTND_NAME "_RequestError", Message );
		break;
	case fblovl::rSoftwareError:
		sclmisc::ReportAndAbort( SCLFRNTND_NAME "_BackendError", Message );
		break;
	case fblovl::rDisconnected:
		sclmisc::ReportAndAbort( SCLFRNTND_NAME "_Disconnection" );
		break;
	default:
		qRGnr();
		break;
	}
qRR
qRT
qRE
}

#define C( name )	case bst##name : return #name; break

const char *sclfrntnd::GetLabel( eBackendSetupType Type )
{
	switch ( Type ) {
	C( Id );
	C( Content );
	default:
		qRFwk();
		break;
	}

	return NULL;	// To avoid a warning.
}

#undef C

namespace {
	stsfsm::wAutomat BackendSetupTypeAutomat_;

	void FillBackendSetupTypeAutomat_( void )
	{
		BackendSetupTypeAutomat_.Init();
		stsfsm::Fill<eBackendSetupType>( BackendSetupTypeAutomat_, bst_amount, GetLabel );
	}
}

eBackendSetupType sclfrntnd::GetBackendSetupType( const str::dString &Pattern )
{
	return stsfsm::GetId( Pattern, BackendSetupTypeAutomat_, bst_Undefined, bst_amount );
}

static void GetPredefinedItem_(
	const rgstry::entry___ &ValueEntry,
	const rgstry::entry___ &AliasEntry,
	const str::string_ &Id,
	const registry_ &Registry,
	const lcl::locale_ &Locale,
	const char *Language,
	xml::rWriter &Writer )
{
qRH
	str::string Value;
	str::string Translation;
	rgstry::tags Tags;
	TOL_CBUFFER___ Buffer;
qRB
	Tags.Init();
	Tags.Append( Id );

	Value.Init();
	sclrgstry::MGetValue( Registry, rgstry::tentry__( AliasEntry, Tags ), Value );

	Translation.Init();
	Locale.GetTranslation( Value.Convert( Buffer ), Language, Translation );

	Writer.PutAttribute( "Alias", Translation );

	Value.Init();
	sclrgstry::MGetValue( Registry, rgstry::tentry__( ValueEntry, Tags ), Value );

	Writer.PutValue( Value );
qRR
qRT
qRE
}

static void GetPredefinedItems_(
	const char *Tag,
	const rgstry::entry___ &ValueEntry,
	const rgstry::entry___ &AliasEntry,
	const rgstry::values_ &Ids,
	const str::string_ &DefaultProjectId,
	const registry_ &Registry,
	const lcl::locale_ &Locale,
	const char *Language,
	xml::rWriter &Writer )
{
	sdr::row__ Row = Ids.First();

	while ( Row != qNIL ) {
		Writer.PushTag( Tag );
		Writer.PutAttribute( "id", Ids( Row ) );

		if ( DefaultProjectId == Ids( Row ) )
			Writer.PutAttribute("Selected", "true" );

		GetPredefinedItem_( ValueEntry,  AliasEntry, Ids( Row ), Registry, Locale, Language, Writer );

		Writer.PopTag();

		Row = Ids.Next( Row );
	}
}

static void GetPredefinedItems_(
	const char *Tag,
	const rgstry::entry___ &IdEntry,
	const rgstry::entry___ &ParameterDefaultEntry,
	const rgstry::entry___ &DefinitionDefaultEntry,
	const rgstry::entry___ &ValueEntry,
	const rgstry::entry___ &AliasEntry,
	const registry_ &Registry,
	const lcl::locale_ &Locale,
	const char *Language,
	xml::rWriter &Writer )
{
qRH
	rgstry::values Ids;
	str::string DefaultId;
qRB
	DefaultId.Init();
	if ( !sclrgstry::OGetValue(Registry, ParameterDefaultEntry, DefaultId)  || ( DefaultId.Amount() == 0 ) )
		sclrgstry::OGetValue( Registry, DefinitionDefaultEntry, DefaultId );

	Ids.Init();
	sclrgstry::GetValues( Registry, IdEntry, Ids );

	Writer.PutAttribute( "Amount", Ids.Amount() );

	GetPredefinedItems_( Tag, ValueEntry, AliasEntry, Ids, DefaultId, Registry, Locale, Language, Writer );
qRR
qRT
qRE
}

static void GetFeatures_(
	const char *ItemsTag,
	const char *ItemTag,
	const char *DefaultTypeTag,
	const rgstry::entry___ &DefaultTypeEntry,
	const rgstry::entry___ &IdEntry,
	const rgstry::entry___ &ParameterDefaultEntry,
	const rgstry::entry___ &DefinitionDefaultEntry,
	const rgstry::entry___ &ValueEntry,
	const rgstry::entry___ &AliasEntry,
	const char *Language,
	xml::rWriter &Writer )
{
qRH
	str::string DefaultType;
qRB
	DefaultType.Init();

	if ( sclrgstry::OGetValue( sclmisc::GetRegistry(), DefaultTypeEntry, DefaultType ) ) {
		Writer.PushTag( DefaultTypeTag );
		Writer.PutValue( DefaultType );
		Writer.PopTag();
	}

	Writer.PushTag( ItemsTag );
	GetPredefinedItems_( ItemTag, IdEntry, ParameterDefaultEntry, DefinitionDefaultEntry, ValueEntry, AliasEntry, sclmisc::GetRegistry(), scllocale::GetLocale(), Language, Writer );
	Writer.PopTag();
qRR
qRT
qRE
}

bso::bool__ sclfrntnd::rFrontend::Connect(
	const fblfrd::compatibility_informations__ &CompatibilityInformations,
	fblfrd::incompatibility_informations_ &IncompatibilityInformations )
{
	fblfrd::eMode Mode = K_().Mode();

	if ( Mode != fblovl::mNone )
		Flow_.Init( K_() );

	return Frontend_.Connect( Language(), Flow_, Mode, CompatibilityInformations, IncompatibilityInformations );
}

void sclfrntnd::rFrontend::Init(
	rKernel &Kernel,
	const char *Language,
	fblfrd::cFrontend &FrontendCallback,
	fblfrd::cReporting &ReportingCallback )
{
qRH
	str::wString Key;
qRB
	// _Flow.Init(...);	// Made on connection.
	_Registry.Init();
	_Registry.Push( sclmisc::GetRegistry() );
	_RegistryLayer = _Registry.CreateEmbedded( rgstry::name( "Session" ) );

	if ( (Language != NULL) && *Language )
		sclrgstry::SetValue( _Registry, str::string( Language ), rgstry::tentry___( sclrgstry::parameter::Language ) );

	Kernel_ = &Kernel;

	Key.Init();
	sclmisc::OGetValue( parameter_::watchdog::Key_, Key );
	Frontend_.Init( Key, FrontendCallback, ReportingCallback );
qRR
qRT
qRE
}

void sclfrntnd::rFrontend::Ping( void )
{
qRH
	str::wString Code;
qRB
	Code.Init();
	sclmisc::OGetValue( parameter_::watchdog::Code_, Code );
	Frontend_.Ping( Code );	// If 'Code' not empty and correct, the backend doesn't return (watchdog testing purpose).
qRR
qRT
qRE
}

void sclfrntnd::rFrontend::Crash( void )
{
qRH
	str::wString Code;
qRB
	Code.Init();
	sclmisc::MGetValue( parameter_::watchdog::Code_, Code );
	Frontend_.Crash( Code );
qRR
qRT
qRE
}

void sclfrntnd::rFrontend::Disconnect( void )
{
	Frontend_.Disconnect();

	Flow_.reset();
}


void sclfrntnd::GetProjectsFeatures(
	const char *Language,
	xml::rWriter &Writer )
{
qRH
	str::string Pattern;
qRB
	GetFeatures_( "Projects", "Project", "DefaultProjectType", parameter_::project_::Type, sclrgstry::definition::project::Id, sclrgstry::parameter::project::Feature, sclrgstry::definition::DefaultProjectId, sclrgstry::definition::TaggedProject, definition_::tagged_project_::Alias_, Language, Writer );
qRR
qRT
qRE
}

void sclfrntnd::GetBackendsFeatures(
	const char *Language,
	xml::rWriter &Writer )
{
qRH
	str::string Backend, Type;
qRB
	Backend.Init();

	if ( sclrgstry::OGetValue( sclmisc::GetRegistry(), parameter_::backend_::Feature_, Backend ) ) {
		Type.Init();
		sclrgstry::MGetValue( sclmisc::GetRegistry(), parameter_::backend_::Type_, Type );

		Writer.PushTag( "Backend" );
		Writer.PutAttribute( "Type", Type );
		Writer.PutValue( Backend );
		Writer.PopTag();
	}

	GetFeatures_( "Backends", "Backend", "DefaultBackendType", parameter_::backend_::Type_, definition_::backends::backend_::Id_,parameter_::backend_::Feature_, definition_::backends::DefaultBackendId, definition_::backends::Backend_, definition_::backends::tagged_backend::Alias, Language, Writer );
qRR
qRT
qRE
}

static void GetBackendFeatures_(
	const str::string_ &Id,
	rFeatures &Features )
{
	sclrgstry::MGetValue( sclmisc::GetRegistry(), rgstry::tentry___( definition_::backends::tagged_backend::Plugin, Id ), Features.Plugin );
	sclrgstry::OGetValue( sclmisc::GetRegistry(), rgstry::tentry___( definition_::backends::TaggedBackend, Id ), Features.Parameters );
}

namespace {
	void EscapeBackslashs_(
		flw::rRFlow &IFlow,
		flw::rWFlow &OFlow )
	{
		bso::char__ C = 0;

		while ( !IFlow.EndOfFlow() ) {
			if ( ( C = IFlow.Get() ) == '\\' )
				OFlow.Put( '\\' );

			OFlow.Put( C );
		}
	}

	void EscapeBackslashs_(
		const str::dString &In,
		str::dString &Out )
	{
	qRH
		flx::sStringIFlow IFlow;
		flx::rStringOFlow OFlow;
	qRB
		IFlow.Init( In );
		OFlow.Init( Out );

		EscapeBackslashs_( IFlow, OFlow );
	qRR
	qRT
	qRE
	}
}

void sclfrntnd::SetBackendFeatures(
	const str::string_ &BackendType,
	const str::string_ &Parameters,
	rFeatures &Features )
{
qRH
	str::wString Id;
qRB
	if ( ( BackendType.Amount() != 0 ) && ( BackendType != NoneBackendType ) ) {
		if ( BackendType == PredefinedBackendType ) {
			Id.Init( Parameters );

			if ( Parameters.Amount() == 0 )
				sclmisc::MGetValue( definition_::backends::DefaultBackendId, Id );

			GetBackendFeatures_( Id, Features );
		} else {
			Features.Plugin = BackendType;
			EscapeBackslashs_( Parameters, Features.Parameters );
		}
	}
qRR
qRT
qRE
}

sdr::sRow sclfrntnd::rKernel::Init(
	const rFeatures &Features,
	const plgn::dAbstracts &Abstracts )
{
	sdr::sRow Row = qNIL;
qRH
	str::wString PluginFilename;
qRB
	Retriever_.Init();
	Plugin_.Init( Features.Plugin );
	Parameters_.Init( Features.Parameters );

	PluginFilename.Init();

	GetFrontendPluginFilename( Plugin_, PluginFilename );

	if ( Plugin_.Amount() != 0 )
		Row = Retriever_.Initialize( PluginFilename, Features.Identifier, Parameters_, Abstracts );
qRR
qRT
qRE
	return Row;
}

namespace {
	const str::dString &BuildAbout_(
		const str::dString &Identifier,
		const str::dString &Details,
		str::dString &About )
	{
		About.Append( Details );
		About.Append(" - {" );
		About.Append( Identifier );
		About.Append("}" );

		return About;
	}

}

const str::dString &sclfrntnd::rKernel::AboutPlugin( str::dString &About )
{
	if ( Retriever_.IsReady()  )
		return BuildAbout_( str::wString( Retriever_.Details() ), str::wString( Retriever_.Identifier() ), About );
	else
		return sclmisc::GetBaseTranslation( SCLFRNTND_NAME "_NoBackend", About );

}

namespace{
	bso::bool__ GuessBackendFeatures_( rFeatures &Features )
	{
		bso::bool__ BackendFound = false;
	qRH
		str::string Type, Parameters;
	qRB
		Parameters.Init();

		if ( sclmisc::OGetValue( parameter_::backend_::Feature_, Parameters ) ) {
			Type.Init();
			sclmisc::MGetValue( parameter_::backend_::Type_, Type );

			SetBackendFeatures( Type, Parameters, Features );
		}

		BackendFound = true;
	qRR
	qRT
	qRE
		return BackendFound;
	}
}

void sclfrntnd::GuessBackendFeatures( rFeatures &Features )
{
	if ( !GuessBackendFeatures_( Features ) )
		sclmisc::ReportAndAbort( SCLFRNTND_NAME "_MissingBackendDeclaration" );
}

const str::dString &sclfrntnd::About(
	const rFeatures &Features,
	str::dString &About )
{
qRH
	str::wString Filename, Identifier, Details;
qRB
	if ( Features.Plugin.Amount() != 0 ) {
		Filename.Init();
		GetFrontendPluginFilename( Features.Plugin, Filename );;

		Identifier.Init();
		Details.Init();

		plgn::IdentifierAndDetails( Filename, Identifier, Details );

		BuildAbout_( Identifier, Details, About );
	}
qRR
qRT
qRE
	return About;
}

#define C( name )	case ph##name : return #name; break

const char *sclfrntnd::GetLabel( eProjectHandling Handling )
{
	switch ( Handling ) {
	C( None );
	C( Load );
	C( Run );
	C( Login );
	default:
		qRFwk();
		break;
	}

	return NULL;	// To avoid a warning.
}

#undef C

namespace {
	stsfsm::wAutomat ProjectHandlingAutomat_;

	void FillProjectHandlingAutomat_( void )
	{
		ProjectHandlingAutomat_.Init();
		stsfsm::Fill<eProjectHandling>( ProjectHandlingAutomat_, ph_amount, GetLabel );
	}
}

eProjectHandling sclfrntnd::GetProjectHandling( const str::dString &Pattern )
{
	return stsfsm::GetId( Pattern, ProjectHandlingAutomat_, ph_Undefined, ph_amount );
}

eProjectHandling sclfrntnd::HandleProject( const scli::sInfo &Info )
{
	eProjectHandling Handling = phNone;
qRH
	str::wString RawHandling;
qRB
	RawHandling.Init();

	if ( ( sclmisc::OGetValue( parameter_::project_::Handling_, RawHandling ) )
		  && ( RawHandling.Amount() != 0 ) ) {
		Handling = GetProjectHandling( RawHandling );

		if ( Handling == ph_Undefined )
			sclrgstry::ReportBadOrNoValueForEntryErrorAndAbort( parameter_::project_::Handling_ );

		switch ( Handling ) {
		case phLoad:
		case phRun:
		case phLogin:
			sclmisc::LoadProject( Info );
			break;
		default:
			qRGnr();
			break;
		}
	}
qRR
qRT
qRE
	return Handling;
}

namespace {
	void FillAutomats_( void )
	{
		FillLoginAutomat_();
		FillBackendSetupTypeAutomat_();
		FillProjectHandlingAutomat_();
	}
}

Q37_GCTOR( sclfrntnd )
{
	FillAutomats_();
}

