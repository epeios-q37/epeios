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


#include "modules.h"

#include "messages.h"

#include "sclm.h"

#include "strmrg.h"

using namespace modules;

namespace {
  rgstry::wRegistry Modules_;
  rgstry::sRow Root_;
  rgstry::rEntry LooseModule_("Module");
  rgstry::rEntry TaggedModule_(RGSTRY_TAGGING_ATTRIBUTE("name"), LooseModule_);
  rgstry::rEntry TaggedModuleDependencies_("@Dependencies", TaggedModule_);
  mtx::rMutex Mutex_;

  void Load_(const fnm::rName &Name)
  {
    qRH;
    rgstry::rContext Context;
    lcl::wMeaning Meaning;
    qRB;
    tol::Init(Context, Modules_);

    if ( (Root_ = rgstry::Fill(Name, xpp::rCriterions(fnm::rName()), "", Modules_, Context)) == qNIL ) {
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

    bso::sBool GetModuleDependencies_(
      const str::dString &Name,
      str::dStrings &Dependencies)
    {
      bso::sBool Exists = false;
    qRH;
      str::wString RawDependency;
    qRB;
      RawDependency.Init();

      if ( Exists = Modules_.GetValue(rgstry::rTEntry(TaggedModuleDependencies_, Name), Root_, RawDependency) ) {
        Split_(RawDependency, Dependencies);
      }
    qRR;
    qRT;
    qRE;
     return Exists;
    }
  }

  namespace {
    void AddAbsentDependency_(
      const str::dString &Dependency,
      str::dStrings &Dependencies)
    {
      if ( str::Search(Dependency, Dependencies) == qNIL )
        Dependencies.Append(Dependency);
        Dependencies.Flush();
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

void modules::Load(const fnm::rName & Name)
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

bso::sBool modules::GetModuleContent(
  const str::dString &Name,
  str::dString &Content)
{
  return Modules_.GetValue(rgstry::rTEntry(TaggedModule_, Name), Root_, Content);
}

bso::sBool modules::GetModuleDependencies(
  const str::dString &Name,
  str::dStrings &Dependencies)
{
  bso::sBool Found = false;
qRH;
  str::wStrings RawDependencies;
qRB;
  RawDependencies.Init();

  if ( Found = GetModuleDependencies_(Name, RawDependencies) )
    AddAbsentDependencies_(RawDependencies, Dependencies);
qRR;
qRT;
qRE;
  return Found;
}

qGCTOR(modules) {
  Modules_.Init();
  Root_ = qNIL;
  Mutex_ = mtx::Create();
}

qGDTOR(modules) {
  if ( Mutex_ != mtx::Undefined )
    mtx::Delete(Mutex_);

  Mutex_ = mtx::Undefined;
}
