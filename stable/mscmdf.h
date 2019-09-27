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

// MuSiC MiDi File

#ifndef MSCMDF_INC_
# define MSCMDF_INC_

# define MSCMDF_NAME		"MSCMDF"

# if defined( E_DEBUG ) && !defined( MSCMDF_NODBG )
#  define MSCMDF_DBG
# endif

# include "err.h"
# include "flw.h"
# include "bso.h"

namespace mscmdf {

	//t The type of a a SMF type.
	typedef bso::u16__ sSMFType;

	//t Type of the delta time ticks..
	typedef bso::u16__ sDeltaTimeTicks;

	//t Type of the track-chunk amount.
	typedef bso::u16__ sTrackChunkAmount;

#define MSCMDF_TRACK_CHUNK_AMOUNT_MAX	BSO_U16_MAX

	//c A header chunk.
	struct header_chunk__ {
		sSMFType SMFType;
		sTrackChunkAmount TrackChunkAmount;
		sDeltaTimeTicks DeltaTimeTicks;
	};

	//f Put in 'HeaderChunk' the content of the header chunk.
	bso::bool__ GetHeaderChunk(
		flw::iflow__ &Flow,
		header_chunk__ &HeaderChunk,
		err::handling__ ErrHandling = err::h_Default );

	void PutHeaderChunk(
		sSMFType SMFType,
		sTrackChunkAmount TrackChunkAmount,
		sDeltaTimeTicks DeltaTimeTicks,
		flw::oflow__ &OFlow );

	inline void PutHeaderChunk(
		const header_chunk__ &HeaderChunk,
		flw::oflow__ &OFlow )
	{
		PutHeaderChunk( HeaderChunk.SMFType, HeaderChunk.TrackChunkAmount, HeaderChunk.DeltaTimeTicks, OFlow );
	}

	//t The type of the size of a track chunk.
	typedef bso::u32__ track_chunk_size__;

	//f Return the size of the track chunk
	track_chunk_size__  GetTrackChunkSize(
		flw::iflow__ &Flow,
		err::handling__ ErrHandling = err::h_Default );

	void PutTrackChunkHeader(
		track_chunk_size__ Size,
		flw::oflow__ &OFlow );
}

			  /********************************************/
				  /* do not modify anything belove this limit */
				  /*			  unless specified		   	  */
/******************************************************************************/

#endif
