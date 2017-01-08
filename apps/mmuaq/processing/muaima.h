/*
	Copyright (C) 2016-2017 Claude SIMON (http://zeusw.org/epeios/contact.html).

	This file is part of 'MMUAq' software.

    'MMUAq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'MMUAq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'MMUAq'.  If not, see <http://www.gnu.org/licenses/>.
*/

// MUA Internet Message Access protocol (IMAP 4rev1 - RFC 3501).

#ifndef MUAIMA__INC
# define MUAIMA__INC

# ifdef XXX_DBG
#	define MUAIMA__DBG
# endif

# include "muabsc.h"

namespace muaima {

	qENUM( Response ) {
		rCapability,
		r_amount,
		r_None,
		r_Undefined
	};

	typedef fdr::rIDressedDriver rDriver_;

	class rResponseDriver
	: public rDriver_
	{
	private:
		qRMV( flw::sIFlow, F_, Flow_ );
		bso::sBool EOF_;
	protected:
		virtual fdr::sSize FDRRead(
			fdr::sSize Maximum,
			fdr::sByte* Buffer ) override
		{
			bso::sBool Continue = true;
			fdr::sByte Byte = 0;
			fdr::sSize Amount = 0;

			flw::sIFlow &Flow = F_();

			if ( !EOF_ ) {
				while ( Continue ) {
					if ( F_().EndOfFlow() )
						qRGnr();

					Byte = Flow.Get();

					if ( Byte == '\r' ) {
						Continue = false;
						EOF_ = true;

						if ( Flow.EndOfFlow() || ( Flow.Get() != '\n' ) )
							qRGnr();
					} else {
						Buffer[Amount++] = Byte;

						if ( Amount == Maximum )
							Continue = false;
					}
				}
			}
			return Amount;
		}
		virtual void FDRDismiss( bso::sBool Unlock ) override
		{
			F_().Dismiss( Unlock );
		}
		virtual fdr::sTID FDRITake( fdr::sTID Owner ) override
		{
			return F_().IDriver().ITake( Owner );
		}
	public:
		void reset( bso::sBool P = true )
		{
			tol::reset( P, Flow_ );
		}
		qCVDTOR( rResponseDriver );
		void Init( flw::sIFlow &Flow )
		{
			EOF_ = false;
			Flow_ = &Flow;
			rDriver_::Init( fdr::ts_Default );
		}
	};

	class rSession
	{
	private:
		str::wString Tag_;
		flw::sDressedIFlow<> IFlow_;
		txf::rOFlow OFlow_;
		rResponseDriver ResponseDriver_;
	public:
		void reset( bso::sBool P = true )
		{
			tol::reset( P, Tag_, IFlow_, OFlow_ );
		}
		qCDTOR( rSession );
		void Init( fdr::rIODriver &Driver )
		{
			tol::Init( Tag_ );
			IFlow_.Init( Driver );
			OFlow_.Init( Driver );
		}
		const str::dString &GetNextTag( void )
		{
			return muabsc::GetNextIMAPTag( Tag_ );
		}
		const str::dString &GetCurrentTag( void ) const
		{
			if ( Tag_.Amount() == 0)
				qRGnr();

			return Tag_;
		}
		flw::sIFlow &IFlow( void )
		{
			return IFlow_;
		}
		txf::sOFlow &OFlow( void )
		{
			return OFlow_;
		}
		eResponse GetResponse( void );
		fdr::rIDriver &GetDataDriver( void )
		{
			ResponseDriver_.Init( IFlow_ );

			return ResponseDriver_;
		}
		void SkipData( void )
		{
		qRH
			flw::sDressedIFlow<> Flow;
		qRB
			Flow.Init(GetDataDriver() );

			while ( !Flow.EndOfFlow() )
				Flow.Skip();
		qRR
		qRT
		qRE
		}
	};

	namespace base {

		qENUM( Indicator_ ) {
			iOK,
			i_True = iOK,
			iPREAUTH,
			iBYE,
			iNO,
			i_False = iNO,
			iBAD,
			i_Error = iBAD,
			iErroneous = i_Error,	// Server returned a not 'POP3' compliant answer.
			i_amount,
			i_Undefined
		};

		qXENUM( Indicator, i );

		eIndicator Connect( rSession &Session );
		eIndicator Logout( rSession &Session );
		eIndicator Capability( rSession &Session );
		eIndicator Login(
			const str::dString &Username,
			const str::dString &Password,
			rSession &Session );
	}
}


#endif
