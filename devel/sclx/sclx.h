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

// SoCLe X(DHTML)

/*
NOTA: In this library, the token string is ALWAYS empty and the token row
is ALWAYS equal to 'qNIL'. Token related data are only useful in 'FaS' mode,
and mainly handled by the 'xdhqxdh' and 'faasq' utilities.
*/

#ifndef SCLX_INC_
# define SCLX_INC_

# define SCLX_NAME		"SCLX"

# if defined( E_DEBUG ) && !defined( SCLX_NODBG )
#  define SCLX_DBG
# endif

# include "sclr.h"

# include "dte.h"
# include "err.h"
# include "fblfrd.h"
# include "rgstry.h"
# include "tme.h"
# include "tol.h"

# include "xdhcdc.h"
# include "xdhcmn.h"
# include "xdhdws.h"
# include "xdhutl.h"

# define SCLX_DEFAULT_SUFFIX XDHDWS_DEFAULT_SUFFIX

namespace sclx {
	namespace faas {
		using namespace xdhdws::faas;
	}
	qCDEF( char, DefaultMarker, '#' );

	namespace registry {
		using rgstry::rEntry;

		namespace parameter {
			using namespace sclr::parameter;
		}

		namespace definition {
			using namespace sclr::definition;

			extern rEntry XMLFilesHandling;
			extern rEntry XSLFile;	// To style XML data tagged.
			extern rEntry HeadFile;	// For the head section of the HTML main page. One page only.
		}
	}

	const sclr::registry_ &GetRegistry( void );

	const char *GetLauncher( void );

	template <typename session> class cAction
	{
	protected:
		virtual void SCLXLaunch(
			session &Session,
			const char *Id,
			xdhcdc::eMode Mode ) = 0;
	public:
		qCALLBACK( Action );
		void Launch(
			session &Session,
			const char *Id,
			xdhcdc::eMode Mode )
		{
			return SCLXLaunch( Session, Id, Mode );
		}
	};

	// How the XSL file are handled.
	qENUM( XSLFileHandling )
	{
		xfhName,		// The name of the XSL file is sent (Atlas toolkit behavior).
		xfhContent,		// The content of the XSL file is sent.
		xfhRegistry,	// One of above depending of the content of the registry.
		xfh_amount,
		xfh_Undefined,
		xfh_Default = xfhRegistry,
	};

# define SCLX_ADec( session, label )\
	extern class s##label\
	: public sclx::cAction<session>\
	{\
	protected:\
		virtual void SCLXLaunch(\
			session &Session,\
			const char *Id,\
			xdhcdc::eMode Mode ) override;\
	public:\
		static const char *Label;\
	} label

# define SCLX_ADef( session, owner, label )\
	owner::s##label owner::label;\
	const char *owner::s##label::Label = #label;\
	void owner::s##label::SCLXLaunch(\
		session &Session,\
		const char *Id,\
		xdhcdc::eMode Mode )

	E_ROW( crow__ );	// callback row;

	template <typename session> E_TTCLONE_( bch::E_BUNCHt_( cAction<session> *, crow__ ), action_callbacks_ );

	template <typename session> class actions_handler_
	{
	private:
		cAction<session> *Get_( const str::string_ &Action ) const
		{
			crow__ Row = stsfsm::GetId( Action, Automat );

			if ( Row == qNIL )
				return NULL;

			return Callbacks( Row );
		}
	public:
		struct s {
			stsfsm::automat_::s Automat;
			typename action_callbacks_<session>::s Callbacks;
		};
		stsfsm::automat_ Automat;
		action_callbacks_<session> Callbacks;
		actions_handler_( s &S )
		: Automat( S.Automat ),
			Callbacks( S.Callbacks )
		{}
		void reset( bso::bool__ P = true )
		{
			Automat.reset( P );
			Callbacks.reset( P );
		}
		void plug( qASd *AS )
		{
			Automat.plug( AS );
			Callbacks.plug( AS );
		}
		actions_handler_ &operator =( const actions_handler_ &AH )
		{
			Automat = AH.Automat;
			Callbacks = AH.Callbacks;

			return *this;
		}
		void Init( void )
		{
			Automat.Init();
			Callbacks.Init();
		}
		bso::bool__ Add(
			const char *Name,
			cAction<session> &Callback )
		{
			return stsfsm::Add( Name, *Callbacks.Append( &Callback ), Automat ) == stsfsm::UndefinedId;
		}
		void Launch(
			session &Session,
			const char *Id,
			const char *Action,
			xdhcdc::eMode Mode )
		{
			cAction<session> *Callback = Get_( str::string( Action ) );

			if ( Callback == NULL )
				qRFwk();	// An event has no associated action. Check the'.xsl' file.

			return Callback->Launch( Session, Id, Mode );
		}
	};

	E_AUTO1( actions_handler );

	template <typename session> class cActionHelper
	{
	protected:
		virtual bso::bool__ SCLXOnBeforeAction(
			session &Session,
			const char *Id,
			const char *Action ) = 0;
		virtual void SCLXOnAfterAction(
			session &Session,
			const char *Id,
			const char *Action ) = 0;
		virtual bso::bool__ SCLXOnClose( session &Session ) = 0;
	public:
		void reset( bso::bool__ = true )
		{
			// Standardization.
		}
		E_CVDTOR( cActionHelper );
		void Init( void )
		{
			// Standardization.
		}
		bso::bool__ OnBeforeAction(
			session &Session,
			const char *Id,
			const char *Action )
		{
			return SCLXOnBeforeAction( Session, Id, Action );
		}
		void OnAfterAction(
			session &Session,
			const char *Id,
			const char *Action )
		{
			return SCLXOnAfterAction( Session, Id, Action );
		}
		bso::bool__ OnClose( session &Session )
		{
			return SCLXOnClose( Session );
		}
	};

	class rActions
	{
	private:
		stsfsm::wAutomat Automat_;
	public:
		void reset( bso::sBool P = true )
		{
			Automat_.reset( P );
		}
		qCDTOR( rActions );
		void Init( void )
		{
			Automat_.Init();
		}
		void Add( const char *Action )
		{
			if ( stsfsm::Add( Action, 0, Automat_ ) != stsfsm::UndefinedId )
				qRGnr();
		}
		template <typename action> void Add( const action &Action )
		{
			if ( stsfsm::Add( action::Name, 0, Automat_ ) != stsfsm::UndefinedId )
				qRGnr();
		}
		template <typename action, typename ... args> void Add(
			const action &First,
			const args &... Others )
		{
			Add( First );
			Add( Others... );
		}
		bso::sBool Search( const char *Action )
		{
			return stsfsm::GetId( str::string( Action ), Automat_ ) == 0;
		}
	};

	typedef fblfrd::cReporting cReporting_;

	qENUM( Position ) {
	  pBefore,  // Content put before element.
	  pBegin,   // Content put as first child of element.
	  pInner,   // Content replaces actual content of element.
	  pEnd,     // Content put as last child of element.
	  pAfter,   // Content put after element.
	  p_amount,
	  p_Undefined
	};

	const char *GetLabel_(ePosition Position);

	qENUM( Action )
	{
	  aAdd,
	  aRemove,
	  aToggle,
	  a_amount,
	  a_Undefined
	};

	const char *GetLabel_(eAction Action);

  template <typename type, int amount, typename gl> class sIds
  {
  private:
    bso::sByte Ids_[amount/8+1];
    bso::sSize Offset_(type Id) const
    {
      return Id / 8;
    }
    bso::sByte Mask_(type Id) const
    {
      return 1 << (Id % 8);
    }
    bso::sByte &Block_(type Id)
    {
      return Ids_[Offset_(Id)];
    }
    bso::sByte Block_(type Id) const
    {
      return Ids_[Offset_(Id)];
    }
    void Set_(
      type Id,
      bso::sBool V = true)
    {
      if ( V )
        Block_(Id) |= Mask_(Id);
      else
        Block_(Id) &= ~Mask_(Id);
    }
    void Set_(
      bso::sBool V,
      type Id)
    {
      return Set_(Id,V);
    }
    template <typename ...ids> void Set_(
      bso::sBool V,
      type Id,
      ids ...IdList)
    {
      Set_(V, IdList...);
      Set_(Id, V);
    }
    void Set_(
      const sIds<type, amount, gl> &Ids,
      bso::sBool V)
    {
      for ( int Id = 0; Id < amount; Id++ )
        if ( Ids.IsSet((type)Id) )
          Set_(V, (type)Id);
    }
    void Set_(
      bso::sBool V,
      const sIds<type, amount, gl> &Ids)
    {
      Set_(Ids, V);
    }
    template <typename ...ids> void Set_(
      bso::sBool V,
      const sIds<type, amount, gl> &Ids,
      ids ...IdList)
    {
      Set_(V, IdList...);
      Set_(Ids, V);
    }
    bso::sBool IsSet_(type Id) const
    {
      return Block_(Id) & Mask_(Id);
    }
    void Invert_(type Id)
    {
      Set_(Id, !IsSet_(Id));
    }
    void Invert_(const sIds<type, amount, gl> &Ids)
    {
      for ( int Id = 0; Id < amount; Id++ )
        if ( Ids.IsSet((type)Id) )
          Invert_((type)Id);
    }
    template <typename ...ids> void Invert_(
      type Id,
      const ids &...IdList)
    {
      Invert_(IdList...);
      Invert_(Id);
    }
    template <typename ...ids> void Invert_(
      const sIds<type, amount, gl> &Ids,
      const ids &...IdList)
    {
      Invert_(IdList...);
      Invert_(Ids);
    }
  public:
    void Reset(void)
    {
      memset(Ids_, 0, sizeof(Ids_));
    }
  public:
    void reset(bso::sBool P = true)
    {
      Reset();
    }
    qCDTOR( sIds );
    template <typename ...ids> sIds(ids ...IdList)
    {
      Init();

      Put(IdList...);
    }
    void Init(void)
    {
      Reset();
    }
    template <typename ...ids> void Put(ids ...IdList)
    {
      Set_(true, IdList...);
    }
    template <typename ...ids> void Remove(ids ...IdList)
    {
      Set_(false, IdList...);
    }
    // Inverts the state of the items in 'IdList'.
    template <typename ...ids> void Invert(ids ...IdList)
    {
      Invert_(IdList...);
    }
    bso::sBool IsSet(type Id) const
    {
      return IsSet_(Id);
    }
    void Fill(
      str::dStrings &Ids,
      sdr::sRow *Links ) const
    {
      for ( int Id = 0; Id < amount; Id++ )
        if ( IsSet((type)Id) )
          Links[Id] = Ids.Append(gl::GetLabel((type)Id));
    }
    void Fill(str::dStrings &Ids) const
    {
      sdr::sRow Links[amount];

      Fill(Ids, Links);
    }
  };

  template <typename type, int amount, typename gl> class rValues
  {
  private:
    str::wStrings Values_;
    sdr::sRow Links_[amount];
    void ResetLinks_(void)
    {
      memset(Links_, -1, sizeof(Links_));
    }
  public:
    void reset(bso::sBool P = true)
    {
      Values_.reset(P);
      ResetLinks_();
    }
    qCDTOR(rValues);
    void Init(void)
    {
      ResetLinks_();
      Values_.Init();
    }
    const str::dString &Get(type Id) const
    {
      if ( Id >= amount )
        qRFwk();

      if ( Links_[Id] == qNIL )
        qRFwk();

      return Values_(Links_[Id]);
    }
    const str::dString &Get(
      type Id,
      str::dString &Value) const
    {
      Value = Get(Id);

      return Value;
    }
    const str::dString &Get(
      type Id,
      str::wString &Value) const
    {
      return Get(Id, *Value);
    }
    const char *Get(
      type Id,
      qCBUFFERh &Buffer) const
    {
      return Get(Id).Convert(Buffer);
    }
    template <typename t> bso::sBool Get(
      type Id,
      t &Number,
      qRPD) const
    {
      if ( !Get(Id).ToNumber(Number) )
        if ( qRPT )
          return false;

      return true;
    }
    template <typename t> t Get(type Id) const
    {
      t Value;

      Get(Id, Value);

      return Value;
    }
    void Get(
      type Id,
      dte::sDate &Date,
      dte::eFormat Format) const
    {
    qRH;
      qCBUFFERh Buffer;
    qRB;
      Date.Init(Get(Id, Buffer), Format);
    qRR;
    qRT;
    qRE;
    }
    void Get(
      type Id,
      tme::sTime &Time) const
    {
    qRH;
      qCBUFFERh Buffer;
    qRB;
      Time.Init(Get(Id, Buffer));
    qRR;
    qRT;
    qRE;
    }
    friend class sProxy;
  };

  template <typename type, int amount, typename gl> class rTValues
  {
  private:
    str::wStrings
      Ids_,
      Values_;
    sdr::sRow Add_(
      type Id,
      const str::dString &Value)
    {
      if ( Id >= amount )
        qRFwk();

      sdr::sRow Row = Ids_.Append(gl::GetLabel(Id));

      if ( Row != Values_.Append(Value))
        qRFwk();

      return Row;
    }
    sdr::sRow Add_(
      const str::dString &Id,
      const str::dString &Value)
    {
      sdr::sRow Row = Ids_.Append(Id);

      if ( Row != Values_.Append(Value))
        qRFwk();

      return Row;
    }
  public:
    void reset(bso::sBool P = true)
    {
      tol::reset(P, Ids_, Values_);
    }
    qCDTOR( rTValues );
    void Init(void)
    {
      tol::Init(Ids_, Values_);
    }
    template <typename id> sdr::sRow Add(
      const id &Id,
      const str::dString &Value)
    {
      return Add_(Id, Value);
    }
    template <typename id> sdr::sRow Add(
      const id &Id,
      const char *Value)
    {
      return Add_(Id, Value);
    }
    template <typename id> sdr::sRow Add(
      const id &Id,
      const str::wString &Value)
    {
      return Add_(Id, Value);
    }
    template <typename id> sdr::sRow Add(
      const id &Id,
      dte::sDate Date,
      dte::eFormat Format)
    {
      dte::pBuffer Buffer;

      if ( Date.IsSet() )
        return Add(Id, Date.ASCII(Format, Buffer));
      else
        return Add(Id, "");
    }
    template <typename id> sdr::sRow Add(
      const id &Id,
      tme::sTime Time)
    {
      tme::pBuffer Buffer;

      if ( Time.IsSet() )
        return Add(Id, Time.ASCII(Buffer));
      else
        return Add(Id, "");
    }
    template <typename id, typename t> sdr::sRow Add(
      const id &Id,
      t Value)
    {
      bso::pInteger Buffer;

      return Add(Id, bso::Convert(Value, Buffer));
    }
    friend class sProxy;
  };

	class sProxy
	{
	private:
		xdhdws::sProxy Core_;
		qRMV( const scli::sInfo, I_, Info_ );
		eXSLFileHandling XSLFileHandling_;
		template <typename s> void Fill_(
			str::dStrings &Values,
			const s &Value )
		{
			Values.Append(Value);
		}
		void Fill_(
			str::dStrings &Values,
			const str::dStrings &SplittedValues );
		void Fill_(
			str::dStrings &Values,
			const str::wStrings &SplittedValues )
    {
      Fill_(Values, *SplittedValues);
    }
    template <typename type, int amount, typename gl> void Fill_(
      str::dStrings &Values,
      const sIds<type, amount, gl> &Ids)
    {
    qRH;
      str::wStrings SplittedValues;
    qRB;
      SplittedValues.Init();

      Ids.Fill(SplittedValues);

      Fill_(Values, SplittedValues);
    qRR;
    qRT;
    qRE;
    }
		template <typename s, typename ...args> void Fill_(
			str::dStrings &Values,
			const s &Value,
			const args &...Args )
		{
			Fill_(Values, Value);
			Fill_(Values, Args...);
		}
		template <typename ...args> void Process_(
			const char *ScriptName,
			str::dString *Result,
			const args &...Args )
		{
		qRH
			str::wStrings Values;
		qRB
			Values.Init();
			Fill_(Values, Args...);
			Core_.Process(ScriptName, Values, Result);
		qRR
		qRE
		qRT
		}
		template <typename ...args> const str::dString &Process_(
			const char *ScriptName,
			str::dString &Buffer,
			const args &...Args )
		{
			Process_(ScriptName, &Buffer, Args...);

			return Buffer;
		}
		template <typename ...args> const char *Process_(
			const char *ScriptName,
			qCBUFFERh &Buffer,
			const args &...Args )
		{
		qRH
			str::wString Return;
		qRB
			Return.Init();
			Process_(ScriptName, &Return, Args...);
			Return.Convert(Buffer);
		qRR
		qRE
		qRT
			return Buffer;
		}
		template <typename ...args> const str::dString &Process_(
			const char *TaggedScript,
			const char *TagList,
			str::dString &Buffer,
			const args &...Args )
		{
			Process_(TaggedScript, TagList, &Buffer, Args...);

			return Buffer;
		}
		template <typename ...args> const char *Process_(
			const char *TaggedScript,
			const char *TagList,
			qCBUFFERh &Buffer,
			const args &...Args )
		{
		qRH
			str::wString Return;
		qRB
			Return.Init();
			Process_(TaggedScript, TagList, &Return, Args...);
			Return.Convert(Buffer);
		qRR
		qRE
		qRT
			return Buffer;
		}
		void Execute_(
			const str::dString &Script,
			str::dString *Result )
		{
			Process_("Execute_1", Result, Script);
		}
    void Alert_(
			const str::dString &XML,
			const str::dString &XSL,
			const str::dString &Title,
			const char *Language );
		void Alert_(
			const str::dString &Message,
			const str::dString &Title,
			const char *MessageLanguage,	// If != 'NULL', 'Message' is translated, otherwise it is displayed as is.
			const char *CloseTextLanguage );
		bso::bool__ Confirm_(
			const str::dString &XML,
			const str::dString &XSL,
			const str::dString &Title,
			const char *Language )
		{
			qRLmt();
			// Reactivate in '.cpp'.
			return false;
		}
		bso::sBool Confirm_(
			const str::dString &Message,
			const char *MessageLanguage,	// If != 'NULL', 'Message' is translated, otherwise it is displayed as is.
			const char *CloseTextLanguage );
		void HandleLayout_(
			const char *Variant,
			const str::dString &Id,
			const rgstry::rEntry &XSLFilename,
			const char *Target,
			const sclr::registry_ &Registry,
			const str::dString &XML,
			bso::char__ Marker);
		template <typename ids> void HandleClasses_(
			eAction Action,
			const ids &Ids,
			const str::dStrings &Classes)
		{
			Process_("HandleClasses_1", NULL, GetLabel_(Action), Ids, Classes);
		}
		void HandleClasses_(
			eAction Action,
			const str::dStrings &Ids,
			const str::dString &Class);  // Applies same class to all ids.
    template <typename type, int amount, typename gl> void HandleClasses_(
      eAction Action,
      const sIds<type, amount, gl> &Ids,
      const str::dString &Class)
    {
    qRH;
      str::wStrings IdsAsStrings;
    qRB;
      IdsAsStrings.Init();

      Ids.Fill(IdsAsStrings);

      HandleClasses_(Action, IdsAsStrings, Class);
    qRR;
    qRT;
    qRE;
    }
		template <typename c1, typename c2> void GetValue_(
			const c1 &Id,
			c2 &Buffer )
		{
		qRH;
			str::wStrings Values;
		qRB;
			Values.Init();
			GetValues(str::wStrings(Id), Values);
			str::Recall(Values, Buffer);
		qRR;
		qRT;
		qRE;
		}
		template <typename c1, typename c2> void GetMark_(
			const c1 &Id,
			c2 &Buffer )
		{
		qRH;
			str::wStrings Marks;
		qRB;
			Marks.Init();
			GetMarks(str::wStrings(Id), Marks);
			str::Recall(Marks, Buffer);
		qRR;
		qRT;
		qRE;
		}
	protected:
		template <typename session, typename rack, typename chars> void HandleLayout_(
			const char *Variant,
			const chars &Id,
			const char *Target,
			const sclr::registry_ &Registry,
			void( *Get )(session &Session, xml::rWriter &Writer),
			session &Session,
			bso::char__ Marker = DefaultMarker )
		{
		qRH;
			rack Rack;
		qRB;
			Rack.Init( Target, Session, I_() );

			Get( Session, Rack() );

			HandleLayout_( Variant, Id, registry::definition::XSLFile, Target, Registry, Rack.Target(), Marker );
		qRR;
		qRT;
		qRE;
		}
		void HandleLayout_(
      const str::dString &Position,
      const str::dString &Id,
      const str::dString &XML,
      const str::dString &XSL)
    {
    qRH;
      str::wString Dummy;
    qRB;
      Dummy.Init();

      Process_("HandleLayout_1", &Dummy, Position, Id, XML, XSL); // The primitive returns a string, hence the 'Dummy' parameter,
                                                                  // but which is not handled by the user.
    qRR;
    qRT;
    qRE;
    }
		void HandleLayout_(
      ePosition Position,
      const str::dString &Id,
      const str::dString &XML,
      const str::dString &XSL)
    {
      return HandleLayout_(GetLabel_(Position), Id, XML, XSL);
    }
	public:
		void reset( bso::sBool P = true )
		{
			tol::reset( P, Core_, Info_ );
			XSLFileHandling_ = xfh_Undefined;
		}
		qCDTOR( sProxy );
		bso::sBool Init(
			xdhcuc::cSingle &Callback,
			const scli::sInfo &Info,
			eXSLFileHandling XSLFileHandling)
		{
			if ( !Core_.Init(Callback) )
        return false;

			Info_ = &Info;
			XSLFileHandling_ = XSLFileHandling;

			if ( tol::IsDev() )
        DebugLog();

			return true;
		}
		const scli::sInfo &Info( void ) const
		{
			return I_();
		}
		void Execute(
			const str::dString &Script,
			str::dString &Result )
		{
			Execute_(Script, &Result);
		}
		void Execute(const str::dString &Script)
		{
			Execute_(Script, NULL);
		}
		template <typename ...args> void Execute(
			const char *TaggedScript,
			const char *TagList,
			str::dString *Result,
			const args &...Args )
		{
			Process_(TaggedScript, TagList, Result, Args...);
		}
		void DebugLog(bso::sBool Switch = true)
		{
			Process_("DebugLog_1", NULL, Switch ? "true" : "false");
		}
		template <typename s> void Log( const s &Message )
		{
			Process_("Log_1", NULL, Message);
		}
		// The basic alert, without use of 'JQuery' based widget.
		void AlertB( const str::dString & Message );
		void Alert(
			const str::dString &XML,
			const str::dString &XSL,
			const str::dString &Title,
			const char *Language );
		void AlertT(
			const str::dString &RawMessage,
			const str::dString &RawTitle,
			const char *Language );	// Translates 'Message'.
		void AlertU(
			const str::dString &Message,
			const str::dString &Title,
			const char *Language );	// Displays 'Message' as is. 'Language' is used for the closing text message.
		// The basic confirm, without use of 'JQuery' based widget.
		bso::sBool ConfirmB(const str::dString & Message);
		bso::bool__ Confirm(
			const str::dString &XML,
			const str::dString &XSL,
			const str::dString &Title,
			const char *Language )
		{
			return Confirm_( XML, XSL, Title, Language );
		}
		bso::bool__ ConfirmT(
			const str::dString &RawMessage,
			const char *Language );
		bso::bool__ ConfirmU(
			const str::dString &Message,
			const char *Language );	// Displays 'Message' as is. 'Language' is used for the closing text message.
    void Put(
      const str::dString &Id,
      ePosition Position,
      const str::dString &XML,
      const str::dString &XSL = str::Empty)
    {
      return HandleLayout_(Position, Id, XML, XSL);
    }
    void Before(
      const str::dString &Id,
      const str::dString &XML,
      const str::dString &XSL = str::Empty)
    {
      return Put(Id, pBefore, XML, XSL);
    }
    void Begin(
      const str::dString &Id,
      const str::dString &XML,
      const str::dString &XSL = str::Empty)
    {
      return Put(Id, pBegin,XML, XSL);
    }
    void Inner(
      const str::dString &Id,
      const str::dString &XML,
      const str::dString &XSL = str::Empty)
    {
      return Put(Id, pInner, XML, XSL);
    }
    void End(
      const str::dString &Id,
      const str::dString &XML,
      const str::dString &XSL = str::Empty)
    {
      return Put(Id, pEnd, XML, XSL);
    }
    void After(
      const str::dString &Id,
      const str::dString &XML,
      const str::dString &XSL = str::Empty)
    {
      return Put(Id, pAfter, XML, XSL);
    }
    void SetAttribute(
			const str::dString &Id,
			const str::dString &Name,
			const str::dString &Value )
		{
			Process_("SetAttribute_1", NULL, Id, Name, Value);
		}
		const char *GetAttribute(
			const str::dString &Id,
			const str::dString &Name,
			qCBUFFERh &Value )
		{
			qRLmt();
			return Value();
		}
		const str::dString &GetAttribute(
			const str::dString &Id,
			const str::dString &Name,
			str::dString &Value )
		{
			qRLmt();
			return Value;
		}
		void RemoveAttribute(
			const str::dString &Id,
			const str::dString &Name )
		{
      Process_("RemoveAttribute_1", NULL, Id, Name);
		}
		template <typename ids> void GetValues(
			const ids &Ids,
			str::dStrings &Values )
    {
    qRH;
      str::wString MergedValues;
    qRB;
      MergedValues.Init();

      Process_("GetValues_1", &MergedValues, Ids);

      xdhcmn::FlatSplit(MergedValues, Values);
    qRR;
    qRT;
    qRE;
    }
    template <typename type, int amount, typename gl> void GetValues(
      const sIds<type, amount, gl> &Ids,
      rValues<type, amount, gl> &Values)
    {
    qRH;
      str::wStrings IdsAsStrings;
    qRB;
      IdsAsStrings.Init();

      Ids.Fill(IdsAsStrings, Values.Links_);

      GetValues(IdsAsStrings, Values.Values_);
    qRR;
    qRT;
    qRE;
    }
		const str::dString &GetValue(
			const str::dString &Id,
			str::dString &Buffer )
		{
			GetValue_(Id, Buffer);

			return Buffer;
		}
		const char *GetValue(
			const str::dString &Id,
			qCBUFFERh &Buffer )
		{
			GetValue_(Id, Buffer);

			return Buffer;
		}
		bso::sBool GetBoolValue(const str::dString &Id)
    {
      bso::sBool Result = false;
    qRH;
      qCBUFFERh Buffer;
    qRB;
      Result = strcmp( GetValue(Id, Buffer), "false") != 0;
    qRR;
    qRT;
    qRE;
      return Result;
    }
    template <typename ids> void GetMarks(
			const ids &Ids,
			str::dStrings &Marks )
    {
      qRH;
        str::wString MergedMarks;
      qRB;
        MergedMarks.Init();

        Process_("GetMarks_1", &MergedMarks, Ids);

        xdhcmn::FlatSplit(MergedMarks, Marks);
      qRR;
      qRT;
      qRE;
      }
		const str::dString &GetMark(
			const str::dString &Id,
			str::dString &Buffer )
		{
			GetMark_(Id, Buffer);

			return Buffer;
		}
		const char *GetMark(
			const str::dString &Id,
			qCBUFFERh &Buffer )
		{
			GetMark_(Id, Buffer);

			return Buffer;
		}
    template <typename ids> void SetValues(
			const ids &Ids,
			const str::dStrings &Values )
		{
			Process_("SetValues_1", NULL, Ids, Values);
		}
		void SetValue(
			const str::dString &Id,
			const str::dString &Value )
		{
			return SetValues(str::wStrings(Id),str::wStrings(Value));
		}
		template <typename type, int amount, typename gl> void SetValues(const rTValues<type, amount, gl> &Values)
		{
		  return SetValues(Values.Ids_, Values.Values_);
		}
		void Focus( const str::dString &Id )
		{
				Process_("Focus_1", NULL, Id);
		}
		const char *Parent(
			const str::dString &Id,
			qCBUFFERh &Value )
		{
			Process_("Parent_1", Value, Id);

			return Value;
		}
		const char *FirstChild(
			const str::dString &Id,
			qCBUFFERh &Value )
		{
			Process_("FirstChild_1", Value, Id);

			return Value;
		}
		const char *LastChild(
			const str::dString &Id,
			qCBUFFERh &Value )
		{
			Process_("LastChild_1", Value, Id);

			return Value;
		}
		const char *PreviousSibling(
			const str::dString &Id,
			qCBUFFERh &Value )
		{
			Process_("PreviousSibling_1", Value, Id);

			return Value;
		}
		const char *NextSibling(
			const str::dString &Id,
			qCBUFFERh &Value )
		{
			Process_("NextSibling_1", Value, Id);

			return Value;
		}
		void InsertChild(
			const str::dString &Child,
			const str::dString &Id )
		{
			qRLmt();
		}
		void AppendChild(
			const str::dString &Child,
			const str::dString &Id )
		{
			qRLmt();
		}
		void InsertBefore(
			const str::dString &Sibling,
			const str::dString &Id )
		{
			qRLmt();
		}
		void InsertAfter(
			const str::dString &Sibling,
			const str::dString &Id )
		{
			qRLmt();
		}
		/*
		void InsertCSSRule(
			const str::dString &Rule,
			xdhcmn::sIndex Index );
		xdhcmn::sIndex AppendCSSRule( const str::dString &Rule );
		void RemoveCSSRule( xdhcmn::sIndex Index );
		*/
		template <typename c, typename ids> void AddClasses(
			const ids &Ids,
			const c &Classes )
		{
			return HandleClasses_(aAdd, Ids, Classes);
		}
		template <typename c> void AddClass(
			const str::dString &Id,
			const c &Class )
		{
			return AddClasses(str::wStrings(Id), Class);
		}
		template <typename c, typename ids> void RemoveClasses(
			const ids &Ids,
			const c &Classes )
		{
			return HandleClasses_(aRemove, Ids, Classes);
		}
		template <typename c> void RemoveClass(
			const str::dString &Id,
			const c &Class )
		{
			return RemoveClasses(str::wStrings(Id), Class);
		}
		template <typename c, typename ids>  void ToggleClasses(
			const ids &Ids,
			const c &Classes )
		{
			return HandleClasses_(aToggle, Ids, Classes);
		}
		template <typename c> void ToggleClass(
			const str::dString &Id,
			const c &Class )
		{
			return ToggleClasses(str::wStrings(Id), Class);
		}
		template <typename ids> void EnableElements( const ids &Ids )
		{
      Process_("EnableElements_1", NULL, Ids);
		}
		void EnableElement( const str::dString &Id )
		{
		  return EnableElements(Id);
		}
		template <typename ids> void Enable(const ids &Ids)
		{
		  EnableElements(Ids);
		}
		template <typename ids> void DisableElements(const ids &Ids)
		{
      Process_("DisableElements_1", NULL, Ids);
		}
		void DisableElement(const str::dString &Id)
		{
		  return DisableElements(Id);
		}
		template <typename ids> void Disable(const ids &Ids)
		{
		  DisableElements(Ids);
		}
		void ScrollTo(const str::dString &Id)
		{
      Process_("ScrollTo_1", NULL, Id);
		}
		const char *Dummy(
			const str::dString &Id,
			qCBUFFERh &Value )
		{
			qRLmt();
			return Value;
		}
	};

	class sReporting
	: public cReporting_
	{
	private:
		Q37_MRMDF( sProxy, P_, Proxy_ );
		Q37_MPMDF( const char, L_, Language_ );
	protected:
		virtual void FBLFRDReport(
			fblovl::reply__ Reply,
			const str::dString &Message ) override
		{
			if ( Reply == fblovl::rDisconnected )
				P_().AlertT("SCLXHTML_Disconnected", str::Empty, L_());
			else {
				//				sclmisc::ReportAndAbort( Message );
				P_().AlertU( Message, str::Empty, L_() );
				qRAbort();
			}
		}
	public:
		void reset( bso::bool__ P = true )
		{
			Proxy_ = NULL;
		}
		E_CVDTOR( sReporting );
		void Init(
			sProxy &Proxy,
			const char *Language )
		{
			Proxy_ = &Proxy;
			Language_ = Language;
		}
	};

	void HandleError(
		sProxy &Proxy,
		const char *Language );

	template <typename session, typename dump> class rRack
	{
	private:
		str::wString Target_;
		mutable flx::E_STRING_TOFLOW___ _Flow;
		xml::rWriter _Writer;
	public:
		void reset( bso::bool__ P = true )
		{
			tol::reset( P, Target_, _Flow, _Writer );
		}
		E_CDTOR( rRack );
		void Init(
			const char *View,
			session &Session,
			const scli::sInfo &Info )
		{
			tol::buffer__ Buffer;
			xml::sMark Mark = xml::Undefined;

			Target_.Init();
			_Flow.Init( Target_ );
			_Writer.Init( _Flow, xml::oIndent, xml::e_Default );
			_Writer.PushTag( "XDHTML" );
			_Writer.PutAttribute( "View", View );
			_Writer.PutAttribute( "Generator", Info.Target() );
			_Writer.PutAttribute( "TimeStamp", tol::DateAndTime( Buffer ) );
			_Writer.PutAttribute( "OS", cpe::GetOSDigest() );
			Mark = _Writer.PushTag( "Corpus" );
			dump::Corpus( Session, _Writer );
			_Writer.PopTag( Mark );
			_Writer.PushTag( "Layout" );
			dump::Common( Session, _Writer );
		}
		operator xml::rWriter &()
		{
			return _Writer;
		}
		xml::rWriter &operator()( void )
		{
			return _Writer;
		}
		const str::dString &Target( void )
		{
			_Writer.reset();	// To close all tags.
			_Flow.Commit();

			return Target_;
		}
	};

	void Broadcast(
		const str::dString &Action,
		const str::dString &Id = str::Empty);

	inline void LoadXSLAndTranslateTags(
		const rgstry::tentry__ &FileName,
		const sclr::registry_ &Registry,
		str::string_ &Content,
		bso::char__ Marker = DefaultMarker )
	{
		return sclm::LoadXMLAndTranslateTags( FileName, Registry, Content, 0, Marker );
	}

	const scli::sInfo &SCLXInfo( void );	// To define by user.
	void SCLXInitialization( xdhcdc::eMode Mode );	// To define by user.

	xdhcdc::cSingle *SCLXFetchCallback();	// To define by user.

	void SCLXDismissCallback( xdhcdc::cSingle *Callback );	// To define by user.

	extern bso::sBool (* SCLXGetHead)(str::dString &Head);  // To override for head handling by user.

// 'typedef SXLX_VALUESr(…) …'
# define SCLX_TVALUESr(type, amount, label_retriever)\
class\
: public sclx::rTValues_<type, amount>\
{\
public:\
  void Init(void)\
  {\
    rTValues_::Init(label_retriever);\
  }\
}

}

/*************/
/**** NEW ****/
/*************/

namespace sclx {
  template <typename session> qTCLONE(actions_handler<session>, rActionsHandler);
};

#endif
