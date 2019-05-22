unit selimage;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms, Dialogs, StdCtrls, Buttons, MemTableDataEh,
  Db, MemTableEh, ComCtrls, ImgList, IniFiles, utils, JvExStdCtrls, JvListComb, ExtCtrls, imgUtils, Math;

type
  TFSelImage = class(TForm)
    Panel1: TPanel;
    btnSave: TBitBtn;
    btnCancel: TBitBtn;
    tcImages: TTabControl;
    lbImages: TJvImageListBox;
    OpenDialog: TOpenDialog;
    btnAddGroup: TButton;
    btnRenameGroup: TButton;
    btnDelGroup: TButton;
    btnClearGroup: TButton;
    Bevel1: TBevel;
    btnAddPic: TButton;
    btnRenamePic: TButton;
    btnDelPic: TButton;
    procedure FormCreate(Sender: TObject);
    procedure tcImagesChange(Sender: TObject);
    procedure btnAddGroupClick(Sender: TObject);
    procedure btnRenameGroupClick(Sender: TObject);
    procedure btnDelGroupClick(Sender: TObject);
    procedure btnClearGroupClick(Sender: TObject);
    procedure btnAddPicClick(Sender: TObject);
    procedure btnRenamePicClick(Sender: TObject);
    procedure btnDelPicClick(Sender: TObject);
  private
    procedure LoadImages(GroupIndex: integer);
    procedure CreatePages;
    //--
    procedure AddGroup;
    procedure RenameGroup;
    procedure DeleteGroup;
    procedure ClearGroup;
    //--
    procedure AddPic;
    procedure RenamePic;
    procedure DeletePic;
    //--
    function IndexOfPicName(Name: string): integer;
    function ConvertImage(Source, Dest: string; Proportional: boolean; var Err: string): boolean;
  public
    function Selected: string;
  end;

implementation

{$R *.dfm}

uses settings;

{ TFSelImage }

procedure TFSelImage.AddGroup;
var
  g: string;

begin
  g := Trim(InputBox('Новая группа', 'Введите имя новой группы', ''));
  if (g = '') then exit;

  if tcImages.Tabs.IndexOf(g) > -1 then
  begin
    Application.MessageBox(pchar('Группа "' + g + '" уже есть!'), 'Ошибка', MB_OK + MB_ICONERROR);
    exit;
  end;

  tcImages.Tabs.Add(g);
  tcImages.TabIndex := tcImages.Tabs.Count - 1;
  LoadImages(tcImages.TabIndex);

  if not WriteIniValue(FSettings.DataDir + RES_CONFIG_FILE, RCFG_SEC_GROUP, IntToStr(tcImages.TabIndex), g) then
  begin
    tcImages.Tabs.Delete(tcImages.TabIndex);
    Application.MessageBox('Не удалось создать группу! При сохранении группы произошла ошибка.', 'Ошибка', MB_OK + MB_ICONERROR);
  end;
end;

procedure TFSelImage.AddPic;
var
  newName, s, err: string;
  r: boolean;

begin
  if tcImages.TabIndex < 0 then exit;

  if OpenDialog.Execute then
  begin
    s := ChangeFileExt(ExtractFileName(OpenDialog.FileName), '');
    newName := Trim(InputBox('Добавление картинки', 'Введите имя картинки', s));
    if (newName = '') then newName := s;
    newName := newName + '.bmp';

    if IniKeyExists(FSettings.DataDir + RES_CONFIG_FILE, RCFG_SEC_FACE, newName, 0) then
    begin
      if (Application.MessageBox(pchar('Картинка "' + newName + '" уже есть в библиотеке! Хотите заменить ее и перенести в ' +
        'текущую группу?'), 'Подтверждение', MB_YESNO + MB_ICONQUESTION) <> ID_YES) then exit;
    end;

    newName := FSettings.DataDir + USER_DATA_DIR + newName;
    if AnsiLowerCase(newName) <> AnsiLowerCase(OpenDialog.FileName) then
    begin
      if DefineImgType(ExtractFileExt(OpenDialog.FileName)) = itBitmap then
        r := CopyFile(OpenDialog.FileName, newName, err)
      else
        r := ConvertImage(OpenDialog.FileName, newName, true, err);

      if not r then
      begin
        Application.MessageBox(pchar('Не удалось перенести файл с изображением в папку данных игры. ' +
          'Изображение не добавлено! Ошибка'#13#10 + err), 'Ошибка', MB_OK + MB_ICONERROR);
        exit;
      end;
    end;

    if not WriteIniValue(FSettings.DataDir + RES_CONFIG_FILE, RCFG_SEC_FACE, ExtractFileName(newName),
      IntToStr(tcImages.TabIndex)) then
      Application.MessageBox('Не удалось добавить картинку! При сохранении конфигурации произошла ошибка.', 'Ошибка', MB_OK + MB_ICONERROR);

    LoadImages(tcImages.TabIndex);
    lbImages.ItemIndex := lbImages.Items.Count - 1;
  end;
end;

procedure TFSelImage.btnAddGroupClick(Sender: TObject);
begin
  AddGroup;
end;

procedure TFSelImage.btnAddPicClick(Sender: TObject);
begin
  AddPic;
end;

procedure TFSelImage.btnClearGroupClick(Sender: TObject);
begin
  ClearGroup;
end;

procedure TFSelImage.btnDelGroupClick(Sender: TObject);
begin
  DeleteGroup;
end;

procedure TFSelImage.btnDelPicClick(Sender: TObject);
begin
  DeletePic;
end;

procedure TFSelImage.btnRenameGroupClick(Sender: TObject);
begin
  RenameGroup;
end;

procedure TFSelImage.btnRenamePicClick(Sender: TObject);
begin
  RenamePic;
end;

procedure TFSelImage.ClearGroup;
var
  i, t, idx: integer;
  f: TIniFile;
  sl: TStringList;

begin
  if tcImages.TabIndex < 0 then exit;

  if (Application.MessageBox(pchar('Очистить группу "' + tcImages.Tabs[tcImages.TabIndex] + '"? Все картинки этой группы будут удалены!'),
    'Подтверждение', MB_YESNO + MB_ICONQUESTION) <> ID_YES) then exit;

  f := TIniFile.Create(FSettings.DataDir + RES_CONFIG_FILE);
  try
    sl := TStringList.Create;
    f.ReadSectionValues(RCFG_SEC_FACE, sl);

    t := tcImages.TabIndex;
    for i := 0 to sl.Count - 1 do
    begin
      idx := StrToInt(sl.Values[sl.Names[i]]);
      if idx = t then
      begin
        f.DeleteKey(RCFG_SEC_FACE, sl.Names[i]);
        DeleteFile(FSettings.DataDir + USER_DATA_DIR + sl.Names[i]);
      end;
    end;

    LoadImages(t);
  finally
    sl.Free;
    f.Free;
  end;
end;

function TFSelImage.ConvertImage(Source, Dest: string; Proportional: boolean; var Err: string): boolean;
var
  b: TBitmap;
  nw, nh: integer;
  c: double;

begin
  result := false;
  Err := '';
  nw := 128;
  nh := 128;

  try
    b := LoadPicture(Source);

    if (b.Width <> nw) or (b.Height <> nh) then
    begin
      if Proportional then
      begin
        if b.Width > b.Height then
        begin
          c := b.Width / b.Height;
          nh := Round(nh / c);
        end else
        if b.Width < b.Height then
        begin
          c := b.Height / b.Width;
          nw := Round(nw / c);
        end;
      end;

      DecreaseBitmap(b, nw, nh);
    end;

    b.SaveToFile(Dest);
    result := true;
  except
    on e: Exception do Err := e.Message;
  end;
end;

procedure TFSelImage.CreatePages;
var
  f: TIniFile;
  sl: TStringList;
  i: integer;

begin
  f := TIniFile.Create(FSettings.DataDir + RES_CONFIG_FILE);
  try
    sl := TStringList.Create;
    tcImages.Tabs.Clear;

    f.ReadSection(RCFG_SEC_GROUP, sl);
    for i := 0 to sl.Count - 1 do
      tcImages.Tabs.Add(f.ReadString(RCFG_SEC_GROUP, sl.Strings[i], ''));
  finally
    sl.Free;
    f.Free;
  end;
end;

procedure TFSelImage.DeleteGroup;
var
  i, t, idx: integer;
  f: TIniFile;
  sl: TStringList;

begin
  if tcImages.TabIndex < 0 then exit;

  if (Application.MessageBox(pchar('Удалить группу "' + tcImages.Tabs[tcImages.TabIndex] + '"? Все картинки этой группы также будут удалены!'),
    'Подтверждение', MB_YESNO + MB_ICONQUESTION) <> ID_YES) then exit;

  f := TIniFile.Create(FSettings.DataDir + RES_CONFIG_FILE);
  try
    sl := TStringList.Create;
    t := tcImages.TabIndex;
    
    f.ReadSectionValues(RCFG_SEC_FACE, sl);
    f.EraseSection(RCFG_SEC_FACE);
    f.EraseSection(RCFG_SEC_GROUP);
    
    tcImages.Tabs.Delete(t);
    for i := 0 to tcImages.Tabs.Count - 1 do
      f.WriteString(RCFG_SEC_GROUP, IntToStr(i), tcImages.Tabs[i]);

    for i := 0 to sl.Count - 1 do
    begin
      idx := StrToInt(sl.Values[sl.Names[i]]);
      if idx <> t then
      begin
        if idx > t then Inc(idx, -1);
        f.WriteString(RCFG_SEC_FACE, sl.Names[i], IntToStr(idx));
      end else
        DeleteFile(FSettings.DataDir + USER_DATA_DIR + sl.Names[i]);
    end;

    if t > 0 then tcImages.TabIndex := t - 1
    else tcImages.TabIndex := t;
    LoadImages(tcImages.TabIndex);
  finally
    sl.Free;
    f.Free;
  end;
end;

procedure TFSelImage.DeletePic;
var
  i: integer;

begin
  if lbImages.ItemIndex < 0 then exit;

  if (Application.MessageBox(pchar('Удалить картинку "' + lbImages.Items.Items[lbImages.ItemIndex].Text + '"?!'),
    'Подтверждение', MB_YESNO + MB_ICONQUESTION) <> ID_YES) then exit;

  DeleteFile(FSettings.DataDir + USER_DATA_DIR + lbImages.Items.Items[lbImages.ItemIndex].Text);

  if not DeleteIniKey(FSettings.DataDir + RES_CONFIG_FILE, RCFG_SEC_FACE, lbImages.Items.Items[lbImages.ItemIndex].Text) then
    Application.MessageBox(pchar('Картинка удалена с ошибками! Не удалось сохранить конфигурацию.'), 'Ошибка', MB_OK + MB_ICONERROR);

  i := lbImages.ItemIndex;
  LoadImages(tcImages.TabIndex);
  if i < lbImages.Items.Count then lbImages.ItemIndex := i
  else lbImages.ItemIndex := lbImages.Items.Count - 1;
end;

procedure TFSelImage.FormCreate(Sender: TObject);
begin
  CreatePages;
  LoadImages(tcImages.TabIndex);
  if lbImages.Items.Count > 0 then lbImages.ItemIndex := 0;
end;

function TFSelImage.IndexOfPicName(Name: string): integer;
var
  i: integer;

begin
  result := -1;

  for i := 0 to lbImages.Items.Count - 1 do
    if AnsiLowerCase(lbImages.Items.Items[i].Text) = AnsiLowerCase(Name) then
    begin
      result := i;
      break;
    end;
end;

procedure TFSelImage.LoadImages(GroupIndex: integer);
var
  i: integer;
  f: TIniFile;
  sl: TStringList;
  fn: string;
  item: TJvImageItem;

begin
  lbImages.Items.Clear;

  f := TIniFile.Create(FSettings.DataDir + RES_CONFIG_FILE);
  try
    sl := TStringList.Create;

    f.ReadSectionValues(RCFG_SEC_FACE, sl);
    for i := 0 to sl.Count - 1 do
      if StrToInt(sl.Values[sl.Names[i]]) = GroupIndex then
      begin
        fn := sl.Names[i];
        item := lbImages.Items.Add;
        item.Text := fn;
        try
          item.Glyph.LoadFromFile(FSettings.DataDir + USER_DATA_DIR + fn);
          item.Glyph.SetSize(128, 128);
        except
          on e: Exception do
            Application.MessageBox(pchar('Не удалось загрузить картинку "' + fn + '"!'#13#10 + e.Message), 'Ошибка', MB_OK + MB_ICONERROR);
        end;
      end;
  finally
    sl.Free;
    f.Free;
  end;
end;

procedure TFSelImage.RenameGroup;
var
  g, old: string;
  i: integer;

begin
  if tcImages.TabIndex < 0 then exit;
  
  i := tcImages.TabIndex;
  old := tcImages.Tabs[i];
  
  g := Trim(InputBox('Переименовать группу', 'Введите новое имя группы', tcImages.Tabs[i]));
  if (g = '') or (g = tcImages.Tabs[i]) then exit;
  if (tcImages.Tabs.IndexOf(g) > -1) and (AnsiLowerCase(g) <> AnsiLowerCase(tcImages.Tabs[i])) then
  begin
    Application.MessageBox(pchar('Группа "' + g + '" уже есть!'), 'Ошибка', MB_OK + MB_ICONERROR);
    exit;
  end;

  tcImages.Tabs[i] := g;
  tcImages.TabIndex := i;

  if not WriteIniValue(FSettings.DataDir + RES_CONFIG_FILE, RCFG_SEC_GROUP, IntToStr(tcImages.TabIndex), g) then
  begin
    tcImages.Tabs[i] := old;
    tcImages.TabIndex := i;
    Application.MessageBox('Не удалось переименовать группу! При сохранении группы произошла ошибка.', 'Ошибка', MB_OK + MB_ICONERROR);
  end;
end;

procedure TFSelImage.RenamePic;
var
  newName: string;
  i: integer;

begin
  if lbImages.ItemIndex < 0 then exit;

  newName := Trim(InputBox('Переименование картинки', 'Введите новое имя картинки',
    ChangeFileExt(lbImages.Items.Items[lbImages.ItemIndex].Text, '')));
  if (newName = '') then exit;
  newName := newName + ExtractFileExt(lbImages.Items.Items[lbImages.ItemIndex].Text);
  if newName = lbImages.Items.Items[lbImages.ItemIndex].Text then exit;

  if IniKeyExists(FSettings.DataDir + RES_CONFIG_FILE, RCFG_SEC_FACE, newName, 0) then
  begin
    Application.MessageBox(pchar('Картинка "' + newName + '" уже есть в библиотеке!'), 'Ошибка', MB_OK + MB_ICONERROR);
    exit;
  end;

  if not RenameFile(FSettings.DataDir + USER_DATA_DIR + lbImages.Items.Items[lbImages.ItemIndex].Text,
    FSettings.DataDir + USER_DATA_DIR + newName) then
  begin
    Application.MessageBox(pchar('Не удалось переименовать картинку!'#13#10 + SysErrorMessage(GetLastError)), 'Ошибка',
      MB_OK + MB_ICONERROR);
    exit;
  end;

  if not DeleteIniKey(FSettings.DataDir + RES_CONFIG_FILE, RCFG_SEC_FACE, lbImages.Items.Items[lbImages.ItemIndex].Text) then
    Application.MessageBox('Ошибка переименования картинки! При сохранении конфигурации произошла ошибка.', 'Ошибка',
      MB_OK + MB_ICONERROR);

  if not WriteIniValue(FSettings.DataDir + RES_CONFIG_FILE, RCFG_SEC_FACE, newName, IntToStr(tcImages.TabIndex)) then
    Application.MessageBox('Ошибка переименования картинки! При сохранении конфигурации произошла ошибка.', 'Ошибка',
      MB_OK + MB_ICONERROR);

  i := lbImages.ItemIndex;
  LoadImages(tcImages.TabIndex);
  lbImages.ItemIndex := i;
end;

function TFSelImage.Selected: string;
begin
  result := lbImages.Items.Items[lbImages.ItemIndex].Text;
end;

procedure TFSelImage.tcImagesChange(Sender: TObject);
begin
  LoadImages(tcImages.TabIndex);
  if lbImages.Items.Count > 0 then lbImages.ItemIndex := 0;
  lbImages.SetFocus;
end;

end.
