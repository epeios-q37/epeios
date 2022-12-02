/*
	Copyright (C) 2022 Claude SIMON (http://q37.info/contact/).

	This file is part of the 'mscfdraftq' tool.

    'mscfdraftq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'mscfdraftq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'mscfdraftq'.  If not, see <http://www.gnu.org/licenses/>.
*/


#include "tsqbndl.h"

using namespace tsqbndl;

# define UUID_  "c79626c0-860b-4425-9b64-a9f7b86d885a"

# if BSO_ENDIANESS_SEAL_SIZE == 4
#  define ENDIANESS_SEAL_TAG_ "XXXX"
# elif BSO_ENDIANESS_SEAL_SIZE == 8
#  define ENDIANESS_SEAL_TAG_ "XXXXXXXX"
# else
#  error
# endif // BSO_ENDIANESS_SEAL_SIZE

#define IDENTIFICATION_  "TasQ; UUID: " UUID_ "; Bitness: " CPE_L_BITNESS "; Endianess seal: " ENDIANESS_SEAL_TAG_
#define INFORMATION_ CPE_DESCRIPTION "; " __DATE__ " - " __TIME__

namespace {
  bso::sBool HeaderIsWritten_ = false;
  uys::rFOH<sizeof(IDENTIFICATION_) + sizeof(INFORMATION_) + sizeof(rXBundle::S_)> FH_;
  rXBundle XBundle_;
  mtx::rMutex Mutex_ = mtx::Undefined;
}

namespace {
  const char *BuildIdentification_(void)
  {
    static char Identification[] = IDENTIFICATION_;

    char *Tag = strstr(Identification, ENDIANESS_SEAL_TAG_);

    if ( Tag == NULL )
      qRGnr();

    strncpy(Tag, bso::EndianessSeal(), sizeof(ENDIANESS_SEAL_TAG_));

    return Identification;
  }
}

void tsqbndl::rXBundle::StoreStatics_(void)
{
  dBundle::Flush();
  FH_.Flush();

  if ( !HeaderIsWritten_ ) {
    FH_.Put((const sdr::sByte *)BuildIdentification_(), 0, sizeof( IDENTIFICATION_ ) );
    FH_.Put((const sdr::sByte *)INFORMATION_, sizeof( IDENTIFICATION_ ), sizeof( INFORMATION_ ) );
    HeaderIsWritten_ = true;
  }

  FH_.Put((const sdr::sByte *)&XBundle_.S_, sizeof(IDENTIFICATION_) + sizeof(INFORMATION_), sizeof(rXBundle::S_));
}

rXBundle &tsqbndl::Get(hGuard &Guard )
{
    Guard.InitAndLock(Mutex_);

    return XBundle_;
}

const rXBundle & tsqbndl::CGet(hGuard &Guard)
{
  return Get(Guard);
}

namespace {
  namespace _ {
    sTRow Add(
      const str::dString &Title,
      const str::dString &Description,
      sTRow Row)
    {
      return XBundle_.Add(Title, Description, Row);
    }
    sTRow Add(
      const char *Title,
      const char *Description,
      sTRow Row)
    {
      return Add(str::wString(Title), str::wString(Description), Row);
    }
  }

  void Populate_(
    dTasks &Tasks,
    sTRow Row)
  {
    _::Add("T1", "D1", Row);
    _::Add("T2", "D2", Row);
    _::Add("T3", "D3", Row);

    Row = Tasks.First(Row);

    Row = Tasks.Next(Row);

    _::Add("T2.1", "D2.1", Row);
    _::Add("T2.2", "# D2.2", Row);

    Row = Tasks.Next(Row);

    _::Add("T3.1", "D3.1", Row);
    _::Add("T3.2", "D3.2", Row);

    Row = Tasks.Previous(Row);
    Row = Tasks.First(Row);

    _::Add("T2.1.1", "D2.1.1", Row);
    _::Add("T2.1.2", "D2.1.2", Row);

  }
}

bso::sBool tsqbndl::Initialize(const fnm::rName &Filename)
{
  Mutex_ = mtx::Create();
  bso::sBool Exists = FH_.Init(Filename, uys::mReadWrite).Boolean();
  char Identification[sizeof( IDENTIFICATION_ )];

  XBundle_.plug(FH_);

  if ( Exists ) {
    FH_.Get(0, sizeof(Identification), (sdr::sByte *)Identification);

    if ( memcmp(Identification, BuildIdentification_(), sizeof(Identification) ) )
      qRFwk();

    FH_.Get(sizeof(IDENTIFICATION_) + sizeof(INFORMATION_), sizeof(XBundle_.S_), (sdr::sByte *)&XBundle_.S_);

    HeaderIsWritten_ = true;
  } else {
    XBundle_.Init();
  }

  return Exists;
}

void tsqbndl::Immortalize(void)
{
  XBundle_.Immortalize();
}
