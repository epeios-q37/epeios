/*
	Copyright (C) 2016 Claude SIMON (http://zeusw.org/epeios/contact.html).

	This file is part of 'XDHDq' software.

    'XDHDq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'XDHDq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'XDHDq'.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef CORE_INC_
# define CORE_INC_

# include "base.h"
# include "instc.h"

# include "sclxdhtml.h"

namespace core {
	extern sclxdhtml::rActionHelper OnNotConnectedAllowedActions;

	class rInstances
	{
	public:
		instc::rUser User;
		void reset( bso::bool__ P = true )
		{
			User.reset( P );
		}
		E_CVDTOR( rInstances );
		void Init( frdfrntnd::rFrontend &Frontend );
	};

	class sDump {
	public:
		static void Corpus(
			rInstances &Instances,
			xml::dWriter &Writer );
		static void Common(
			rInstances &Instances,
			xml::dWriter &Writer );
	};

	typedef sclxdhtml::rSession < rInstances, frdfrntnd::rFrontend, base::ePage, base::p_Undefined, sDump > rSession;

	class sActionHelper
	: public sclxdhtml::cActionHelper<core::rSession>
	{
	protected:
		virtual bso::bool__ SCLXOnBeforeAction(
			core::rSession &Session,
			const char *Id,
			const char *Action ) override;
		virtual void SCLXOnRefresh( core::rSession &Session ) override;
		virtual bso::sBool SCLXOnClose( core::rSession &Session ) override;
	};

	class rCore
	: public sclxdhtml::rCore<rSession>
	{
	private:
		sActionHelper ActionHelperCallback_;
	public:
		void reset( bso::bool__ P = true )
		{
			ActionHelperCallback_.reset( P );
		}
		E_CDTOR( rCore );
		void Init( xdhcmn::eMode Mode );
	};

	extern rCore Core;

	sclfrntnd::rKernel &Kernel( void );

	void About(
		rSession &Session,
		xml::writer_ &Writer );
}

#endif