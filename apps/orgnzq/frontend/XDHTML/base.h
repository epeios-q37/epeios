/*
	Copyright (C) 2015-2016 Claude SIMON (http://q37.info/contact/).

	This file is part of 'orgnzq' software.

    'orgnzq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'orgnzq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'orgnzq'.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef BASE__INC
# define BASE__INC

# include "sclxdhtml.h"

# include "ogzfbc.h"
# include "ogzinf.h"

# include "frdinstc.h"

# include "xdhdws.h"

# define BASE_NAME				OGZINF_LC_AFFIX	SCLXDHTML_DEFAULT_SUFFIX
# define BASE_AUTHOR_NAME		OGZINF_AUTHOR_NAME
# define BASE_AUTHOR_CONTACT	OGZINF_AUTHOR_CONTACT
# define BASE_OWNER_NAME		OGZINF_OWNER_NAME
# define BASE_OWNER_CONTACT		OGZINF_OWNER_CONTACT
# define BASE_COPYRIGHT_YEARS	COPYRIGHT_YEARS
# define BASE_COPYRIGHT			BASE_COPYRIGHT_YEARS " " BASE_OWNER_NAME " (" BASE_OWNER_CONTACT ")"
# define BASE_SOFTWARE_NAME		OGZINF_SOFTWARE_NAME
# define BASE_SOFTWARE_VERSION	OGZINF_SOFTWARE_VERSION
# define BASE_SOFTWARE_DETAILS	OGZINF_SOFTWARE_NAME " V" OGZINF_SOFTWARE_VERSION
# define BASE_SOFTWARE_URL		OGZINF_SOFTWARE_URL


/***** Macros dealing with actions ****/
// Declaration.
# define BASE_ACD( name )\
	extern class s##name\
	: public base::cAction\
	{\
	protected:\
		virtual void SCLXLaunch(\
			core::rSession &Session,\
			const char *Id ) override;\
	public:\
		static const char *Name;\
	} name

// Registering.
# define BASE_ACR( name )\
	base::Register( s##name::Name, name );

// Definition.
# define BASE_AC( owner, name )\
	owner::s##name owner::name;\
	const char *owner::s##name::Name = #name;\
	void owner::s##name::SCLXLaunch(\
		core::rSession &Session,\
		const char *Id )
/**********/

// Predeclaration.

namespace core {
	class rSession;
}

namespace core {
	class rSession;
}

namespace base {
	extern const char *Name;

	typedef sclxdhtml::cAction<core::rSession> cAction;

	void Register(
		const char *Name,
		cAction &Callback );

	class sActionHelper
	: public sclxdhtml::cActionHelper<core::rSession>
	{
	protected:
		virtual bso::bool__ SCLXOnBeforeAction(
			core::rSession &Session,
			const char *Id,
			const char *Action ) override;
		virtual void SCLXOnRefresh( core::rSession &Session ) override;
		virtual bso::bool__ SCLXOnClose( core::rSession &Session ) override;
	};

	typedef xdhdws::cCorpus cCorpus_;

	class sCorpusCallback
	: public cCorpus_
	{
	private:
		qRMV( frdfrntnd::rFrontend, F_,  Frontend_ );
	protected:
		virtual void XDHDWSDump( xml::writer_ &Writer ) override
		{
			if ( F_().IsConnected() )
				F_().DumpCorpus( Writer );
		}
	public:
		void reset( bso::bool__ P = true )
		{
			Frontend_ = NULL;
		}
		E_CVDTOR( sCorpusCallback );
		void Init( frdfrntnd::rFrontend &Frontend )
		{
			Frontend_ = &Frontend;
		}
	};

	XDHDWS_RACKS( Name );

	void InitCallback_(
		sCorpusCallback &Callback,
		core::rSession &Session );

	void DumpFocus_(
		const core::rSession &Session,
		xml::dWriter &Writer );

	template <typename rack> class rRack_
	: public rack
	{
	private:
		sCorpusCallback Callback_;
	public:
		void reset( bso::bool__ P = true )
		{
			rack::reset( P );
			Callback_.reset( P );
		}
		E_CDTOR( rRack_ );
		void Init(
			const char *View,
			core::rSession &Session )
		{
			InitCallback_( Callback_, Session );
			rack::Init( View, Callback_ );

			DumpFocus_( Session, *this );
		}
	};

	typedef rRack_<rLayoutRack_> rLayoutRack;
	typedef rRack_<rCastingRack_> rCastingRack;
}

#endif