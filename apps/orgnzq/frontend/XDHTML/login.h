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

#ifndef LOGIN__INC
# define LOGIN__INC

# include "base.h"

namespace login {
	BASE_ACD( SwitchBackendType );
	BASE_ACD( DisplayEmbeddedBackendFilename );
	BASE_ACD( Connect );
	BASE_ACD( Dismiss );

	class fActionCallbacks
	{
	public:
		BASE_ACU( SwitchBackendType );
		BASE_ACU( DisplayEmbeddedBackendFilename );
		BASE_ACU( Connect );
		BASE_ACU( Dismiss );
	public:
		void reset( bso::bool__ P = true )
		{
			BASE_ACR( SwitchBackendType );
			BASE_ACR( DisplayEmbeddedBackendFilename );
			BASE_ACR( Connect );
			BASE_ACR( Dismiss );
		}
		qCVDTOR( fActionCallbacks );
		void Init( void )
		{
			BASE_ACI( SwitchBackendType );
			BASE_ACI( DisplayEmbeddedBackendFilename );
			BASE_ACI( Connect );
			BASE_ACI( Dismiss );
		}
	};

	void SetLayout( core::fSession &Session );
}

#endif