unit utils;

interface

uses
  Forms, Windows, SysUtils, Classes, Registry, ShellAPI, IniFiles, ShlObj, ActiveX, ComObj, Variants, Math,
  Graphics, MemTableDataEh, Db, MemTableEh, ExtCtrls, KAZip, load;

const
  // разделы ini-файла дл€ хранени€ настроек
  APPDATAREGSEC = 'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders';
  DESKTOPREGKEY = 'Desktop';
  INI_SEC_WINDOW = 'WINDOW';
  INI_SEC_CONFIG = 'CONFIG';
  INI_SEC_LEAR_ORDER = 'LEAR_ORDER';
  INI_SEC_GAME_OPTS = 'GAME_OPTIONS';
  INI_SEC_PROFILES = 'PROFILES';
  INI_SEC_NETWORK = 'NETWORK';
  INI_SEC_SYSTEM = 'SYSTEM';
  RCFG_SEC_GROUP = 'GROUP';
  RCFG_SEC_FACE = 'FACE';
  REC_WORD_DELIM = '|';
  DEF_PROFILE = 'default';
  CYCLE_STEP_LIMIT = 1000;
  PARAMS_DELIM = #4;

  DATA_DIR = 'data\';
  RES_DIR = 'cache\';
  USER_DATA_DIR = 'userData\';  
  BG_DIR = RES_DIR + 'background\';
  FACE_DIR = RES_DIR + 'face\';
  BACK_DIR = RES_DIR + 'back\';
  DECK_DIR = RES_DIR + 'deck\';
  DECK_RUS_DIR = DECK_DIR + 'rus\';
  DECK_SOL_DIR = DECK_DIR + 'sol\';
  DECK_SLAV_DIR = DECK_DIR + 'slav\';
  DECK_SOUV_DIR = DECK_DIR + 'souv\';
  DECK_ENG_DIR = DECK_DIR + 'eng\';

  PARAM_FILE = 'config.ini';
  PLAYER_DATA_FILE = 'players.db';
  RES_FILE = 'resources.pak';
  RES_CONFIG_FILE = 'resources.cfg';
  SAVE_FILE = '%s.sav';
  SAVE_FILE_NET = '%s.nsv';
  LOG_FILE = 'poker.log';

type
  TEscHideAction = (eaNone, eaChangeCaption, eaMinimize, eaHideOnTray, eaClose);

function iif(Switch: boolean; iftrue: variant; iffalse: variant): variant;
function GetVersion(FileName: string): string;
procedure CreateLink(PathObj, PathLink, Desc, param: string);
function GetTempDir: string;
function ReadRegValueStr(RootKey: HKEY; Key, Param, default: string): string;

// ini files
function ReadIniValue(IniFile, Section, Param, default: string): string;
function WriteIniValue(IniFile, Section, Param, Value: string): boolean;
function DeleteIniKey(IniFile, Section, Param: string): boolean;
function DeleteIniSection(IniFile, Section: string): boolean;
function CopyIniSection(FileFrom, FileTo, Section: string; var ErrMessage: string): boolean;
procedure ReadIniSections(IniFile: string; SL: TStringList);
procedure DeleteIniSecStartWith(FileName, SecStartWith: string);
procedure RenameIniSection(FileName, OldName, NewName: string);
function IniKeyExists(FileName, Section, Key: string; Mode: integer): boolean;

function GetFileSize(FileName: string): Int64;
function GetDesktopDir: string;
function CopyFile(SourceFile, DestFile: string; var ErrMsg: string): boolean;
function DeleteDir(Directory: string; var ErrMsg: string): boolean;
function MoveDir(DirFrom, DirTo: string; CanReload, DelSrc: boolean; FLoad: TFLoad; var Err: string): boolean;
function ExtractWordEx(n: integer; s: string; WordDelims: TSysCharSet; IgnoreBlockChars: TSysCharSet): string;
function WordCountEx(s: string; WordDelims: TSysCharSet; IgnoreBlockChars: TSysCharSet): integer;
function GetFontStyle(style: string): TFontStyles;
function FontStyleAsString(fstyle: TFontStyles): string;
function GenRandString(genrule, vlength: integer): string;
function TextToString(Text: string; Decorator: string = ''; Delimiter: string = ','): string;
function GetFileIcon(FileName: string; var Icon: TIcon): boolean;
function DCS_(S: string): string;
function ECS_(S: string): string;
function MillisecondsToTimeStr(ms: Cardinal): string;
procedure AddToLog(FileName, str: string; gtime: TDateTime);
function UnpackArch(ArchName, DestPath: string; CanRewrite: boolean; FLoad: TFLoad; var Err: string): boolean;
function DosToAnsi(s: string): string;
function LoadResources(ResFile, DestDir: string; CanReload: boolean; FLoad: TFLoad; var Err: string): boolean;
function CountFiles(Folder: string): integer;
function CheckPortNumber(PortNumber: integer): string;

implementation

function iif(Switch: boolean; iftrue: variant; iffalse: variant): variant;
begin
  if Switch then
    result := iftrue
  else
    result := iffalse;
end;

function GetVersion(FileName: string): string;
var
  Info: Pointer;
  InfoSize: DWORD;
  FileInfo: PVSFixedFileInfo;
  FileInfoSize: DWORD;
  Tmp: DWORD;
  Major1, Major2, Minor1, Minor2: Integer;

begin
  result := '';
  Major1 := 0;
  Major2 := 0;
  Minor1 := 0;
  Minor2 := 0;

  InfoSize := GetFileVersionInfoSize(PChar(FileName), Tmp);

  if InfoSize = 0 then result := ''
  else
  begin
    GetMem(Info, InfoSize);
    try
      GetFileVersionInfo(PChar(FileName), 0, InfoSize, Info);
      VerQueryValue(Info, '\', Pointer(FileInfo), FileInfoSize);
      Major1 := FileInfo.dwFileVersionMS shr 16;
      Major2 := FileInfo.dwFileVersionMS and $FFFF;
      Minor1 := FileInfo.dwFileVersionLS shr 16;
      Minor2 := FileInfo.dwFileVersionLS and $FFFF;
    finally
      FreeMem(Info, FileInfoSize);
    end;
  end;

  result := IntToStr(Major1) + '.' + IntToStr(Major2) + '.' + IntToStr(Minor1) + '.' + IntToStr(Minor2);
end;

procedure CreateLink(PathObj, PathLink, Desc, param: string);
var
  IObject: IUnknown;
  SLink: IShellLink;
  PFile: IPersistFile;
  lFileName: WideString;

begin
  IObject := CreateComObject(CLSID_ShellLink);
  SLink := IObject as IShellLink;
  PFile := IObject as IPersistFile;
  with SLink do
  begin
    SetArguments(pchar(param));
    SetDescription(pchar(Desc));
    SetPath(pchar(PathObj));
    SetWorkingDirectory(pchar(ExtractFilePath(PathObj)));
  end;
  lFileName := PathLink + '\' + Desc + '.lnk';
  PFile.Save(pwChar(lFileName), false);
end;

function GetTempDir: string;
var
  buff: array [0..255] of char;

begin
  GetEnvironmentVariable(pchar('TEMP'), buff, SizeOf(buff));
  result := string(buff);
  if (Length(result) > 0) and (result[Length(result)] = '\') then Delete(result, Length(result), 1);
end;

function ReadRegValueStr(RootKey: HKEY; Key, Param, default: string): string;
var
  reg: TRegistry;

begin
  result := default;
  reg := TRegistry.Create(KEY_READ);
  reg.RootKey := RootKey;

  try
    if reg.OpenKey(Key, False) and reg.ValueExists(Param) then result := reg.ReadString(Param);
  except
  end;

  reg.CloseKey;
  reg.Free;
end;

function ReadIniValue(IniFile, Section, Param, default: string): string;
var
  f: TIniFile;

begin
  result := default;
  if not FileExists(IniFile) then exit;
  f := TIniFile.Create(IniFile);
  try
    result := f.ReadString(Section, Param, default);
  except
  end;
  f.Free;
end;

function WriteIniValue(IniFile, Section, Param, Value: string): boolean;
var
  f: TIniFile;

begin
  result := false;
  if not FileExists(IniFile) then exit;
  f := TIniFile.Create(IniFile);
  try
    f.WriteString(Section, Param, Value);
    result := true;
  except
  end;
  f.Free;
end;

function DeleteIniKey(IniFile, Section, Param: string): boolean;
var
  f: TIniFile;

begin
  result := false;
  if not FileExists(IniFile) then exit;
  f := TIniFile.Create(IniFile);
  try
    f.DeleteKey(Section, Param);
    result := true;
  except
  end;
  f.Free;
end;

function DeleteIniSection(IniFile, Section: string): boolean;
var
  f: TIniFile;

begin
  result := false;
  if not FileExists(IniFile) then exit;
  f := TIniFile.Create(IniFile);
  try
    f.EraseSection(Section);
    result := true;
  except
  end;
  f.Free;
end;

function CopyIniSection(FileFrom, FileTo, Section: string; var ErrMessage: string): boolean;
var
  fSrc, fDest: TIniFile;
  i: integer;
  sl: TStringList;

begin
  result := false;
  ErrMessage := '';
  fSrc := TIniFile.Create(FileFrom);
  fDest := TIniFile.Create(FileTo);
  sl := TStringList.Create;

  try
    fDest.EraseSection(Section);
    fSrc.ReadSection(Section, sl);
    for i := 0 to sl.Count - 1 do
      fDest.WriteString(Section, sl.Strings[i], fSrc.ReadString(Section, sl.Strings[i], ''));
    result := true;
  except
    on e: Exception do
      ErrMessage := e.Message;
  end;

  sl.Free;
  fSrc.Free;
  fDest.Free;
end;

procedure ReadIniSections(IniFile: string; SL: TStringList);
var
  f: TIniFile;

begin
  if not Assigned(SL) then exit;
  SL.Clear;
  f := TIniFile.Create(IniFile);
  try
    f.ReadSections(SL);
  except
  end;
  f.Free;
end;

procedure DeleteIniSecStartWith(FileName, SecStartWith: string);
var
  sl: TStringList;
  i: integer;

begin
  sl := TStringList.Create;
  try
    ReadIniSections(FileName, sl);
    for i := 0 to sl.Count - 1 do
      if (Pos(SecStartWith, sl.Strings[i]) = 1) then DeleteIniSection(FileName, sl.Strings[i]);
  finally
    sl.Free;
  end;
end;

procedure RenameIniSection(FileName, OldName, NewName: string);
var
  f: TIniFile;
  sl: TStringList;
  i: integer;
  
begin
  if not FileExists(FileName) then exit;

  sl := TStringList.Create;
  f := TIniFile.Create(FileName);
  try
    if f.SectionExists(OldName) then
    begin
      f.ReadSectionValues(OldName, sl);
      for i := 0 to sl.Count - 1 do
        f.WriteString(NewName, sl.Names[i], sl.Values[sl.Names[i]]);

      f.EraseSection(OldName);
    end;
  finally
    sl.Free;
    f.Free;
  end;
end;

function IniKeyExists(FileName, Section, Key: string; Mode: integer): boolean;
var
  i: integer;
  f: TIniFile;
  sl: TStringList;

begin
  // поиск не чувствителен к регистру
  // Mode: 0 - полное совпадение, 1 - по вхождению
  result := false;
  if not FileExists(FileName) then exit;

  sl := TStringList.Create;
  f := TIniFile.Create(FileName);
  try
    case Mode of
      0: result := f.ValueExists(Section, Key);
      1:
      begin
        f.ReadSection(Section, sl);
        for i := 0 to sl.Count - 1 do
        begin
          result := Pos(AnsiLowerCase(Key), AnsiLowerCase(sl.Strings[i])) > 0;
          if result then break;
        end;
      end;
    end;
  finally
    sl.Free;
    f.Free;
  end;
end;

function GetFileSize(FileName: string): Int64;
var
  sr: TSearchRec;
  si: integer;

begin
  result := 0;
  if not FileExists(FileName) then exit;

  si := FindFirst(FileName, faAnyFile, sr);
  if si = 0 then result := sr.Size;
  FindClose(sr);
end;

function GetDesktopDir: string;
begin
  result := ReadRegValueStr(HKEY_CURRENT_USER, APPDATAREGSEC, DESKTOPREGKEY, '');
end;

function CopyFile(SourceFile, DestFile: string; var ErrMsg: string): boolean;
var
  fsrc, fdest: TFileStream;

begin
  result := False;
  if not FileExists(SourceFile) then
  begin
    ErrMsg := 'Ќе найден файл источник "' + SourceFile + '"!';
    exit;
  end;
  if not DirectoryExists(ExtractFileDir(DestFile)) then
  begin
    ErrMsg := 'ѕапка назначени€ "' + ExtractFileDir(DestFile) + '" не существует!';
    exit;
  end;

  try
    try
      fsrc := TFileStream.Create(SourceFile, fmOpenRead);
      fdest := TFileStream.Create(DestFile, fmCreate);
      fsrc.Seek(0, soFromBeginning);
      fdest.CopyFrom(fsrc, fsrc.Size);
      result := fdest.Size = fsrc.Size;
    finally
      if Assigned(fsrc) then fsrc.Free;
      if Assigned(fdest) then fdest.Free;
    end;
  except
    on e: Exception do
    begin
      ErrMsg := e.Message;
      result := False;
    end;
  end;
end;

function DeleteDir(Directory: string; var ErrMsg: string): boolean;
var
  sr: TSearchRec;
  si: integer;

begin
  result := true;
  ErrMsg := '';
  if not DirectoryExists(Directory) then exit;

  si := FindFirst(Directory + '\*.*', faAnyFile, sr);
  while si = 0 do
  begin
    if (sr.Name = '.') or (sr.Name = '..') then
    begin
      si := FindNext(sr);
      continue;
    end;
    if (sr.Attr and faDirectory) = faDirectory then
    begin
      result := DeleteDir(Directory + '\' + sr.Name, ErrMsg);
      if not result then break;
    end else
    begin
      SetFileAttributes(pchar(Directory + '\' + sr.Name), faArchive);
      result := DeleteFile(Directory + '\' + sr.Name);
      if not result then
      begin
        ErrMsg := SysErrorMessage(GetLastError);
        break;
      end;
    end;
    si := FindNext(sr);
  end;
  FindClose(sr);

  if not result then exit;
  result := RemoveDir(Directory);
  if not result then
    ErrMsg := SysErrorMessage(GetLastError);
end;

function MoveDir(DirFrom, DirTo: string; CanReload, DelSrc: boolean; FLoad: TFLoad; var Err: string): boolean;
var
  sr: TSearchRec;
  si: integer;

begin
  result := true;
  Err := '';
  if not ForceDirectories(DirTo) then exit;
  if not DirectoryExists(DirFrom) then exit;

  si := FindFirst(DirFrom + '\*.*', faAnyFile, sr);
  while si = 0 do
  begin
    if (sr.Name = '.') or (sr.Name = '..') then
    begin
      si := FindNext(sr);
      continue;
    end;
    if (sr.Attr and faDirectory) = faDirectory then
    begin
      result := MoveDir(DirFrom + '\' + sr.Name, DirTo + '\' + sr.Name, CanReload, DelSrc, FLoad, Err);
      if not result then break;
    end else
    begin
      if Assigned(FLoad) then FLoad.lbFile.Caption := sr.Name;
      Application.ProcessMessages;

      if (FileExists(DirTo + '\' + sr.Name) and CanReload) or (not FileExists(DirTo + '\' + sr.Name)) then
      begin
        result := CopyFile(DirFrom + '\' + sr.Name, DirTo + '\' + sr.Name, Err);
        if not result then break;
      end;

      if DelSrc then
      begin
        SetFileAttributes(pchar(DirFrom + '\' + sr.Name), faArchive);
        result := DeleteFile(DirFrom + '\' + sr.Name);
        if not result then
        begin
          Err := SysErrorMessage(GetLastError);
          break;
        end;
      end;
    end;
    si := FindNext(sr);
  end;
  FindClose(sr);

  if not result then exit;
  if DelSrc then result := DeleteDir(DirFrom, Err);
end;

function ExtractWordEx(n: integer; s: string; WordDelims: TSysCharSet; IgnoreBlockChars: TSysCharSet): string;
var
  CurrBlChar: char;
  iblock: boolean;
  i: integer;
  wn: integer;

begin
  result := '';
  iblock := false;
  CurrBlChar := #0;
  wn := 1;

  for i := 1 to Length(s) do
  begin
    if (iblock) then
    begin
      if (s[i] = CurrBlChar) then
      begin
        iblock := false;
        CurrBlChar := #0;
      end;
      if (wn = n) then result := result + s[i];
      continue;
    end;
    if (s[i] in IgnoreBlockChars) then
    begin
      iblock := true;
      CurrBlChar := s[i];
      if (wn = n) then result := result + s[i];
      continue;
    end;
    if (s[i] in WordDelims) then
    begin
      Inc(wn);
      if (wn > n) then exit;
    end else
      if (wn = n) then result := result + s[i];
  end;
end;

function WordCountEx(s: string; WordDelims: TSysCharSet; IgnoreBlockChars: TSysCharSet): integer;
var
  CurrBlChar: char;
  iblock: boolean;
  i: integer;

begin
  if (s = '') then result := 0
  else result := 1;
  iblock := false;
  CurrBlChar := #0;

  for i := 1 to Length(s) do
  begin
    if (iblock) then
    begin
      if (s[i] = CurrBlChar) then
      begin
        iblock := false;
        CurrBlChar := #0;
      end;
      continue;
    end;
    if (s[i] in IgnoreBlockChars) then
    begin
      iblock := true;
      CurrBlChar := s[i];
      continue;
    end;
    if ((s[i] in WordDelims) and (i < Length(s))) then Inc(result);
  end;
end;

function GetFontStyle(style: string): TFontStyles;
var
  i: integer;
  s: string;

begin
  result := [];
  for i := 0 to WordCountEx(style, [','], []) do
  begin
    s := LowerCase(Trim(ExtractWordEx(i, style, [','], [])));
    if (s = 'fsbold') then result := result + [fsBold];
    if (s = 'fsitalic') then result := result + [fsItalic];
    if (s = 'fsunderline') then result := result + [fsUnderline];
    if (s = 'fsstrikeout') then result := result + [fsStrikeOut];
  end;
end;

function FontStyleAsString(fstyle: TFontStyles): string;
begin
  result := '';
  if (fsBold in fstyle) then
    if (result = '') then result := 'fsBold'
    else result := result + ',fsBold';
  if (fsItalic in fstyle) then
    if (result = '') then result := 'fsItalic'
    else result := result + ',fsItalic';
  if (fsUnderline in fstyle) then
    if (result = '') then result := 'fsUnderline'
    else result := result + ',fsUnderline';
  if (fsStrikeOut in fstyle) then
    if (result = '') then result := 'fsStrikeOut'
    else result := result + ',fsStrikeOut';
end;

function GenRandString(genrule, vlength: integer): string;
var
  i: integer;
  c: byte;
  symbs: set of byte;

begin
  result := '';
  symbs := [];
  if genrule > 6 then genrule := 6;

  case genrule of
    0: symbs := symbs + [48..57];                           //цифры 0..9
    1: symbs := symbs + [65..90, 97..122];                  //буквы A..Z, a..z
    2: symbs := symbs + [65..90];                           //буквы A..Z
    3: symbs := symbs + [97..122];                          //буквы a..z
    4: symbs := symbs + [48..57, 65..90];                   //цифры + буквы A..Z
    5: symbs := symbs + [48..57, 97..122];                  //цифры + буквы a..z
    6: symbs := symbs + [48..57, 65..90, 97..122];          //цифры + буквы A..Z, a..z
  end;
  if symbs = [] then exit;

  Randomize;
  for i := 1 to vlength do
  begin
    c := Random(123);
    while not (c in symbs) do c := Random(123);
    result := result + chr(c);
  end;
end;

function TextToString(Text: string; Decorator: string; Delimiter: string): string;
var
  i: integer;
  f: boolean;

begin
  result := StringReplace(Text, #13#10, Delimiter, [rfReplaceAll]);
  if (result <> '') then
  begin
    if Pos(Delimiter, result) = 1 then
      result := StringReplace(result, Delimiter, '', []);

    f := false;
    for i := 1 to Length(Delimiter) do
      if result[Length(result) - Length(Delimiter) + i] <> Delimiter[i] then
      begin
        break;
        f := false;
      end else
        f := true;

    if f then Delete(result, Length(result) - Length(Delimiter) + 1, Length(Delimiter));

    if Decorator <> '' then
      result := Decorator + StringReplace(result, Delimiter, Decorator + Delimiter + Decorator, [rfReplaceAll]) + Decorator;
  end;
end;

function GetFileIcon(FileName: string; var Icon: TIcon): boolean;
begin
  result := false;
  if (not FileExists(FileName)) or (not Assigned(Icon)) then exit;
  try
    Icon.Handle := ExtractIcon(HInstance, pchar(FileName), 0);
    result := true;
  except
  end;
end;

function DCS_(S: string): string;
var
  i, l, n: integer;

begin
  Result := '';
  l := Length(S);
  n := l - (l div 2);
  for i := 1 to n do
  begin
    Result := Chr(Ord(S[i]) + 1) + Result;
    if i + n <= l then Result := Chr(Ord(S[i + n]) + 2) + Result;
  end;
end;

function ECS_(S: string): string;
var
  i, l: integer;

begin
  Result := '';
  l := Length(S);
  for i := 0 to l - 1 do
    if i mod 2 = 0 then Result := Result + Chr(Ord(S[l - i]) - 1);
  for i := 0 to l - 1 do
    if i mod 2 <> 0 then Result := Result + Chr(Ord(S[l - i]) - 2);
end;

function MillisecondsToTimeStr(ms: Cardinal): string;
var
  hh, mm, ss, sss: integer;

begin
  sss := ms div 1000;
  ss := (sss mod 3600) mod 60;
  mm := (sss mod 3600) div 60;
  hh := sss div 3600;
  result := Format('%2.2d:%2.2d:%2.2d', [hh, mm, ss]);
end;

procedure AddToLog(FileName, str: string; gtime: TDateTime);
var
  fs: TFileStream;
  ss: TStringStream;

begin
  //формат лога:
  //04.04.2010  10:15:00  сообщение

  if gtime = 0 then
    str := DateToStr(Now) + '  ' + TimeToStr(Now) + '  ' + str + #13#10
  else
    str := TimeToStr(gtime) + '  ' + str + #13#10;

  try
    try
      if FileExists(FileName) then
      begin
        fs := TFileStream.Create(FileName, fmOpenWrite);
        fs.Seek(fs.Size, soFromBeginning);
      end else
        fs := TFileStream.Create(FileName, fmCreate);

      ss := TStringStream.Create(str);
      ss.WriteString(str);
      ss.Seek(0, soFromBeginning);
      fs.CopyFrom(ss, ss.Size);
    finally
      fs.Free;
      ss.Free;
    end;
  except
  end;
end;

function UnpackArch(ArchName, DestPath: string; CanRewrite: boolean; FLoad: TFLoad; var Err: string): boolean;
var
  zip: TKAZip;
  i: integer;
  f: TFileStream;
  Dest: string;

begin
  try
    Err := '';    
    zip := TKAZip.Create(nil);
    zip.Open(ArchName);
    try
      if not zip.IsZipFile then
        raise Exception.Create('Ќеверный формат. ‘айл не €вл€етс€ zip-архивом.');

      for i := 0 to zip.Entries.Count - 1 do
      begin
        Dest := DestPath + DosToAnsi(zip.Entries.Items[i].FileName);

        if Assigned(FLoad) then
        begin
          FLoad.lbFile.Caption := DosToAnsi(zip.Entries.Items[i].FileName);
          FLoad.lbProgress.Caption := ' эширование ресурсов: ' + IntToStr(Round(((i + 1) / zip.Entries.Count) * 100)) + '% (' +
            IntToStr(i + 1) + ' / ' + IntToStr(zip.Entries.Count) + ')';
          Application.ProcessMessages;
        end;

        if zip.Entries.Items[i].IsFolder then
        begin
          result := ForceDirectories(Dest);
          if not result then raise Exception.Create(SysErrorMessage(GetLastError));
        end else
        begin
          if FileExists(Dest) then
          begin
            if not CanRewrite then continue;
            SetFileAttributes(pchar(Dest), faArchive);
            f := TFileStream.Create(Dest, fmOpenWrite);
          end else
            f := TFileStream.Create(Dest, fmCreate);

          zip.ExtractToStream(zip.Entries.Items[i], f);
          f.Free;
        end;
      end;
    finally
      zip.Close;
      zip.Free;
    end;
    result := true;
  except
    on e: Exception do
    begin
      Err := e.Message;
      result := false;
    end;
  end;
end;

function DosToAnsi(s: string): string;
begin
  SetLength(result, Length(s));
  OemToAnsi(pchar(s), pchar(result));
end;

function LoadResources(ResFile, DestDir: string; CanReload: boolean; FLoad: TFLoad; var Err: string): boolean;
begin
  Err := '';
  result := true;

  if CanReload then
  begin
    result := DeleteDir(DestDir, Err);
    if not result then exit;
  end;

  result := ForceDirectories(DestDir);
  if not result then
  begin
    Err := SysErrorMessage(GetLastError);
    exit;
  end;

  result := UnpackArch(ResFile, DestDir, CanReload, FLoad, Err);
end;

function CountFiles(Folder: string): integer;
var
  sr: TSearchRec;
  si: integer;

begin
  result := 0;
  if not DirectoryExists(Folder) then exit;

  si := FindFirst(Folder + '\*.*', faAnyFile, sr);
  while si = 0 do
  begin
    if (sr.Name = '.') or (sr.Name = '..') then
    begin
      si := FindNext(sr);
      continue;
    end;

    if (sr.Attr and faDirectory) = faDirectory then
      result := result + CountFiles(Folder + '\' + sr.Name)
    else Inc(result);
    si := FindNext(sr);
  end;
  FindClose(sr);
end;

function CheckPortNumber(PortNumber: integer): string;
begin
  case PortNumber of
    1030..1032,49151: result := '–езерв';
    1024: result := 'KDM (K Display Manager)';
    1025: result := 'ѕорт прослушивани€ RFS, NFS, IIS';
    1026: result := 'CAP'#13#10'Microsoft DCOM';
    1027: result := '6A44 (IPv6 Behind NAT44 CPEs)';
    1029: result := 'SOLID-MUX'#13#10'Microsoft DCOM';
    1033: result := 'NETINFO-LOCAL';
    1034: result := 'ACTIVESYNC';
    1035: result := 'MXXRLOGIN';
    1036: result := 'NSSTP (Nebula Secure Segment Transfer Protocol)';
    1037: result := 'AMS';
    1038: result := 'MTQP (Message Tracking Query Protocol)';
    1039: result := 'SBL (Streamlined Blackhole)';
    1040: result := 'NETARX';
    1041: result := 'DANF-AK2';
    1042: result := 'AFROG Subnet Roaming';
    1043: result := 'BOINC-CLIENT';
    1044: result := 'DCUTILITY (Dev Consortium Utility)';
    1045: result := 'FPITP (Fingerprint Image Transfer Protocol)';
    1046: result := 'WFREMOTERTM (WebFilter Remote Monitor)';
    1047: result := 'NEOD1 (Sun''s NEO Object Request Broker)';
    1048: result := 'NEOD2 (Sun''s NEO Object Request Broker)';
    1049: result := 'TD-POSTMAN (Tobit David Postman VPMN)';
    1050: result := 'CBA (CORBA Management Agent)';
    1051: result := 'OPTIMA-VNET';
    1052: result := 'DDT (Dynamic DNS Tools)';
    1053: result := 'REMOTE-AS (Remote Assistant)';
    1054: result := 'BRVREAD';
    1055: result := 'ANSYSLMD (ANSYS License Manager)';
    1056: result := 'VFO';
    1057: result := 'STARTRON';
    1058: result := 'NIM (IBM AIX Network Installation Manager)';
    1059: result := 'NIMREG (IBM AIX Network Installation Manager Registration)';
    1060: result := 'POLESTAR';
    1061: result := 'KIOSK';
    1062: result := 'Veracity';
    1063: result := 'KyoceraNetDev';
    1064: result := 'JSTEL';
    1065: result := 'SYSCOMLAN';
    1066: result := 'FPO-FNS';
    1067: result := 'INSTL-BOOTS (Installation Bootstrap Protocol Server)';
    1068: result := 'INSTL-BOOTC (Installation Bootstrap Protocol Client)';
    1069: result := 'COGNEX-INSIGHT';
    1070: result := 'GMRUpdateSERV';
    1071: result := 'BSQUARE-VOIP';
    1072: result := 'CARDAX';
    1073: result := 'BridgeControl';
    1074: result := 'WARMSPOTMGMT (Warmspot Management Protocol)';
    1075: result := 'RDRMSHC';
    1076: result := 'DAB-STI-C';
    1077: result := 'IMGames';
    1078: result := 'Avocent-Proxy';
    1079: result := 'ASPROVATalk';
    1080: result := 'SOCKS';
    1081: result := 'PVUNIWIEN';
    1082: result := 'AMT-ESD-PROT';
    1083: result := 'ANSOFT-LM-1 (Anasoft License Manager)';
    1084: result := 'ANSOFT-LM-2 (Anasoft License Manager)';
    1085: result := 'WebObjects';
    1086: result := 'cplscrambler-lg (CPL Scrambler Logging)';
    1087: result := 'cplscrambler-in (CPL Scrambler Internal)';
    1088: result := 'cplscrambler-al (CPL Scrambler Alarm Log)';
    1089: result := 'ff-annunc (FF Annunciation)';
    1090: result := 'ff-fms (FF Fieldbus Message Specification)';
    1091: result := 'ff-sm (FF System Management)';
    1092: result := 'obrpd (Open Business Reporting Protocol)';
    1093: result := 'PROOFD';
    1094: result := 'ROOTD';
    1095: result := 'NICELink';
    1096: result := 'cnrprotocol (Common Name Resolution Protocol)';
    1097: result := 'sunclustermgr (Sun Cluster Manager)';
    1098: result := 'rmiactivation (RMI Activation)';
    1099: result := 'rmiregistry (RMI Registry)';
    1100: result := 'MCTP';
    1101: result := 'PT2-DISCOVER';
    1102: result := 'ADOBESERVER-1';
    1103: result := 'ADOBESERVER-2';
    1104: result := 'XRL';
    1105: result := 'FTRANHC';
    1106: result := 'ISOIPSIGPORT-1';
    1107: result := 'ISOIPSIGPORT-2';
    1108: result := 'ratio-adp';
    1109: result := 'KPOP (Kerberized Post Office Protocol)';
    1110: result := 'WEBADMSTART, Start web admin server';
    1111: result := 'LMSocialServer';
    1112: result := 'ICP (Intelligent Communication Protocol)';
    1113: result := 'LTP-DEEPSPACE (Licklider Transmission Protocol)';
    1114: result := 'Mini-SQL';
    1115: result := 'ARDUS-TRNS (ARDUS Transfer)';
    1116: result := 'ARDUS-CNTL (ARDUS Control)';
    1117: result := 'ARDUS-MTRNS (ARDUS Multicast Transfer)';
    1118: result := 'SACRED (Securely Available Credentials Protocol)';
    1119: result := 'BNETGAME (Battle.net Chat/Game Protocol)';
    1120: result := 'BNETFILE (Battle.net File Transfer Protocol)';
    1121: result := 'RMPP';
    1122: result := 'availant-mgr';
    1123: result := 'Murray';
    1124: result := 'hpvmmcontrol (HP VMM Control)';
    1125: result := 'hpvmmagent (HP VMM Agent)';
    1126: result := 'hpvmmdata (HP VMM Data)';
    1127: result := 'KWDB-COMMN (KWDB Remote Communication)';
    1128: result := 'SAPHostCtrl (SAPHostControl over SOAP/HTTP)';
    1129: result := 'SAPHostCtrlS (SAPHostControl over SOAP/HTTPS)';
    1130: result := 'CASP (CAC App Service Protocol)';
    1131: result := 'CASPSSL (CAC App Service Protocol с шифрованием по SSL)';
    1132: result := 'KVM-VIA-IP';
    1133: result := 'DFN (Data Flow Network)';
    1134: result := 'APLX (MicroAPL APLX)';
    1135: result := 'OmniVision Communication Service';
    1136: result := 'HHB-Gateway';
    1137: result := 'TRIM Workgroup Service';
    1138: result := 'encrypted-admin';
    1139: result := 'EVM (Enterprise Virtual Manager)';
    1140: result := 'AutoNOC Network Operations protocol';
    1141: result := 'MXOMSS, User Message Service';
    1142: result := 'EDTOOLS, User Discovery Service';
    1143: result := 'IMYX (Infomatryx Exchange)';
    1144: result := 'FUSCRIPT (Fusion Script)';
    1145: result := 'X9-ICUE (X9 iCue Show Control)';
    1146: result := 'AUDIT-TRANSFER';
    1147: result := 'CAPIoverLAN';
    1148: result := 'ELFIQ-REPL (Elfiq Replication Service)';
    1149: result := 'BVTSONAR (BlueView Sonar Service)';
    1150: result := 'BLAZE (Blaze File Server)';
    1151: result := 'UNIZENSUS (Unizensus Login Server)';
    1152: result := 'WINPOPLANMESS (Winpopup LAN Messenger)';
    1153: result := 'C1222-ACSE (ANSI C12.22 Port)';
    1154: result := 'RESACOMMUNITY';
    1155: result := 'NFA (Network File Access)';
    1156: result := 'iasControl-OMS (Oracle)';
    1157: result := 'iasControl (Oracle)';
    1158: result := 'dbControl-OMS (Oracle)';
    1159: result := 'Oracle-OMS';
    1160: result := 'OLSV, DB Lite Multi-User Server';
    1161: result := 'HEALTH-POLLING';
    1162: result := 'HEALTH-TRAP';
    1163: result := 'SDDP (SmartDialer Data Protocol)';
    1164: result := 'QSM-Proxy';
    1165: result := 'QSM-GUI';
    1166: result := 'QSM-REMOTE';
    1167: result := 'Cisco-IPSLA (Cisco IOS IP Service Level Agreements control protocol)';
    1168: result := 'VCHAT Conference Service';
    1169: result := 'TRIPWIRE';
    1170: result := 'ATC-LM (AT+C License Manager)';
    1171: result := 'ATC-APPSERVER (AT+C FmiApplicationServer)';
    1172: result := 'DNAP';
    1173: result := 'D-CINEMA-RRP (D-Cinema Request-Response)';
    1174: result := 'FNET-REMOTE-UI (FlashNet Remote Admin)';
    1175: result := 'DOSSIER';
    1176: result := 'INDIGO-SERVER (Indigo Home Automation Server)';
    1177: result := 'DKMessenger';
    1178: result := 'SGI-STORMAN (SGI Storage Manager)';
    1179: result := 'B2N (Backup To Neighbor)';
    1180: result := 'MC-CLIENT (Millicent Client Proxy)';
    1181: result := '3COMNETMAN (3Com Net Management)';
    1182: result := 'AcceleNet (команды)';
    1183: result := 'LLSURFUP-HTTP';
    1184: result := 'LLSURFUP-HTTPS';
    1185: result := 'CATCHPOLE';
    1186: result := 'MySQL-Cluster';
    1187: result := 'Alias Service';
    1188: result := 'HP-WebAdmin'#13#10'SKYs Corporation';
    1189: result := 'UNET';
    1190: result := 'COMMLINX-AVL';
    1191: result := 'GPFS (General Parallel File System)';
    1192: result := 'CAIDS-SENSOR';
    1193: result := 'FIVEACROSS';
    1194: result := 'OpenVPN';
    1195: result := 'RSF-1 clustering';
    1196: result := 'NETMAGIC (Network Magic)';
    1197: result := 'CARRIUS-RSHELL (Carrius Remote Access)';
    1198: result := 'CAJO-DISCOVERY';
    1199: result := 'DMIDI';
    1200: result := 'SCOL (используетс€ сервером Cryo Interactive)';
    1214: result := 'Kazaa';
    1220: result := 'QuickTime Streaming Server administration';
    1223: result := 'TGP, TrulyGlobal Protocol, also known as ЂThe Gur Protocolї (named for Gur Kimchi of TrulyGlobal)';
    1241: result := 'Nessus Security Scanner';
    1248: result := 'NSClient/NSClient++/NC_Net (Nagios)';
    1270: result := 'Microsoft System Center Operations Manager (SCOM) agent';
    1311: result := 'Dell Open Manage Https';
    1313: result := 'Xbiim (Canvii server)';
    1337: result := 'WASTE Encrypted File Sharing Program';
    1352: result := 'IBM Lotus Notes/Domino RPC protocol';
    1387: result := 'cadsi-lm (formerly Computer Aided Design Software, Inc. (CADSI)) LM';
    1414: result := 'IBM WebSphere MQ (formerly known as MQSeries)';
    1431: result := 'Reverse Gossip Transport Protocol (RGTP)';
    1433: result := 'Microsoft SQL Server†Ч Server';
    1434: result := 'Microsoft SQL Server†Ч Monitor';
    1494: result := 'Citrix XenApp Independent Computing Architecture (ICA) thin client protocol';
    1512: result := 'Microsoft Windows Internet Name Service (WINS)';
    1521: result := 'nCube License Manager'#13#10'Oracle database default listener';
    1524: result := 'ingreslock, ingres';
    1526: result := 'Oracle database common alternative for listener';
    1533: result := 'IBM Sametime IMЧVirtual Places Chat';
    1547: result := 'Laplink';
    1550: result := 'Gadu-Gadu (direct client-to-client)';
    1645: result := 'radius, RADIUS authentication protocol (default for Cisco and Juniper Networks RADIUS servers)';
    1646: result := 'radacct, RADIUS accounting protocol (default for Cisco and Juniper Networks RADIUS servers)';
    1627: result := 'iSketch';
    1677: result := 'Novell GroupWise clients in client/server access mode';
    1716: result := 'America''s Army Massively multiplayer online role-playing game (MMORPG)';
    1720: result := 'h323hostcall (H323 VoIP calls)';
    1723: result := 'Microsoft Point-to-Point Tunneling Protocol (PPTP)';
    1755: result := 'Microsoft Media Services (MMS, ms-streaming)';
    1761: result := 'cft-0'#13#10'Novell Zenworks Remote Control utility';
    1762..1768: result := 'cft-1 to cft-7';
    1812: result := 'radius, RADIUS authentication protocol';
    1813: result := 'radacct, RADIUS accounting protocol';
    1863: result := 'MSNP (Microsoft Notification Protocol)';
    1935: result := 'Adobe Macromedia Flash Real Time Messaging Protocol (RTMP) Ђplainї protocol';
    1947: result := 'HASP SRM –абота и с сетевым, и с локальным ключами HASP происходит через локальный демон или службу';
    1970: result := 'Danware NetOp Remote Control';
    1971: result := 'Danware NetOp School';
    1972: result := 'InterSystems Cach?';
    1984: result := 'Big BrotherЧnetwork monitoring tool';
    1988: result := 'SKYs Corporation';
    1994: result := 'Cisco STUN-SDLC (Serial TunnelingЧSynchronous Data Link Control) protocol';
    1998: result := 'Cisco X.25 over TCP (XOT) service';
    2000: result := 'Cisco SCCP (Skinny)'#13#10'Phantom Transport Layer';
    2002: result := 'Secure Access Control Server (ACS) for Windows';
    2030: result := 'Oracle Services for Microsoft Transaction Server';
    2031: result := 'mobrien-chatЧobsolete';
    2041: result := 'Mail.ru јгент communication protocol';
    2042: result := 'Mail.ru јгент communication protocol';
    2053: result := 'lot105-ds-upd Lot105 DSuper Updates'#13#10'knetd Kerberos de-multiplexor';
    2073: result := 'DataReel Database';
    2074: result := 'Vertel VMF SA (то есть App. SpeakFreely)';
    2080: result := 'Autodesk license daemon';
    2082: result := 'Infowave Mobility Server'#13#10'CPanel default';
    2083: result := 'Secure Radius Service (radsec)'#13#10'CPanel default SSL';
    2086: result := 'GNUnet'#13#10'WebHost Manager default';
    2087: result := 'WebHost Manager default SSL';
    2095: result := 'CPanel default Web mail';
    2096: result := 'CPanel default SSL Web mail';
    2102: result := 'zephyr-srv Project Athena Zephyr Notification Service server';
    2103: result := 'zephyr-clt Project Athena Zephyr Notification Service serv-hm connection';
    2104: result := 'zephyr-hm Project Athena Zephyr Notification Service hostmanager';
    2105: result := 'eklogin Kerberos encrypted remote login (rlogin)'#13#10'zephyr-hm-srv Project Athena Zephyr Notification Service hm-serv connection';
    2106: result := 'Lineage2 AUTH port (default)';
    2161: result := 'APC Agent';
    2181: result := 'EForward-document transport system';
    2219: result := 'NetIQ NCAP Protocol';
    2220: result := 'NetIQ End2End';
    2222: result := 'DirectAdmin default';
    2301: result := 'HP System Management Redirect to port 2381';
    2369: result := 'Default for BMC Software CONTROL-M/ServerЧConfiguration Agent';
    2370: result := 'Default for BMC Software CONTROL-M/ServerЧto allow the CONTROL-M/Enterprise Manager to connect to the CONTROL-M/Server';
    2381: result := 'HP Insight Manager default for Web server';
    2404: result := 'IEC 60870-5-104';
    2428: result := 'Cisco MGCP';
    2447: result := 'ovwdb†Ч OpenView Network Node Manager (NNM) daemon';
    2483: result := 'Oracle database listening for unsecure client connections to the listener';
    2484: result := 'Oracle database listening for SSL client connections to the listener';
    2546: result := 'Vytal VaultЧData Protection Services';
    2593: result := 'RunUO†Ч Ultima Online server';
    2594: result := 'Old Paradise†Ч Ultima Online server';
    2598: result := 'new ICAЧwhen Session Reliability is enabled';
    2612: result := 'QPasa from MQSoftware';
    2710: result := 'XBT Bittorrent Tracker'#13#10'Knuddels.de';
    2735: result := 'NetIQ Monitor Console';
    2809: result := 'corbaloc: iiop URL, per the CORBA 3.0.3 specification'#13#10'IBM WebSphere Application Server (WAS) Bootstrap/rmi default';
    2948: result := 'WAP-push Multimedia Messaging Service (MMS)';
    2949: result := 'WAP-pushsecure Multimedia Messaging Service (MMS)';
    2967: result := 'Symantec AntiVirus Corporate Edition';
    3000: result := 'Miralix License server';
    3001: result := 'Miralix Phone Monitor';
    3002: result := 'Miralix CSTA';
    3003: result := 'Miralix GreenBox API';
    3004: result := 'Miralix InfoLink';
    3006: result := 'Miralix SMS Client Connector';
    3007: result := 'Miralix OM Server';
    3025: result := 'netpd.org';
    3030: result := 'NetPanzer';
    3034: result := 'Plain Manager Port BlueCoat ProxySG services';
    3036: result := 'Secure Manager Port BlueCoat ProxySG services';
    3050: result := 'gds_db (—”Ѕƒ Interbase/Firebird)';
    3074: result := 'Xbox Live';
    3128: result := 'HTTP used by Web caches and the default for the Squid cache & Kerio Winroute Firewall';
    3260: result := 'iSCSI target';
    3268: result := 'msft-gc, Microsoft Global Catalog (LDAP service which contains data from Active Directory forests)';
    3269: result := 'msft-gc-ssl, Microsoft Global Catalog over SSL (similar to port 3268, LDAP over SSL)';
    3283: result := 'Apple Remote Desktop reporting (officially Net Assistant, referring to an earlier product)';
    3300: result := 'TripleA game server';
    3305: result := 'odette-ftp, Odette File Transfer Protocol (OFTP)';
    3306: result := '—истема управлени€ базами данных MySQL'#13#10'—истема управлени€ базами данных MS SQL';
    3307: result := '—истема управлени€ базами данных MySQL';
    3333: result := 'Network Caller ID server';
    3386: result := 'GTP'' 3GPP GSM/UMTS CDR logging protocol';
    3389: result := 'Microsoft Terminal Server (RDP) ќфициально зарегистрировано как Windows Based Terminal (WBT)';
    3396: result := 'Novell NDPS Printer Agent';
    3455: result := '[RSVP] Reservation Protocol';
    3632: result := 'distributed compiler';
    3689: result := 'Digital Audio Access Protocol (DAAP)Чused by AppleТs iTunes and AirPort Express';
    3690: result := 'Subversion version control system';
    3702: result := 'Web Services Dynamic Discovery (WS-Discovery)';
    3724: result := 'World of Warcraft Online gaming MMORPG';
    3784: result := 'Ventrilo VoIP program used by Ventrilo';
    3868: result := 'DIAMETER base protocol';
    3872: result := 'Oracle Management Remote Agent';
    3899: result := 'RAdmin';
    3900: result := 'udt_os, IBM UniData UDT OS';
    3945: result := 'EMCADS service, a Giritech product used by G/On';
    3949: result := 'OER communications†Ч Optimized Edge Routing';
    4000: result := 'Diablo II game';
    4007: result := 'PrintBuzzer printer monitoring socket server';
    4080: result := 'Kerio Control Administration';
    4081: result := 'Secured Kerio Control Administration';
    4089: result := 'OpenCORE Remote Control Service';
    4090: result := 'Kerio VPN';
    4093: result := 'PxPlus Client server interface ProvideX';
    4096: result := 'Bridge-Relay Element ASCOM';
    4100: result := 'WatchGuard Authentication AppletЧdefault';
    4111: result := 'Xgrid'#13#10'Microsoft Office SharePoint Portal Server administration';
    4125: result := 'Microsoft Remote Web Workplace administration';
    4226: result := 'Aleph One (игра)';
    4224: result := 'Cisco CDP Cisco discovery Protocol';
    4444: result := 'I2P ѕо умолчанию дл€ проксировани€ HTTP трафика.';
    4445: result := 'I2P ѕо умолчанию дл€ проксировани€ HTTPS трафика.';
    4662: result := 'OrbitNet Message Service'#13#10'often used by eMule';
    4664: result := 'Google Desktop Search';
    4747: result := 'Apprentice';
    4750: result := 'BladeLogic Agent';
    4894: result := 'LysKOM Protocol A';
    4899: result := 'RAdminЧпрограмма дл€ удаленного управлени€';
    4900: result := 'KommuteЧфайлообменный клиент';
    5000: result := 'UPnPЧWindows network device interoperability'#13#10'VTunЧVPN Software';
    5001: result := 'Iperf (Tool for measuring TCP and UDP bandwidth performance)'#13#10'Slingbox and Slingplayer';
    5003: result := 'FileMaker';
    5004: result := 'RTP (Real-time Transport Protocol) media data';
    5005: result := 'RTP (Real-time Transport Protocol) control protocol';
    5031: result := 'AVM CAPI-over-TCP (ISDN over Ethernet tunneling)';
    5050: result := 'Yahoo! Messenger'#13#10'NatICQ getway (шлюз между пользователем клиента NatICQ и системой мгновенных сообщений ICQ)';
    5051: result := 'ita-agent Symantec Intruder Alert';
    5060: result := 'Session Initiation Protocol (SIP)';
    5061: result := 'Session Initiation Protocol (SIP) over TLS';
    5104: result := 'IBM Tivoli Framework NetCOOL/Impact HTTP Service';
    5106: result := 'A-Talk Common connection';
    5107: result := 'A-Talk Remote server connection';
    5110: result := 'ProRat Server';
    5121: result := 'Neverwinter Nights';
    5154: result := 'BZFlag';
    5176: result := 'ConsoleWorks default UI interface';
    5190: result := 'ICQ и AOL Instant Messenger';
    5222: result := 'Extensible Messaging and Presence Protocol (XMPP, Jabber) client connection';
    5223: result := 'Extensible Messaging and Presence Protocol (XMPP, Jabber) client connection over SSL';
    5269: result := 'Extensible Messaging and Presence Protocol (XMPP, Jabber) server connection';
    5298: result := 'Extensible Messaging and Presence Protocol (XMPP) link-local messaging';
    5351: result := 'NAT Port Mapping ProtocolЧclient-requested configuration for inbound connections through network address translators';
    5355: result := 'LLMNRЧLink-Local Multicast Name Resolution';
    5402: result := 'mftp, Stratacache OmniCast content delivery system MFTP file sharing protocol';
    5405: result := 'NetSupport';
    5421: result := 'NetSupport 2';
    5432: result := 'PostgreSQL';
    5495: result := 'Applix TM1 Admin server';
    5498: result := 'Hotline tracker server connection';
    5500: result := 'VNC remote desktop protocolЧfor incoming listening viewer, Hotline control connection';
    5501: result := 'Hotline file transfer connection';
    5517: result := 'Setiqueue Proxy server client for SETI@Home project';
    5555: result := 'Freeciv versions up to 2.0, Hewlett Packard Data Protector, SAP';
    5556: result := 'Freeciv';
    5631: result := 'pcANYWHEREdata, Symantec pcAnywhere (version 7.52 and later) data';
    5666: result := 'NRPE (Nagios)';
    5667: result := 'NSCA (Nagios)';
    5800: result := 'VNC remote desktop protocolЧfor use over HTTP';
    5814: result := 'Hewlett-Packard Support Automation (HP OpenView Self-Healing Services)';
    5900: result := 'Virtual Network Computing (VNC) remote desktop protocol (used by Apple Remote Desktop and others)';
    5938: result := 'TeamViewer remote desktop protocol';
    5984: result := 'CouchDB database server';
    6000: result := 'X11Чused between an X client and server over the network';
    6005: result := 'Default for BMC Software CONTROL-M/ServerЧSocket';
    6014: result := 'Autodesk license daemon';
    6050: result := 'Brightstor Arcserve Backup';
    6051: result := 'Brightstor Arcserve Backup';
    6086: result := 'PDTPЧFTP like file server in a P2P network';
    6100: result := 'Vizrt System';
    6110: result := 'softcm, HP Softbench CM';
    6111: result := 'spc, HP Softbench Sub-Process Control';
    6112: result := 'ЂdtspcdїЧa network daemon that accepts requests from clients to execute commands and launch applications remotely'#13#10'Blizzard''s Battle.net gaming service, ArenaNet gaming service';
    6113..6119: result := 'World of Warcraft MMORPG Realmservers';
    6129: result := 'Dameware Remote Control';
    6346: result := 'gnutella-svc, Gnutella (FrostWire, Limewire, Shareaza, etc.)';
    6347: result := 'gnutella-rtr, Gnutella alternate';
    6379: result := 'Redis Ч сетевое журналируемое хранилище данных типа Ђключ-значениеї с открытым исходным кодом.';
    6444: result := 'Sun Grid EngineЧQmaster Service';
    6445: result := 'Sun Grid EngineЧExecution Service';
    6502: result := 'Danware Data NetOp Remote Control';
    6514: result := 'ѕротокол Syslog Ч доставка сообщений о происход€щих в системе событи€х с использованием механизмов TLS/DTLS';
    6522: result := 'Gobby (and other libobby-based software)';
    6566: result := 'SANE (Scanner Access Now Easy)†Ч SANE network scanner daemon';
    6600: result := 'Music Player Daemon (MPD)';
    6619: result := 'odette-ftps, Odette File Transfer Protocol (OFTP) over TLS/SSL';
    6668: result := 'I2P ѕо умолчанию дл€ проксировани€ IRC трафика.';
    6665..6667,6669: result := 'IRC';
    6679: result := 'IRC SSL (Secure Internet Relay Chat)†Ч often used';
    6697: result := 'IRC SSL (Secure Internet Relay Chat)†Ч often used';
    6699: result := 'WinMX';
    6881..6887: result := 'BitTorrent part of full range of ports used most often';
    6888: result := 'MUSE'#13#10'BitTorrent part of full range of ports used most often';
    6889..6890: result := 'BitTorrent part of full range of ports used most often';
    6891..6900: result := 'BitTorrent part of full range of ports used most often'#13#10'Windows Live Messenger (File transfer)';
    6901: result := 'Windows Live Messenger (Voice)'#13#10'BitTorrent part of full range of ports used most often';
    6902..6968: result := 'BitTorrent part of full range of ports used most often';
    6969: result := 'acmsoda'#13#10'BitTorrent tracker';
    6970..6999: result := 'BitTorrent part of full range of ports used most often';
    7000: result := 'Default for Azureus''s built in HTTPS Bittorrent Tracker';
    7001: result := 'Default for BEA WebLogic Server''s HTTP server';
    7002: result := 'Default for BEA WebLogic Server''s HTTPS server';
    7005: result := 'Default for BMC Software CONTROL-M/Server and CONTROL-M/AgentЧAgent-to-Server';
    7006: result := 'Default for BMC Software CONTROL-M/Server and CONTROL-M/AgentЧServer-to-Agent';
    7010: result := 'Default for Cisco AON AMC (AON Management Console)';
    7025: result := 'Zimbra LMTP [mailbox]†Ч local mail delivery';
    7047: result := 'Zimbra conversion server';
    7071: result := 'Zimbra Administration Console';
    7133: result := 'Enemy Territory: Quake Wars';
    7171: result := 'Tibia';
    7306: result := 'Zimbra mysql [mailbox]';
    7307: result := 'Zimbra mysql [logger]';
    7657: result := 'I2P ѕо умолчанию веб-консоль управлени€ роутером i2p';
    7659: result := 'I2P ѕо умолчанию дл€ проксировани€ SMTP трафика';
    7660: result := 'I2P ѕо умолчанию дл€ проксировани€ POP3 трафика';
    7670: result := 'BrettspielWelt BSW Boardgame Portal';
    7777: result := 'Default used by Windows backdoor program tini.exe'#13#10'ѕорт сервера SAMP';
    7831: result := 'Default used by Smartlaunch Internet Cafe Administration software';
    8000: result := 'Commonly used for internet radio streams such as those using IceCast'#13#10'Commonly used for internet radio streams such as those using SHOUTcast';
    8002: result := 'Cisco Systems Unified Call Manager Intercluster';
    8008: result := 'HTTP Alternate'#13#10'IBM HTTP Server administration default';
    8010: result := 'XMPP/Jabber File transfers';
    8074: result := 'Gadu-Gadu';
    8080: result := 'HTTP alternate (http_alt)Чcommonly used for Web proxy and caching server'#13#10'Apache Tomcat';
    8086: result := 'HELM Web Host Automation Windows Control Panel'#13#10'Kaspersky AV Control Center';
    8087: result := 'Hosting Accelerator Control Panel'#13#10'SW Soft Plesk Control Panel';
    8090: result := 'Another HTTP Alternate (http_alt_alt)Чused as an alternative to port 8080';
    8118: result := 'PrivoxyЧadvertisement-filtering Web proxy';
    8172: result := '—лужба веб-управлени€ IIS';
    8200: result := 'GoToMyPC';
    8220: result := 'Bloomberg';
    8222: result := 'VMware Server Management User Interface (insecure Web interface)';
    8291: result := 'WinboxЧDefault on a MikroTik RouterOS for a Windows application used to administer MikroTik RouterOS';
    8294: result := 'Bloomberg';
    8333: result := 'VMware Server Management User Interface (secure Web interface)';
    8400: result := 'cvp, Commvault Unified Data Management';
    8443: result := 'Parallels Plesk Panel';
    8500: result := 'ColdFusion Macromedia/Adobe ColdFusion default';
    8585: result := 'Tensor GDPЧdefault';
    8840: result := 'Opera Unite по умолчанию';
    8880: result := 'cddbp-alt, CD DataBase (CDDB) protocol (CDDBP) alternate'#13#10'WebSphere Application Server SOAP connector default';
    8881: result := 'Atlasz Informatics Research Ltd Secure Application Server';
    8882: result := 'Atlasz Informatics Research Ltd Secure Application Server';
    8888: result := 'GNUmp3d HTTP music streaming and Web interface'#13#10'LoLo Catcher HTTP Web interface (www.optiform.com)';
    9000: result := 'Buffalo LinkSystem Web access'#13#10'DBGp';
    9001: result := 'Tor network default'#13#10'DBGp Proxy';
    9009: result := 'Pichat ServerЧPeer to peer chat software';
    9043: result := 'WebSphere Application Server Administration Console secure';
    9060: result := 'WebSphere Application Server Administration Console';
    9080: result := 'glrpc, Groove Collaboration software GLRPC'#13#10'WebSphere Application Server Http Transport (port 1) default';
    9090: result := 'Openfire Administration Console';
    9100: result := 'JetDirect HP Print Services';
    9101: result := 'Bacula Director';
    9102: result := 'Bacula File Daemon';
    9103: result := 'Bacula Storage Daemon';
    9119: result := 'MXit Instant Messenger';
    9418: result := 'git, Git pack transfer service';
    9535: result := 'mngsuite, LANDesk Management Suite Remote Control'#13#10'BBOS001, IBM Websphere Application Server (WAS) High Avail Mgr Com';
    9443: result := 'WebSphere Application Server Http Transport (port 2) default';
    9800: result := 'WebDAV Source'#13#10'WebCT e-learning portal';
    9999: result := 'Lantronix UDS-10/UDS100 RS-485 to Ethernet Converter TELNET control'#13#10'Urchin Web Analytics';
    10000: result := 'WebminЧWeb-based Linux admin tool'#13#10'BackupExec';
    10001: result := 'Lantronix UDS-10/UDS100 RS-485 to Ethernet Converter default';
    10008: result := 'Octopus Multiplexer, primary port for the CROMP protocol';
    10017: result := 'AIX,NeXT, HPUXЧrexd daemon control';
    10024: result := 'Zimbra smtp [mta]Чto amavis from postfix';
    10025: result := 'Ximbra smtp [mta]Чback to postfix from amavis';
    10050: result := 'Zabbix-Agent';
    10051: result := 'Zabbix-Trapper';
    10113: result := 'NetIQ Endpoint';
    10114: result := 'NetIQ Qcheck';
    10115: result := 'NetIQEndpoint';
    10116: result := 'NetIQ VoIP Assessor';
    10200..10204: result := 'FRISK Software InternationalТs f-protd virus scanning daemon for Unix platforms';
    10308: result := 'Digital Combat Simulator';
    10480: result := 'SWAT 4 Dedicated Server';
    11211: result := 'memcached';
    11235: result := 'Savage:Battle for Newerth Server Hosting';
    11294: result := 'Blood Quest Online Server';
    11371: result := 'OpenPGP HTTP Keyserver';
    11576: result := 'IPStor Server management communication';
    12345: result := 'NetBusЧremote administration tool (often Trojan horse)';
    12975: result := 'LogMeIn Hamachi (VPN tunnel software)';
    13720: result := 'Symantec NetBackup†Ч bprd (formerly VERITAS)';
    13721: result := 'Symantec NetBackup†Ч bpdbm (formerly VERITAS)';
    13724: result := 'Symantec Network Utility†Ч vnetd (formerly VERITAS)';
    13782: result := 'Symantec NetBackup†Ч bpcd (formerly VERITAS)';
    13783: result := 'Symantec VOPIED protocol (formerly VERITAS)';
    13785: result := 'Symantec NetBackup Database†Ч nbdb (formerly VERITAS)';
    13786: result := 'Symantec nomdb (formerly VERITAS)';
    14147: result := 'FileZilla Server admin interface';
    15000: result := 'Wesnoth'#13#10'hydap, Hypack Hydrographic Software Packages Data Acquisition';
    15345: result := 'XPilot Contact';
    15779: result := 'Joymax Co. Ltd.''s Silkroad Online''s launcher server port';
    15780: result := 'Joymax Co. Ltd.''s Silkroad Online''s Game authentication port';
    15881: result := 'Joymax Co. Ltd.''s Silkroad Online''s update download port';
    15883..15884: result := 'Joymax Co. Ltd.''s Silkroad Online''s game world port';
    16000: result := 'shroudBNC';
    16080: result := 'Mac OS X Server Web (HTTP) service with performance cache';
    18181: result := 'Content Vectoring Protocol (OPSEC CVP)';
    18158: result := 'Trend Micro OfficeScan';
    18390: result := 'Battlefield: Bad Company 2';
    19226: result := 'Panda Software AdminSecure Communication Agent';
    19638: result := 'Ensim Control Panel';
    19813: result := '4D database Client Server Communication';
    20000: result := 'DNP (Distributed Network Protocol), a protocol used in SCADA systems between communicating RTU''s and IED''s'#13#10'Usermin, Web-based user tool';
    20720: result := 'Symantec i3 Web GUI server';
    22004: result := 'MTA Deathmatch';
    22347: result := 'WibuKey, WIBU-SYSTEMS AG Software protection system';
    22350: result := 'CodeMeter, WIBU-SYSTEMS AG Software protection system';
    24554: result := 'BINKP, Fidonet mail transfers over TCP/IP';
    24800: result := 'Synergy: keyboard/mouse sharing software';
    24842: result := 'StepMania: Online: Dance Dance Revolution Simulator';
    25565: result := 'Minecraft';
    25666: result := 'Doom 2D Multiplayer';
    25667: result := 'ћастерсервер Doom 2D Multiplayer';
    25999: result := 'Xfire';
    26000: result := 'id Software''s Quake server'#13#10'CCP''s EVE Online Online gaming MMORPG';
    27000..27009: result := 'Autodesk license daemon';
    27017: result := 'MongoDB default.';
    27018: result := 'Steam';
    27374: result := 'Sub7 default. Most script kiddies do not change from this.';
    27900: result := '(through 27901) Nintendo Wi-Fi Connection';
    28910: result := 'Nintendo Wi-Fi Connection';
    28960: result := 'Call of Duty 2 Common Call of Duty 2 (PC Version)';
    28961: result := 'Call of Duty 4: Modern Warfare Common Call of Duty 4 (PC Version)';
    29000: result := 'Perfect world online gaming mmorpg';
    29900: result := 'Nintendo Wi-Fi Connection';
    29920: result := 'Nintendo Wi-Fi Connection';
    30000: result := 'Pokemon Netbattle';
    30564: result := 'Multiplicity: keyboard/mouse/clipboard sharing software';
    31337: result := 'Back Orifice†Ч средство дл€ удаленного администрировани€ (часто тро€нска€ программа)'#13#10'xc0r3 security';
    31415: result := 'ThoughtSignalЧServer Communication Service (often Informational)';
    31456..31458: result := 'TetriNET (in order: IRC, game, and spectating)';
    32245: result := 'MMTSG-mutualed через MMT (зашифрованна€ передача)';
    32976: result := 'LogMeIn Hamachi (программа создани€ VPN соединени€)';
    33434: result := 'traceroute';
    34443: result := 'Linksys PSUS4 print server';
    37777: result := 'Digital Video Recorder hardware';
    36963: result := 'Counter-Strike 2D multiplayer (2D-клон попул€рной игры CounterStrike)';
    37904: result := 'LG TV';
    40000: result := 'SafetyNET p Real-time Industrial Ethernet protocol';
    43594..43595: result := 'RuneScape';
    47808: result := 'BACnet Building Automation and Control Networks';
    49000: result := 'MATAHARI';
    else result := '';
  end;
end;

end.
