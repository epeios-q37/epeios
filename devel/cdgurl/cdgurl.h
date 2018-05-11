/*
	Copyright (C) 1999-2017 Claude SIMON (http://q37.info/contact/).

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

// CoDinG URL.
// Based on http://www.geekhideout.com/urlcode.shtml.

#ifndef CDGURL__INC
# define CDGURL__INC

# define CDGURL_NAME		"CDGURL"

# if defined( E_DEBUG ) && !defined( CDGURL_NODBG )
#  define CDGURL_DBG
# endif

# include "cnvfdr.h"
# include "flw.h"
# include "err.h"
# include "tol.h"

# include <ctype.h>

namespace cdgurl {
	typedef fdr::oflow_driver___<> rOFlowDriver_;

	inline fdr::byte__ ToHex_( fdr::byte__ Byte) {
	  static fdr::byte__ Hex[] = "0123456789abcdef";
	  return Hex[Byte&15];
	}

	typedef flw::standalone_oflow__<>	sWFlow_;
	typedef flw::standalone_iflow__<>	sRFlow_;

	typedef cnvfdr::cConverter cConverter_;
	typedef cnvfdr::rConverterRDriver rRDriver_;
	typedef cnvfdr::rConverterWDriver rWDriver_;

	class sURLEncoder_
	: public cConverter_
	{
	protected:
		virtual void CNVFDRConvert(
			flw::sRFlow &In,
			flw::sWFlow &Out )
		{
			fdr::byte__ Byte = 0;

			while ( !In.EndOfFlow() ) {
				switch ( Byte = In.Get() ) {
				default:
					if ( !isalnum( Byte ) ) {
						fdr::byte__ Buffer[3] = { '%' };
						Buffer[1] = ToHex_( Byte >> 4 );
						Buffer[2] = ToHex_( Byte & 15 );
						Out.Write( Buffer, sizeof( Buffer ) );
						break;
					}
				case '-':
				case '_':
				case '.':
				case '~':
					Out.Put( Byte );
					break;
				case ' ':
					Out.Put( '+' );
					break;
				}
			}
		}
	public:
		void reset( bso::sBool = true )
		{
			// Standardization.
		}
		qCVDTOR( sURLEncoder_ );
		void Init( void )
		{
			// Standardization.
		}
	};

	typedef cnvfdr::rConverterRDriver rRDriver_;

	class rURLEncoderRDriver
	: public rRDriver_
	{
	private:
		sURLEncoder_ Encoder_;
	public:
		void reset( bso::sBool P = true )
		{
			rRDriver_::reset( P );
			Encoder_.reset( P );
		}
		qCDTOR( rURLEncoderRDriver );
		void Init(
			fdr::rRDriver &In,
			fdr::thread_safety__ ThreadSafety = fdr::ts_Default )
		{
			Encoder_.Init();
			rRDriver_::Init( Encoder_, In, ThreadSafety );
		}
	};

#if 0

	template <class rURLEncoderRDriver
	: public rRConverter_
	{
	private:
		sURLEncoder Encoder_;
	public:
		void reset( bso::sBool P = true )
		{
			Encoder_.reset( P );
		}
		qCDTOR( rURLEncoderRDriver );
		void Init( void )
		{
			Encoder_.Init();
		}
	};

	class rEncodingRFlow
	: public sWFlow_
	{
	private:
		rEncodeDriver Driver_;
	public:
		void reset( bso::bool__ P = true )
		{
			sWFlow_::reset( P );
			Driver_.reset( P );
		}
		qCDTOR( rEncodingRFlow );
		void Init( flw::oflow__ &Flow )
		{
			Driver_.Init( Flow );
			sOFlow_::Init( Driver_ );
		}
	};


	class rEncodeDriver
	: public rOFlowDriver_
	{
	private:
		qRMV( flw::oflow__, F_, Flow_ );
	protected:
		virtual fdr::size__ FDRWrite(
			const fdr::byte__ *Buffer,
			fdr::size__ Maximum ) override
		{
			fdr::byte__ Byte = 0;
			fdr::size__ Written = 0;

			while ( Written < Maximum ) {
				switch ( Byte = Buffer[Written++] ) {
				default:
					if ( !isalnum( Byte ) ) {
						fdr::byte__ Buffer[3] = { '%' };
						Buffer[1] = ToHex_( Byte >> 4 );
						Buffer[2] = ToHex_( Byte & 15 );
						F_().Write( Buffer, sizeof( Buffer ) );
						break;
					}
				case '-':
				case '_':
				case '.':
				case '~':
					F_().Put( Byte );
					break;
				case ' ':
					F_().Put( '+' );
					break;
				}
			}

			return Written;
		}
		virtual void FDRCommit( bso::sBool Unlock ) override
		{
			F_().Commit( Unlock );
		}
		virtual fdr::sTID FDROTake( fdr::sTID Owner ) override
		{
			 return F_().ODriver().OTake( Owner );
		}
	public:
		void reset( bso::sBool P = true )
		{
			rOFlowDriver_::reset( P );
			Flow_ = NULL;
		}
		qCVDTOR( rEncodeDriver );
		void Init( flw::oflow__ &Flow )
		{
			rOFlowDriver_::Init( fdr::ts_Default );
			Flow_ = &Flow;
		}
	};

	typedef flw::standalone_oflow__<>	sOFlow_;

	class rEncodingOFlow
	: public sOFlow_
	{
	private:
		rEncodeDriver Driver_;
	public:
		void reset( bso::bool__ P = true )
		{
			sOFlow_::reset( P );
			Driver_.reset( P );
		}
		qCDTOR( rEncodingOFlow );
		void Init( flw::oflow__ &Flow )
		{
			Driver_.Init( Flow );
			sOFlow_::Init( Driver_  );
		}
	};

	const str::string_ &Encode(
		const str::string_ &Plain,
		str::string_ &Encoded );

	typedef fdr::iflow_driver___<> rIFlowDriver_;

	inline fdr::byte__ FromHex_( fdr::byte__ Byte )
	{
		if ( !isxdigit( Byte ) )
			qRFwk();

		return isdigit( Byte ) ? Byte - '0' : tolower( Byte ) - 'a' + 10;
	}

	class rDecodeDriver
	: public rIFlowDriver_
	{
	private:
		qRMV( flw::iflow__, F_, Flow_ );
	protected:
		virtual fdr::size__ FDRRead(
			fdr::size__ Maximum,
			fdr::byte__ *Buffer ) override
		{
			fdr::size__ Red = 0;
			bso::sSize Available = 0;
			fdr::byte__ Byte = 0;
			bso::sBool Stop = F_().EndOfFlow() || ( Red >= Maximum );

			while ( !Stop ) {
				switch ( Byte = F_().View() ) {
				case '+':
					F_().Skip();
					Buffer[Red++] = ' ';
					break;
				case '%':
					if ( F_().IsCacheEmpty( &Available ) )
						qRFwk();

					if ( ( Available >= 3 ) || ( Red == 0 ) ) {
						F_().Skip();
						Buffer[Red++] = ( FromHex_( F_().Get() ) << 4 ) + FromHex_( F_().Get() );
					} else
						Stop = true;
					break;
				default:
					Buffer[Red++] = F_().Get();
					break;
				}

				Stop = Stop || ( Red >= Maximum ) || F_().IsCacheEmpty() || F_().EndOfFlow();
			}

			return Red;
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
			rIFlowDriver_::reset( P );
			Flow_ = NULL;
		}
		qCVDTOR( rDecodeDriver );
		void Init( flw::iflow__ &Flow )
		{
			rIFlowDriver_::Init( fdr::ts_Default );
			Flow_ = &Flow;
		}
	};

	typedef flw::standalone_iflow__<> sIFlow_;

	class rDecodingIflow
	: public sIFlow_
	{
	private:
		rDecodeDriver Driver_;
	public:
		void reset( bso::bool__ P = true )
		{
			sIFlow_::reset( P );
			Driver_.reset( P );
		}
		qCDTOR( rDecodingIflow );
		void Init( flw::iflow__ &Flow )
		{
			Driver_.Init( Flow );
			sIFlow_::Init( Driver_  );
		}
	};

	const str::string_ &Decode(
		const str::string_ &Encoded,
		str::string_ &Plain );

#endif
}

#endif
