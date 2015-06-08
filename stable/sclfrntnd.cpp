/*
	Copyright (C) 2000-2015 Claude SIMON (http://q37.info/contact/).

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

#define SCLFRNTND__COMPILATION

#include "sclfrntnd.h"

/******************************************************************************/
				  /* do not modify anything above this limit */
				  /*			  unless specified			 */
				  /*******************************************/

#include "scllocale.h"
#include "sclmisc.h"

using namespace sclfrntnd;

using sclrgstry::registry_;

static rgstry::entry___ DefaultProjectType_("DefaultProjectType", sclrgstry::Parameters );
static rgstry::entry___ ProjectAction_("@Action", DefaultProjectType_ );
static rgstry::entry___ PredefinedProjects_( "PredefinedProjects", sclrgstry::Definitions );
static rgstry::entry___ DefaultPredefinedProject_( "@Default", PredefinedProjects_ );
static rgstry::entry___ FreePredefinedProject_( "PredefinedProject", PredefinedProjects_ ); 
static rgstry::entry___ PredefinedProjectId_( "@id", FreePredefinedProject_ );
static rgstry::entry___ PredefinedProject_( RGSTRY_TAGGING_ATTRIBUTE( "id" ), FreePredefinedProject_);
static rgstry::entry___ PredefinedProjectAlias_( "@Alias", PredefinedProject_ );

static rgstry::entry___ Backend_( "Backend", sclrgstry::Parameters );
static rgstry::entry___ BackendAccessMode_( "@AccessMode", Backend_ );
static rgstry::entry___ BackendType_( "@Type", Backend_ );
static rgstry::entry___ BackendPingDelay_( "PingDelay", Backend_ );

static rgstry::entry___ Authentication_( "Authentication", sclrgstry::Parameters );
static rgstry::entry___ AuthenticationCypherKey_( "@CypherKey", Authentication_ );
static rgstry::entry___ AuthenticationMode_( "@Mode", Authentication_ );
static rgstry::entry___ AuthenticationLogin_( "Login", Authentication_ );
static rgstry::entry___ AuthenticationPassword_( "Password", Authentication_ );

static rgstry::entry___ DefaultBackendType_("DefaultBackendType", sclrgstry::Parameters );
static rgstry::entry___ PredefinedBackends_( "PredefinedBackends", sclrgstry::Definitions );
static rgstry::entry___ DefaultPredefinedBackend_( "@Default", PredefinedBackends_ );
static rgstry::entry___ FreePredefinedBackend_( "PredefinedBackend", PredefinedBackends_ ); 
static rgstry::entry___ PredefinedBackendId_( "@id", FreePredefinedBackend_ );
static rgstry::entry___ PredefinedBackend_( RGSTRY_TAGGING_ATTRIBUTE( "id" ), FreePredefinedBackend_);
static rgstry::entry___ PredefinedBackendAlias_( "@Alias", PredefinedBackend_ );
static rgstry::entry___ PredefinedBackendType_( "@Type", PredefinedBackend_ );

static rgstry::entry___ Internals_( "Internals" );
static rgstry::entry___ ProjectId_( "ProjectId", Internals_ );

stsfsm::automat ActionAutomat_;

bso::bool__ sclfrntnd::kernel___::Init(
	const features___ &Features,
	csdsnc::log_callback__ *LogCallback )
{
	bso::bool__ Success = false;
qRH
	csdlec::library_data__ LibraryData;
	csdleo::mode__ Mode = csdleo::m_Undefined;
	TOL_CBUFFER___ Buffer;
qRB
	LibraryData.Init( csdleo::cRegular, Features.Location.Convert( Buffer ), err::qRRor, sclerror::SCLERRORError );

	if ( !_ClientCore.Init( Features, LibraryData, LogCallback ) )
		qRReturn;

	Success = true;
qRR
qRT
qRE
	return Success;
}



static void FillActionAutomat_( void )
{
	ActionAutomat_.Init();
	stsfsm::Fill( ActionAutomat_, a_amount, GetLabel );
}

#define A( name )	case a##name : return #name; break

const char *sclfrntnd::GetLabel( action__ Action )
{
	switch ( Action ) {
	A( None );
	A( Load );
	A( Launch );
	default:
		qRFwk();
		break;
	}

	return NULL;	// To avoid a 'warning'.
}

action__ sclfrntnd::GetAction( const str::string_ &Pattern )
{
	return stsfsm::GetId( Pattern, ActionAutomat_, a_Undefined, a_amount );
}

static const lcl::meaning_ &GetMeaning_(
	const char *Message,
	lcl::meaning &Meaning )
{
qRH
	str::string RefinedMessage;
qRB
	RefinedMessage.Init( "FRD_" );
	RefinedMessage.Append( Message );

	Meaning.SetValue( RefinedMessage );
qRR
qRT
qRE
	return Meaning;
}

static void GetPredefinedItem_(
	const rgstry::entry___ &ValueEntry,
	const rgstry::entry___ &AliasEntry,
	const str::string_ &Id,
	const registry_ &Registry,
	const lcl::locale_ &Locale,
	const char *Language,
	xml::writer_ &Writer )
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
	xml::writer_ &Writer )
{
	ctn::E_CMITEM( rgstry::value_ ) Id;
	sdr::row__ Row = Ids.First();

	Id.Init( Ids );

	while ( Row != qNIL ) {
		Writer.PushTag( Tag );
		Writer.PutAttribute( "id", Id( Row ) );

		if ( DefaultProjectId == Id( Row ) )
			Writer.PutAttribute("Selected", "true" );

		GetPredefinedItem_( ValueEntry,  AliasEntry, Id( Row ), Registry, Locale, Language, Writer );

		Writer.PopTag();

		Row = Ids.Next( Row );
	}
}

static void GetPredefinedItems_(
	const char *Tag,
	const rgstry::entry___ &IdEntry,
	const rgstry::entry___ &DefaultEntry,
	const rgstry::entry___ &ValueEntry,
	const rgstry::entry___ &AliasEntry,
	const registry_ &Registry,
	const lcl::locale_ &Locale,
	const char *Language,
	xml::writer_ &Writer )
{
qRH
	rgstry::values Ids;
	str::string DefaultId;
qRB
	DefaultId.Init();
	sclrgstry::OGetValue( Registry, DefaultEntry, DefaultId );

	Ids.Init();
	sclrgstry::GetValues( Registry, IdEntry, Ids );

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
	const rgstry::entry___ &DefaultEntry,
	const rgstry::entry___ &ValueEntry,
	const rgstry::entry___ &AliasEntry,
	const char *Language,
	xml::writer_ &Writer )
{
qRH
	str::string DefaultType;
qRB
	DefaultType.Init();
	sclrgstry::OGetValue( sclrgstry::GetCommonRegistry(), DefaultTypeEntry, DefaultType );

	if ( DefaultType.Amount() != 0 ) {
		Writer.PushTag( DefaultTypeTag );
		Writer.PutValue( DefaultType );
		Writer.PopTag();
	}

	Writer.PushTag( ItemsTag );
	GetPredefinedItems_( ItemTag, IdEntry, DefaultEntry, ValueEntry, AliasEntry, sclrgstry::GetCommonRegistry(), scllocale::GetLocale(), Language, Writer );
	Writer.PopTag();
qRR
qRT
qRE
}

action__ sclfrntnd::GetProjectsFeatures(
	const char *Language,
	xml::writer_ &Writer )
{
	action__ Action = aNone;
qRH
	str::string Pattern;
qRB
	Pattern.Init();
	sclrgstry::OGetValue( sclrgstry::GetCommonRegistry(), ProjectAction_, Pattern );

	if ( Pattern.Amount() != 0 )
		if ( ( Action = GetAction( Pattern ) ) == a_Undefined )
			sclrgstry::ReportBadOrNoValueForEntryErrorAndAbort( ProjectAction_ );

	GetFeatures_( "PredefinedProjects", "PredefinedProject", "DefaultProjectType", DefaultProjectType_, PredefinedProjectId_, DefaultPredefinedProject_, PredefinedProject_, PredefinedProjectAlias_, Language, Writer );
qRR
qRT
qRE
	return Action;
}

void sclfrntnd::GetBackendsFeatures(
	const char *Language,
	xml::writer_ &Writer )
{
qRH
	str::string Backend, Type;
qRB
	Backend.Init();
	sclrgstry::OGetValue( sclrgstry::GetCommonRegistry(), Backend_, Backend );

	if ( Backend.Amount() != 0 ) {
		Type.Init();
		sclrgstry::MGetValue( sclrgstry::GetCommonRegistry(), BackendType_, Type );

		Writer.PushTag( "Backend" );
		Writer.PutAttribute( "Type", Type );
		Writer.PutValue( Backend );
		Writer.PopTag();
	}

	GetFeatures_( "PredefinedBackends", "PredefinedBackend", "DefaultBackendType", DefaultBackendType_, PredefinedBackendId_, DefaultPredefinedBackend_, PredefinedBackend_, PredefinedBackendAlias_, Language, Writer );
qRR
qRT
qRE
}

bso::uint__ sclfrntnd::GetBackendPingDelay( void )
{
	return sclrgstry::OGetUInt(sclrgstry::GetCommonRegistry(), BackendPingDelay_, 0 );
}

static void LoadProject_( const str::string_ &FileName )
{
qRH
	str::string Id;
qRB
	Id.Init();
	sclmisc::LoadProject( FileName, Id );
qRR
qRT
qRE
}

static void LoadPredefinedProject_( const str::string_ &Id )
{
qRH
	str::string ProjectFileName;
qRB
	if ( Id.Amount() == 0 )
		sclmisc::ReportAndAbort( SCLFRNTND_NAME "_EmptyPredefinedProjectId" );

	ProjectFileName.Init();
	sclrgstry::MGetValue(sclrgstry::GetCommonRegistry(), rgstry::tentry___( PredefinedProject_, Id ), ProjectFileName );

	if ( ProjectFileName.Amount() == 0 )
		sclmisc::ReportAndAbort( SCLFRNTND_NAME "_NoOrBadProjectFileNameInPredefinedProject", Id );

	LoadProject_( ProjectFileName );
qRR
qRT
qRE
}

void sclfrntnd::LoadProject(
	frdbse::project_type__ ProjectType,
	const str::string_ &ProjectFeature )
{
	switch ( ProjectType ) {
	case frdbse::ptNew:
		sclrgstry::EraseProjectRegistry();
		break;
	case frdbse::ptPredefined:
		LoadPredefinedProject_( ProjectFeature );
		break;
	case frdbse::ptUser:
		if ( ProjectFeature.Amount() == 0  )
			sclmisc::ReportAndAbort( SCLFRNTND_NAME "_NoProjectFileSelected" );
		LoadProject_( ProjectFeature );
		break;
	case frdbse::pt_Undefined:
		qRFwk();
		break;
	default:
		qRFwk();
		break;
	}
}

static void GetPredefinedBackendFeatures_(
	const str::string_ &Id,
	features___ &Features )
{
qRH
	str::string Buffer;
	rgstry::tentry___ BackendTypeEntry;
qRB
	BackendTypeEntry.Init( PredefinedBackendType_, Id );

	Buffer.Init();
	switch ( frdbse::GetBackendType(sclrgstry::MGetValue(sclrgstry::GetCommonRegistry(), BackendTypeEntry, Buffer ) ) ) {
	case frdbse::btDaemon:
		Features.Type = csducl::tDaemon;
		break;
	case frdbse::btEmbedded:
		Features.Type = csducl::tPlugin;
		break;
	default:
		sclrgstry::ReportBadOrNoValueForEntryErrorAndAbort( BackendTypeEntry );
		break;
	}

	sclrgstry::MGetValue(sclrgstry::GetCommonRegistry(), rgstry::tentry___( PredefinedBackend_, Id ), Features.Location );
qRR
qRT
qRE
}

void sclfrntnd::LaunchProject(
	kernel___ &Kernel,
	frdbse::backend_type__ BackendType,
	const str::string_ &BackendFeature )
{
qRH
	features___ Features;
qRB
	Features.Init();

	Features.PingDelay = GetBackendPingDelay();

	switch ( BackendType ) {
	case frdbse::btDaemon:
		Features.Type = csducl::tDaemon;
		Features.Location = BackendFeature;
		break;
	case frdbse::btEmbedded:
		Features.Type = csducl::tPlugin;
		Features.Location = BackendFeature;
		break;
	case frdbse::btPredefined:
		GetPredefinedBackendFeatures_( BackendFeature, Features );
		break;
	case frdbse::pt_Undefined:
		qRFwk();
		break;
	default:
		qRFwk();
		break;
	}

	if ( !Kernel.Init( Features ) ) {
		sclmisc::ReportAndAbort( SCLFRNTND_NAME "_UnableToConnectToBackend", Features.Location );
	}
qRR
qRT
qRE
}


static void FillAutomats_( void )
{
	FillActionAutomat_();
}

Q37_GCTOR( sclfrntnd )
{
	FillAutomats_();
}
