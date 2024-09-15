/*
	Copyright (C) 2021 Claude SIMON (http://q37.info/contact/).

	This file is part of the 'McRq' tool.

    'McRq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'McRq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'McRq'.  If not, see <http://www.gnu.org/licenses/>.
*/


#ifndef SERVER_INC_
# define SERVER_INC_

# include "common.h"

# include "sdr.h"
# include "sck.h"

namespace server {
  qROW( Row );

  typedef common::rHandler rHandler_;

  class rHandler
  : private rHandler_
  {
  public:
    void reset(bso::sBool P = true)
    {
      rHandler_::reset(P);
    }
    qCDTOR(rHandler);
    void Init(void)
    {
      reset();

      rHandler_::Init();
    }
    void Process(void);
    sRow Get(void) const;
    sck::rRWDriver& Get(sRow Row);
  };
}

#endif
