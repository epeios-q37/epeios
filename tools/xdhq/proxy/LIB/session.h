/*
	Copyright (C) 2017 Claude SIMON (http://zeusw.org/epeios/contact.html).

	This file is part of 'XDHq' software.

    'XDHq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'XDHq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'XDHq'.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef SESSION_INC_
# define SESSION_INC_

# include "faaspool.h"

# include "csdmnc.h"
# include "logq.h"
# include "xdhcmn.h"
# include "xdhdws.h"

namespace session {

	qMIMICs( bso::sU32, sId_ );
	qCDEF(sId_, UndefinedId_, bso::U32Max);

	extern csdmnc::rCore Core;
	extern logq::rFDriver<> LogDriver;

	qENUM( Mode_ ) {
		mFaaS,	// FaaS mode, direct connexion (not muxed) through the easy to install component.
		mProd,	// Production mode, muxed connexion through the native component.
		m_amount,
		m_Undefined
	};

	class rSession
	: public xdhcmn::cSession,
	  public xdhdws::sProxy
	{
	private:
		eMode_ _Mode_;
		faaspool::rRWDriver FaaSDriver_;
		csdmnc::rRWDriver ProdDriver_;
		struct {
			sId_ Id;
			str::wString IP;
		} Logging_;
		fdr::rRWDriver &D_( void )
		{
			switch ( _Mode_ ) {
			case mFaaS:
				return FaaSDriver_;
				break;
			case mProd:
				return ProdDriver_;
				break;
			default:
				qRGnr();
				break;
			}

#ifdef CPE_C_CLANG
# pragma clang diagnostic push
# pragma clang diagnostic ignored "-Wnull-dereference"
#endif

			return *(fdr::rRWDriver *)NULL;	// To avoid a warning.

#ifdef CPE_C_CLANG
# pragma clang diagnostic pop
#endif

		}
		void Log_( const str::dString &Message );
		void ReportErrorToBackend_(
			const char *Message,
			flw::rWFlow &Flow )
		{
			if ( Message == NULL )
				Message = "";

			prtcl::Put( Message, Flow );	// If 'Message' not empty, client will display content and abort.

			if ( Message[0] ) {
				Flow.Commit();
				qRGnr();
			}
		}
		void ReportNoErrorToBackend_( flw::rWFlow &Flow )
		{
			ReportErrorToBackend_( NULL, Flow );
		}
		void ReportToFrontend_(const str::dString &HTML);
		void ReportErrorToFrontend_(const str::dString &Message);
		bso::bool__ Launch_(
			const char *Id,
			const char *Action );
	protected:
		virtual bso::sBool XDHCMNInitialize(
			xdhcmn::cUpstream &Callback,
			const char *Language,
			const str::dString &Token ) override;
		virtual bso::bool__ XDHCMNLaunch(
			const char *Id,
			const char *Action ) override;
        virtual void XDHCMNBroadcast(const str::dString &Id) override;
	public:
		void reset( bso::sBool P = true )
		{
			tol::reset( P, FaaSDriver_, ProdDriver_ );
			_Mode_ = m_Undefined;
			xdhdws::sProxy::reset( P );
			Logging_.Id = UndefinedId_;
			Logging_.IP.reset( P );
		}
		qCVDTOR( rSession )
		bso::sBool Init( void *)
		{
			tol::reset( FaaSDriver_, ProdDriver_ );
			_Mode_ = m_Undefined;

			Logging_.IP.Init();

			return true;
		}
		operator fdr::rRWDriver &( void )
		{
			return D_();
		}
		fdr::rRWDriver &Driver( void )
		{
			return D_();
		}
	};
}

#endif