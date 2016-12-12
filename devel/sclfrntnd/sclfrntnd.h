/*
	Copyright (C) 1999-2016 Claude SIMON (http://q37.info/contact/).

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

#ifndef SCLFRNTND__INC
# define SCLFRNTND__INC

# define SCLFRNTND_NAME		"SCLFRNTND"

# if defined( E_DEBUG ) && !defined( SCLFRNTND_NODBG )
#  define SCLFRNTND_DBG
# endif

// SoCLe FRoNTeND

# include "sclrgstry.h"
# include "sclmisc.h"

# include "fblfrd.h"

# include "plgn.h"

# include "err.h"
# include "flw.h"
# include "xml.h"

// NOTA : 'SCLF_' is used in place of 'SCLFRNTND_' for macro. 

/***************/
/***** OLD *****/
/***************/

namespace sclfrntnd {
	using fblfrd::compatibility_informations__;

	using fblfrd::incompatibility_informations_;
	using fblfrd::incompatibility_informations;

	typedef fblfrd::universal_frontend___ _frontend___;

	// Returns the plugin of id 'Id' path an name for connecting to a remote backend.
	void GetFrontendPluginFilename(
		const str::string_ &Id,
		str::string_ &Filename );

	struct rFeatures {
	public:
		str::string Plugin;	// Name of the plugin.
		const char *Identifier;
		str::string Parameters;
		void reset( bso::bool__ P = true )
		{
			Plugin.reset( P );
			Identifier = NULL;
			Parameters.reset( P );
		}
		E_CDTOR( rFeatures );
		void Init(void)
		{
			Plugin.Init();
			Identifier = NULL;
			Parameters.Init();
		}
	};

	// Below both  definition refers to special backend type. Other backend types refers to a plugin defined in the 'FrontendPlugins' section.
	qCDEF( char *, NoneBackendType, "None" );	// No backend is used.
	qCDEF( char *, PredefinedBackendType, "Predefined" );	// Refers to a predefined backend.

	void SetBackendFeatures(
		const str::dString &BackendType,
		const str::string_ &Parameters,
		rFeatures &Features );

	// Is exposed because, even if there is generally only one kernel per frontend, there could be two (a frontend dealing with two different backends).
	class rKernel
	{
	private:
		plgn::rRetriever<fblovl::cDriver> Retriever_;
		str::wString Plugin_, Parameters_;
		fblovl::cDriver &P_( void )
		{
			return Retriever_.Plugin();
		}
	public:
		void reset( bso::bool__ P = true )
		{
			tol::reset( P, Retriever_, Plugin_, Parameters_ );
		}
		E_CVDTOR( rKernel );
		sdr::sRow Init(
			const rFeatures &Features,
			const plgn::dAbstracts &Abstracts );
		const char *Details( void )
		{
			return Retriever_.Details();
		}
		const str::dString &AboutPlugin( str::dString &About );
		fblovl::eMode Mode( void )
		{
			return P_().Mode();
		}
		csdrcc::rDriver *New( void )
		{
			return P_().New();
		}
		void Delete( csdrcc::rDriver *Driver )
		{
			P_().Delete( Driver );
		}
		void GetFeatures(
			str::dString &Plugin,
			str::dString &Parameters ) const
		{
			Plugin.Append( Plugin_ );
			Parameters.Append( Parameters_ );
		}
	};

	typedef flw::sDressedIOFlow<> sDressedIOFlow_;

	class rIOFlow_
	: public sDressedIOFlow_
	{
	private:
		qRMV( rKernel, K_, Kernel_ );
		qRMV( csdrcc::rDriver, D_, Driver_ );
		void DeleteDriver_( void )
		{
			if ( Driver_ != NULL )
				K_().Delete( Driver_ );
		}
	public:
		void reset( bso::sBool P = true )
		{
			sDressedIOFlow_::reset( P );

			if ( P ) {
				DeleteDriver_();
			}

			Kernel_ = NULL;
			Driver_ = NULL;
		}
		qCDTOR( rIOFlow_ );
		void Init( rKernel &Kernel )
		{
			DeleteDriver_();

			Kernel_ = &Kernel;
			Driver_ = K_().New();

			sDressedIOFlow_::Init( D_() );
		}
	};

	class rFrontend
	: public _frontend___
	{
	private:
		qRMV( rKernel, K_, Kernel_ );
		rIOFlow_ Flow_;
		rgstry::multi_level_registry _Registry;
		rgstry::level__ _RegistryLevel;
		mutable TOL_CBUFFER___ _Language;
	public:
		void reset( bso::bool__ P = true )
		{
			_frontend___::reset( P );
			Flow_.reset( P );
			_Registry.reset( P );
			_RegistryLevel = rgstry::UndefinedLevel;
			_Language.reset();
			Kernel_ = NULL;
		}
		E_CVDTOR( rFrontend );
		void Init(
			rKernel &Kernel,
			const char *Language,
			fblfrd::reporting_callback__ &ReportingCallback );
		void Ping( void );
		void Crash( void );
		bso::bool__ Connect(
			const fblfrd::compatibility_informations__ &CompatibilityInformations,
			fblfrd::incompatibility_informations_ &IncompatibilityInformations );
		void Disconnect( void );
		const rgstry::multi_level_registry_ &Registry( void ) const
		{
			return _Registry;
		}
		const char *Language( void ) const
		{
			return sclrgstry::MGetValue( _Registry, rgstry::tentry___( sclrgstry::parameter::Language ), _Language );
		}
	};

	inline void LoadProject(
		sclmisc::project_type__ Type,
		const str::string_ &Feature )
	{
		sclmisc::LoadProject( Type, Feature );
	}

	void GetProjectsFeatures(
		const char *Language,
		xml::writer_ &Writer );

	void GetBackendsFeatures(
		const char *Language,
		xml::writer_ &Writer );

	void GuessBackendFeatures( rFeatures &Features );	// Set features following what's in registry.

# define SCLF_I( ns, name, id  )\
	namespace ns {\
		typedef fbltyp::s##id tId;\
		E_TMIMIC__( tId, sId );\
		typedef fbltyp::d##id##s dIds;\
		qW( Ids );\
\
		E_CDEF( sId, Undefined, fbltyp::Undefined##id );\
	}\
\
	typedef ns::tId t##name;\
	typedef ns::sId s##name;\
	typedef ns::dIds d##name##s;\
	qW( name##s );\
\
	E_CDEF( s##name, Undefined##name, ns::Undefined )

	template <typename ids> class dI1S
	{
	public:
		struct s {
			typename ids::s Ids;
			str::dStrings::s Strings1;
		};
		ids Ids;
		str::dStrings Strings1;
		dI1S( s &S )
		: Ids( S.Ids ),
		  Strings1( S.Strings1 )
		{}
		void reset( bso::bool__ P = true )
		{
			Ids.reset( P );
			Strings1.reset( P );
		}
		void plug( qASd *AS )
		{
			Ids.plug( AS );
			Strings1.plug( AS );
		}
		dI1S &operator =(const dI1S &I1S)
		{
			Ids = I1S.Ids;
			Strings1 = I1S.Strings1;

			return *this;
		}
		void Init( void )
		{
			Ids.Init();
			Strings1.Init();
		}
		qNAVl( Ids. );
	};

	qW1( I1S );

# define SCLF_I1S( ns, name, id  )\
	SCLF_I( ns, name, id );\
\
	namespace ns {\
		typedef sclfrntnd::dI1S<d##name##s> dI1S;\
		qW( I1S );\
	}\
	typedef ns::dI1S d##name##sI1S;\
	qW( name##sI1S )

	template <typename id> class dI2S	// id, 2 strings.
	: public dI1S<id>
	{
	public:
		struct s
		: public dI1S<id>::s
		{
			str::dStrings::s Strings2;
		};
		str::dStrings Strings2;
		dI2S( s &S )
		: dI1S<id>( S ),
		  Strings2( S.Strings2 )
		{}
		void reset( bso::bool__ P = true )
		{
			dI1S<id>::reset( P );
			Strings2.reset( P );
		}
		void plug( qASd *AS )
		{
			dI1S<id>::plug( AS );
			Strings2.plug( AS );
		}
		dI2S &operator =(const dI2S &I2S)
		{
			dI1S<id>::operator =( I2S );
			Strings2 = I2S.Strings2;

			return *this;
		}
		void Init( void )
		{
			dI1S<id>::Init();
			this->Strings2.Init();
		}
	};

	qW1( I2S );


# define SCLF_I2S( name, id  )\
	namespace ns {\
		typedef sclfrntnd::dI1S<d##name##s> dI2S;\
		qW( I2S );\
	}\
	typedef ns::dI2S d##name##sI2S;\
	qW( name##sI2S )

	E_CDEF( char *, IdAttribute, "id" );
	E_CDEF( char *, AmountAttribute, "Amount" );

	qENUM( Kind ) {
		kTag,
		kAttribute,
		kValue,
		kAttr = kAttribute,
		k_amount,
		k_Undefined,
		k_End = k_Undefined
	};

	inline void Dump_(
		xml::dWriter &Writer,
		eKind Kind )
	{
		switch ( Kind ) {
		case k_End:
			break;
		default:
			qRFwk();
			break;
		}
	}
	
	template <typename ... args> inline void Dump_(
		xml::dWriter &Writer,
		eKind Kind,
		const str::dString *Value,
		const char *Label,
		args... Args )
	{
		switch ( Kind ) {
		case kTag:
			Writer.PutValue( *Value, Label );
			break;
		case kAttribute:
			Writer.PutAttribute( Label, *Value );
			break;
		case kValue:
			Writer.PutValue( *Value );
			break;
		default:
			qRFwk();
			break;
		}

		Dump_( Writer, Args... );
	}

	template <typename ... args> inline void Dump_(
		xml::dWriter &Writer,
		eKind Kind,
		const str::dString *Value,
		args... Args )
	{
		switch ( Kind ) {
		case kValue:
			Writer.PutValue( *Value );
			break;
		default:
			qRFwk();
			break;
		}

		Dump_( Writer, Args... );
	}

	template <typename id, typename... args> inline void Dump_(
		xml::dWriter &Writer,
		id Id,
		args... Args )	// Kind, Value, [Label], kind, value, [Label]... k_End.
	{
		Writer.PutAttribute( IdAttribute, *Id );

		Dump_( Writer, Args... );
	}

	// Root tag is handled by user, so he/she cans put his/her own attributes. 'Amount' attribute is addded.
	template <typename ids> inline void Dump(
		const dI1S<ids> &I1S,
		const char *ItemLabel,
		xml::writer_ &Writer )
	{
		sdr::row__ Row = I1S.First();

		xml::PutAttribute( sclfrntnd::AmountAttribute, I1S.Amount(), Writer );

		while ( Row != qNIL ) {
			Writer.PushTag( ItemLabel );

			Dump_( Writer, I1S.Ids( Row ), kValue, &I1S.Strings1( Row ), k_End );

			Writer.PopTag();

			Row = I1S.Next( Row );
		}
	}
	
	template <typename ids> inline void Dump(
		const dI1S<ids> &I1S,
		const char *ItemsLabel,
		const char *ItemLabel,
		xml::writer_ &Writer )
	{
		Writer.PushTag( ItemsLabel );

		Dump( I1S, ItemLabel, Writer );

		Writer.PopTag();
	}

	// Root tag is handled by user, so he/she cans put his/her own attributes. 'Amount' attribute is addded.
	template <typename ids> inline void Dump(
		const dI1S<ids> &I1S,
		const char *ItemLabel,
		eKind String1LabelKind,
		const char *String1Label,
		xml::writer_ &Writer )
	{
		sdr::row__ Row = I1S.First();

		xml::PutAttribute( sclfrntnd::AmountAttribute, I1S.Amount(), Writer );

		while ( Row != qNIL ) {
			Writer.PushTag( ItemLabel );

			Dump_( Writer, I1S.Ids( Row ), String1LabelKind, &I1S.Strings1( Row ), String1Label, k_End );

			Writer.PopTag();

			Row = I1S.Next( Row );
		}
	}

	template <typename ids> inline void Dump(
		const dI1S<ids> &I1S,
		const char *ItemsLabel,
		const char *ItemLabel,
		eKind String1LabelKind,
		const char *String1Label,
		xml::writer_ &Writer )
	{
		Writer.PushTag( ItemsLabel );

		Dump( I1S, ItemLabel, String1LabelKind, String1Label, Writer );

		Writer.PopTag();
	}


	E_CDEF( char *, LabelAttribute, "label" );

	// Root tag is handled by user, so he/she cans put his/her own attributes. 'Amount' attribute is addded.
	template <typename ids> inline void DumpWithLabelAttribute(
		const sclfrntnd::dI1S<ids> &I1S,
		const char *ItemLabel,
		xml::writer_ &Writer )
	{
		Dump<ids>( I1S, ItemLabel, kAttribute, LabelAttribute, Writer );
	}

	template <typename ids> inline void DumpWithLabelAttribute(
		const sclfrntnd::dI1S<ids> &I1S,
		const char *ItemsLabel,
		const char *ItemLabel,
		xml::writer_ &Writer )
	{
		Dump<ids>( I1S, ItemsLabel, ItemLabel, kAttribute, LabelAttribute, Writer );
	}
}

/***************/
/***** NEW *****/
/***************/

namespace sclfrntnd {

	// Login-related bevaviour.
	qENUM( Login ) {
		lBlank,		// All the fields are left blank,
		lPartial,	// Only the 'Login' field is filled.
		lFull,		// Both 'Login' and 'Password' field are filled.
		lAutomatic,	// The 'Login' page is skipped, and the login parameters are retrieved frrom the configuration file.
		l_amount,
		l_Undefined
	};

	const char *GetLabel( eLogin Login );

	eLogin GetLogin( const str::dString &Pattern );

	eLogin GetLoginParameters(
		str::dString &UserID,
		str::dString &Password );

	eLogin GetLoginFeatures( xml::dWriter &Writer );

	/* An identifier usually identifies the plugin used to access the backend.
	Identifier belows are returned when there in no bckend, or if the backend is embedded. */
	namespace identifier {
		qCDEF(char *, NoneBackendIdentifier, "_NONE" );
		qCDEF(char *, EmbeddedBackendIdentifier, "_EMBEDDED" );
	}

	using fblfrd::cReporting;

	class sReportingCallback
	: public cReporting
	{
	protected:
		virtual void FBLFRDReport(
			fblovl::reply__ Reply,
			const char *Message ) override;
	public:
		void reset( bso::bool__ P = true )
		{
			cReporting::reset( P );
		}
		E_CVDTOR( sReportingCallback );
		void Init( void)
		{
			cReporting::Init();
		}
	};

	const str::dString &About(
		const rFeatures &Features,
		str::dString &About );

	qENUM( BackendSetupType ) {
		bstId,
		bstContent,
		bst_amount,
		bst_Undefined
	};

	const char *GetLabel( eBackendSetupType Type);

	eBackendSetupType GetBackendSetupType( const str::dString &Pattern );

	qENUM( ProjectHandling ) {
		phNone,	// The project is not handled ; it's the one which is selected by default, user can change.
		phLoad,	// The project is loaded.
		phRun,	// Project loaded and run.
		phLogin,	// Project is loaded, but only the login form is displayed ; login can be skipped depoending on loging configuration.
		ph_amount,
		ph_Undefined,
	};

	const char *GetLabel( eProjectHandling );

	eProjectHandling GetProjectHandling( const str::dString &Pattern );

	eProjectHandling HandleProject( void );
}

#endif
