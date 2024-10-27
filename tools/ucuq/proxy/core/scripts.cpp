/*
  Copyright (C) 2024 Claude SIMON (http://q37.info/contact/).

  This file is part of the 'UCUq' toolkit.

  'UCUq' is free software: you can redistribute it and/or modify it
  under the terms of the GNU Affero General Public License as published
  by the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  'UCUq' is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with 'UCUq'.  If not, see <http://www.gnu.org/licenses/>.
*/


#include "scripts.h"

#include "messages.h"

#include "sclm.h"

#include "strmrg.h"

using namespace scripts;

namespace {
  rgstry::wRegistry Scripts_;
  rgstry::sRow Root_;
  rgstry::rEntry LooseScript_("Script");
  rgstry::rEntry TaggedScript_(RGSTRY_TAGGING_ATTRIBUTE("name"), LooseScript_);
  rgstry::rEntry TaggedScriptDependencies_("Dependencies", TaggedScript_);
  mtx::rMutex Mutex_;

  void Load_(const fnm::rName &Name)
  {
    qRH;
    rgstry::rContext Context;
    lcl::wMeaning Meaning;
    qRB;
    tol::Init(Context, Scripts_);

    if ( (Root_ = rgstry::Fill(Name, xpp::rCriterions(fnm::rName()), "", Scripts_, Context)) == qNIL ) {
      Meaning.Init();
      rgstry::GetMeaning(Context, Meaning);
      sclm::ReportAndAbort(Meaning);
    }
    qRR;
    qRT;
    qRE;
  }

  namespace {
    namespace {
      bso::sBool GetScript_(
        const str::dString &Name,
        str::dString &Script)
      {
        return Scripts_.GetValue(rgstry::rTEntry(TaggedScript_, Name), Root_, Script);
      }

      namespace {
        void Split_(
          flw::rRFlow &Flow,
          str::dStrings &Splitted)
        {
        qRH
          str::wString Item;
        bso::sChar C = 0;
        qRB
          Item.Init();

        while ( !Flow.EndOfFlow() ) {
          C = Flow.Get();

          if ( C == ',' ) {
            if ( Item.Amount() ) {
              Splitted.Append(Item);
              Item.Init();
            }
          }
          else
            Item.Append(C);
        }

        if ( Item.Amount() )
          Splitted.Append(Item);
        qRR
        qRE
        qRT
        }
      }

      void Split_(
        const str::dString &Merged,
        str::dStrings &Splitted)
      {
        flx::sStringRFlow Flow;

        Flow.Init(Merged);

        Split_(Flow, Splitted);
      }
    }

    void GetScriptDependencies_(
      const str::dString &Name,
      str::dStrings &Dependencies)
    {
      str::wString RawDependency;

      RawDependency.Init();

      if ( Scripts_.GetValue(rgstry::rTEntry(TaggedScriptDependencies_, Name), Root_, RawDependency) ) {
        Split_(RawDependency, Dependencies);
      }
    }
  }

  bso::sBool GetScriptAndDependencies_(
    const str::dString &Name,
    str::dString &Script,
    str::wStrings &Dependencies)
  {
    GetScriptDependencies_(Name, Dependencies);

    return GetScript_(Name, Script);
  }

  namespace {
    void AddAbsentDependency_(
      const str::dString &Dependency,
      str::dStrings &Dependencies)
    {
      if ( str::Search( Dependency, Dependencies) == qNIL )
        Dependencies.Append(Dependency);
    }
  }

  void AddAbsentDependencies_(
    const str::dStrings &Source,
    str::dStrings &Target)
  {
    sdr::sRow Row = Source.First();

    while ( Row != qNIL ) {
      AddAbsentDependency_(Source(Row), Target);

      Row = Source.Next(Row);
    }
  }
}

void scripts::Load(const fnm::rName & Name)
{
qRH;
  mtx::rHandle Handle;
qRB;
  Handle.InitAndLock(Mutex_);

  Load_(Name);
qRR;
qRT;
qRE;
}

bso::sBool scripts::GetScript(
  const str::dString &Name,
  str::dString &Script,
  str::dStrings &Dependencies)
{
  bso::sBool Found = false;
qRH;
  str::wStrings RawDependencies;
qRB;
  RawDependencies.Init();

  if ( Found = GetScriptAndDependencies_(Name, Script, RawDependencies) )
    AddAbsentDependencies_(RawDependencies, Dependencies);
qRR;
qRT;
qRE;
  return Found;
}

qGCTOR(scripts) {
  Scripts_.Init();
  Root_ = qNIL;
  Mutex_ = mtx::Create();
}

qGDTOR(Scripts) {
  if ( Mutex_ != mtx::Undefined )
    mtx::Delete(Mutex_);

  Mutex_ = mtx::Undefined;
}
